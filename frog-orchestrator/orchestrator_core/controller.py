'''
@author: fabiomignini
'''

from __future__ import division

import json
import logging
from scheduler import Scheduler
import uuid

from vnf_template_library.template import Template
from vnf_template_library.validator import ValidateTemplate
from orchestrator_core.exception import sessionNotFound, GraphError
from orchestrator_core.nffg_manager import NFFG_Manager
from orchestrator_core.sql.session import Session
from orchestrator_core.sql.graph import Graph
from orchestrator_core.sql.image import Images
from orchestrator_core.sql.node import Node 
from orchestrator_core.userAuthentication import UserData
from nffg_library.nffg import NF_FG
from orchestrator_core.config import Configuration

DEBUG_MODE = Configuration().DEBUG_MODE


class UpperLayerOrchestratorController(object):
    '''
        Class that performs the logic of orchestrator_core
    '''
    def __init__(self, user_data):
        self.user_data = user_data

    def get(self, nffg_id):
        session = Session().get_active_user_session_by_nf_fg_id(nffg_id, error_aware=False)
        logging.debug("Getting session: "+str(session.id))
        graphs_ref = Graph().getGraphs(session.id)
        instantiated_nffgs = []
        for graph_ref in graphs_ref:
            instantiated_nffgs.append(Graph().get_nffg(graph_ref.id))
        
        if not instantiated_nffgs:
            return None
        # TODO: If the graph has been split, we need to rebuild the origina nffg
        return instantiated_nffgs[0].getJSON()
    
    def delete(self, nffg_id):        
        # Get the component adapter associated  to the node where the nffg was instantiated
        session = Session().get_active_user_session_by_nf_fg_id(nffg_id, error_aware=False)
        logging.debug("Deleting session: "+str(session.id))

        graphs_ref = Graph().getGraphs(session.id)
        for graph_ref in graphs_ref:
            node = Node().getNode(Graph().getNodeID(graph_ref.id))
            
            # Get instantiated nffg
            instantiated_nffg = Graph().get_nffg(graph_ref.id)
            logging.debug('NF-FG that we are going to delete: '+instantiated_nffg.getJSON())
            
            # Check external connections, if a graph is connected to this, the deletion will be cancelled
            if self.checkExternalConnections(instantiated_nffg):
                raise Exception("This graph has been connected with other graph, delete these graph before to delete this.")
            
            # Analyze end-point connections
            remote_nffgs_dict = self.analizeRemoteConnection(instantiated_nffg, node, delete=True)
            
            # If needed, update the remote graph
            self.updateRemoteGraph(remote_nffgs_dict)
            
            # De-instantiate profile
            orchestrator = Scheduler(graph_ref.id, self.user_data).getInstance(node)
            
            try:
                orchestrator.deinstantiateProfile(instantiated_nffg, node)
            except Exception as ex:
                logging.exception(ex)
                Session().set_error(session.id)
                raise ex
            
        logging.debug('Session deleted: '+str(session.id))
        # Set the field ended in the table session to the actual datatime        
        Graph().delete_session(session.id)
        Session().set_ended(session.id)
    
    def update(self, nffg, delete = False):        
        session = Session().get_active_user_session_by_nf_fg_id(nffg.id, error_aware=True)
        Session().updateStatus(session.id, 'updating')
        
        # Get profile from session
        graphs_ref = Graph().getGraphs(session.id)
        if len(graphs_ref) > 1:
            # If the graph has been split, the smart update is not supported
            logging.warning("The graph has been split in various nffg, in this case the smart update is not supported.")
            self.delete(nffg.id)
        else:
            
            old_nffg = Graph().get_nffg(graphs_ref[0].id)
            logging.debug('NF-FG that has to be updated: '+old_nffg.getJSON())
            nffg.db_id = old_nffg.db_id
            
            # Get VNFs templates
            self.prepareNFFG(nffg)
    
            # Get the component adapter associated  to the node where the nffg was instantiated
            old_node = Node().getNode(Graph().getNodeID(graphs_ref[0].id))
            scheduler = Scheduler(old_nffg.db_id, self.user_data)
            orchestrator, new_node = scheduler.schedule(nffg)
            
            # If the orchestrator have to connect two graphs in different nodes,
            # the end-points must be characterized to allow a connection between nodes
            remote_nffgs_dict = self.analizeRemoteConnection(nffg, new_node)
            
            # If needed, update the remote graph
            self.updateRemoteGraph(remote_nffgs_dict)
            
            if new_node.id != old_node.id:
                logging.warning("The graph will be instantiated in a different node, in this case the smart update is not supported.")
                orchestrator.deinstantiateProfile(nffg, old_node)
                Graph().delete_session(session.id)
                Graph().addNFFG(nffg, session.id)
                Graph().setNodeID(graphs_ref[0].id, Node().getNodeFromDomainID(new_node.domain_id).id)
                try:
                    orchestrator.instantiateProfile(nffg, new_node)
                except Exception as ex:
                    logging.exception(ex)
                    Session().set_error(session.id)          
                    raise ex
            else:
                # Update the nffg
                try:
                    orchestrator.updateProfile(nffg, old_nffg, new_node)
                except Exception as ex:
                    logging.exception(ex)
                    Session().set_error(session.id)
                    raise ex
        
        Session().updateStatus(session.id, 'complete')
        Session().updateSessionNode(session.id, new_node.id, new_node.id)
        return session.id
        
    def put(self, nffg):
        """
        Manage the request of NF-FG instantiation
        """
        logging.debug('Put from user '+self.user_data.username+" of tenant "+self.user_data.tenant)
        if self.checkNFFGStatus(nffg.id) is True:
            logging.debug('NF-FG already instantiated, trying to update it')
            session_id = self.update(nffg)
            logging.debug('Update completed')
        else:
            session_id  = uuid.uuid4().hex
            Session().inizializeSession(session_id, self.user_data.getUserID(), nffg.id, nffg.name)
            try:
                # Manage profile
                self.prepareNFFG(nffg)
                 
                
                # TODO: To split the graph we have to loop the following three instructions
                # Take a decision about where we should schedule the serving graph (UN or HEAT), and the node
                Graph().id_generator(nffg, session_id)
                orchestrator, node = Scheduler(nffg.db_id, self.user_data).schedule(nffg)
                
                # If the orchestrator have to connect two graphs in different nodes,
                # the end-points must be characterized to allow a connection between nodes
                remote_nffgs_dict = self.analizeRemoteConnection(nffg, node)
                
                # If needed, update the remote graph
                self.updateRemoteGraph(remote_nffgs_dict)
                
                # Save the NFFG in the database, with the state initializing
                Graph().addNFFG(nffg, session_id)
                
                Graph().setNodeID(nffg.db_id, node.id)
                
                # Instantiate profile
                logging.info('Call CA to instantiate NF-FG')
                logging.debug(nffg.getJSON())
                orchestrator.instantiateProfile(nffg, node)
                logging.debug('NF-FG instantiated') 
                
                Session().updateSessionNode(session_id, node.id, node.id)    
            except Exception as ex:
                logging.exception(ex)
                '''
                Graph().delete_graph(nffg.db_id)
                '''
                Session().set_error(session_id)
                raise ex
        
        Session().updateStatus(session_id, 'complete')
                                
        return session_id
        
    def prepareNFFG(self, nffg):
        manager = NFFG_Manager(nffg)  
        
        # Retrieve the VNF templates, if a node is a new graph, expand it
        logging.debug('Add templates to nffg')
        manager.addTemplates()
        logging.debug('Post expansion: '+nffg.getJSON())
        
        # Optimize NF-FG, currently the switch VNF when possible will be collapsed
        manager.mergeUselessVNFs()   
        
        # Change the remote node ID in remote_endpoint_id and in prepare_connection_to_remote_endpoint_id to the internal value
        self.convertRemoteNodeID(nffg)
        
    def checkNFFGStatus(self, service_graph_id):
        # TODO: Check if the graph exists, if true
        try:
            session_id = Session().get_active_user_session_by_nf_fg_id(service_graph_id).id
        except sessionNotFound:
            return False
        
        status = self.getResourcesStatus(session_id)
        
        if status is None:
            return False
        # If the status of the graph is complete, return False
        if status['status'] == 'complete' or DEBUG_MODE is True:
            return True
        # If the graph is in ERROR.. raise a proper exception
        if status['status'] == 'error':
            raise GraphError("The graph has encountered a fatal error, contact the administrator")
        # TODO:  If the graph is still under instantiation returns 409
        if status['status'] == 'in_progress':
            raise Exception("Graph busy")
        # If the graph is deleted, return True
        if status['status'] == 'ended' or status['status'] == 'not_found':
            return False
    
    def getStatus(self, nffg_id):
        '''
        Returns the status of the graph
        '''        
        logging.debug("Getting resources information for graph id: "+str(nffg_id))
        # TODO: have I to manage a sort of cache? Reading from db the status, maybe
        session_id = Session().get_active_user_session_by_nf_fg_id(nffg_id).id
        
        logging.debug("Corresponding to session id: "+str(session_id))
        status = self.getResourcesStatus(session_id)
        return json.dumps(status)
    
    def getResourcesStatus(self, session_id):
        graphs_ref = Graph().getGraphs(session_id)
        for graph_ref in graphs_ref:
            # Check where the nffg is instantiated and get the instance of the CA and the endpoint of the node
            node = Node().getNode(Graph().getNodeID(graph_ref.id))
            
            # Get the status of the resources
            scheduler = Scheduler(graph_ref.id, self.user_data)  
            orchestrator = scheduler.getInstance(node)
            status = orchestrator.getStatus(node)
            logging.debug(status)
            return status
    
    def convertRemoteNodeID(self, nffg):
        '''
        Convert the remote graph id present in the remote_endpoint_id (inside the end-point),
        in the internal ID created by the orchestrator (that is the one sent to the component adapter).
        '''
        for end_point in nffg.end_points:
            if end_point.remote_endpoint_id is not None:
                session_id = Session().get_active_user_session_by_nf_fg_id(end_point.remote_endpoint_id.split(':')[0],
                    error_aware=True).id
                graphs_ref = Graph().getGraphs(session_id)
                for graph_ref in graphs_ref:
                    remote_nffg = Graph().get_nffg(graph_ref.id)
                    for remote_end_point in remote_nffg.end_points:
                        if remote_end_point.id == end_point.remote_endpoint_id.split(':')[1]:
                            end_point.remote_endpoint_id = str(graph_ref.id)+ ':' +end_point.remote_endpoint_id.split(':')[1]
    
    def updateRemoteGraph(self, remote_nffgs_dict):
        for remote_nffg in remote_nffgs_dict.itervalues():
            try:
                session = Session().get_active_user_session_by_nf_fg_id(remote_nffg.id, error_aware=True)
            except sessionNotFound:
                continue
            remote_user_data = UserData()
            remote_user_data.getUserData(session.user_id)
            Session().updateStatus(session.id, 'updating')
            self.prepareNFFG(remote_nffg)
            scheduler = Scheduler(remote_nffg.db_id, remote_user_data)
            orchestrator, node = scheduler.schedule(remote_nffg)
            old_nf_fg = Graph().get_nffg(remote_nffg.db_id)
            try:
                orchestrator.updateProfile(remote_nffg, old_nf_fg, node)
            except Exception as ex:
                logging.exception(ex)
                '''
                Graph().delete_graph(nffg.db_id)
                '''
                Session().set_error(session.id)
                raise ex     
            Session().updateStatus(session.id, 'complete')
    
    def analizeRemoteConnection(self, nffg, node, delete=False):
        '''
        Check if the nffg will be installed in the same node of an eventually remote graph.
        In this is not the case, the orchestrator has to characterize in a better way the end-point. 
        '''
        # Getting remote graphs
        remote_nffgs_dict = {}
        for end_point in nffg.end_points:
            if end_point.remote_endpoint_id is not None:
                remote_graph_id = end_point.remote_endpoint_id.split(':')[0]
                if remote_graph_id in remote_nffgs_dict:
                    remote_nffg = remote_nffgs_dict[end_point.remote_endpoint_id.split(':')[0]]
                else:
                    remote_nffg = Graph().get_nffg(end_point.remote_endpoint_id.split(':')[0])
                    remote_nffgs_dict[str(remote_nffg.db_id)] = remote_nffg
                for remote_end_point in remote_nffg.end_points:
                    if remote_end_point.id == end_point.remote_endpoint_id.split(':')[1]:
                        if delete is False:
                            remote_end_point.prepare_connection_to_remote_endpoint_ids.append(str(nffg.db_id)+':'+end_point.id)
                        else:
                            remote_end_point.prepare_connection_to_remote_endpoint_ids.remove(str(nffg.db_id)+':'+end_point.id)
                            
        # TODO: characterization in case of different node instantiation
        
        return remote_nffgs_dict
    
    def checkExternalConnections(self, nffg):
        for end_point in nffg.end_points:
            if end_point.prepare_connection_to_remote_endpoint_ids:
                return True
        return False
    
    def getTemplate(self, instance_id):
        template_location = Graph().getVNFFromInternalID(internal_id=instance_id).template_location
        return json.dumps(NFFG_Manager(None).getTemplate(template_location).getDict())
    
    def getYANG(self, instance_id):
        template_location = Graph().getVNFFromInternalID(internal_id=instance_id).template_location
        temlate_dict = NFFG_Manager(None).getTemplate(template_location).getDict()
        ValidateTemplate().validate(temlate_dict)
        template = Template()
        template.parseDict(temlate_dict)
        yang =  Images().getConfiguationModel(template.uri.split('/v2/images/')[1])
        logging.debug(yang)
        return yang