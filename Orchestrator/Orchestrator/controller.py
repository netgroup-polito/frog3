'''
@author: fabiomignini
'''

from __future__ import division

import json
import logging
from scheduler import Scheduler
import uuid

from Common.exception import sessionNotFound, GraphError
from Common.SQL.session import Session
from Common.SQL.graph import Graph
from Common.SQL.node import Node 
from Common.NF_FG.validator import ValidateNF_FG
from Common.NF_FG.nf_fg import NF_FG
from Common.NF_FG.nf_fg_managment import NF_FG_Management

'''
    NEWS: From now on, CAs are in charge of getting users tokens from Keystone (if needed)
    Moreover, they should insert Keystone user's internal id into the Session table (user_id),
    exactly like they already do with other OpenStack objects...
'''


class UpperLayerOrchestratorController(object):
    '''
        Class that performs the logic of orchestrator
    '''
    def __init__(self, userdata):
        self.userdata = userdata

    def get(self, nffg_id):
        '''
        Returns the status of the graph
        '''
        logging.debug("Authenticating the user - Get");
        
        logging.debug("Getting resources information for graph id: "+str(nffg_id))
        # TODO: have I to manage a sort of cache? Reading from db the status, maybe
        session_id = Session().get_active_user_session_by_nf_fg_id(nffg_id).id
        
        logging.debug("Corresponding to session id: "+str(session_id))
        status = self.getResourcesStatus(session_id)
        return json.dumps(status)
    
    def delete(self, nffg_id):        
        # Authenticate the User
        logging.debug("Authenticating the user - DELETE");
        
        # Retrieve the session data, from active session on a port of a switch passed, if no active session raise an exception
        # session = SessionSQL.get_active_user_device_session(token.get_userID(), self.session)
        ##logging.debug("nffg_id: "+nffg_id)
        
        # Get the component adapter associated  to the node where the nffg was instantiated
        session_id = Session().get_active_user_session_by_nf_fg_id(nffg_id, error_aware=False).id
        logging.debug("session_id: "+str(session_id))
        node = Node().getNode(Graph().getNodeID(session_id))
        
        # Get instantiated nffg
        instantiated_nffg = Graph().get_nffg(session_id)
        logging.debug('Instantiated_nffg that we are going to delete: '+instantiated_nffg.getJSON())
        
        # De-instantiate profile
        orchestrator = Scheduler(session_id, self.userdata).getInstance(node)
        try:
            orchestrator.deinstantiateProfile(instantiated_nffg, node)
        except Exception as ex:
            logging.exception(ex)
            raise ex
        
        # Set the field ended in the table session to the actual datatime        
        Graph().delete_graph(session_id)
        Session().set_ended(session_id)
    
    def update(self, nf_fg, delete = False):
        logging.info('Orchestrator - UPDATE - Authenticating the user - UPDATE')
        
        session = Session().get_active_user_session_by_nf_fg_id(nf_fg.id, error_aware=True)
        Session().updateStatus(session.id, 'updating')
        
        # Get profile from session
        logging.debug('Orchestrator - UPDATE - get instantiate profile')
        old_nf_fg = Graph().get_nffg(session.id)
        logging.debug('Orchestrator - UPDATE - Old profile\n'+old_nf_fg.getJSON())

        nf_fg = self.prepareNF_FG(nf_fg)
        
        # Get the component adapter associated  to the node where the nffg was instantiated
        old_node = Node().getNode(Graph().getNodeID(session.id))
        scheduler = Scheduler(session.id, self.userdata)
        orchestrator, new_node = scheduler.schedule(nf_fg)
        
        if new_node.id != old_node.id:
            orchestrator.deinstantiateProfile(nf_fg, old_node)
            Graph().delete_graph(session.id)
            Graph().addNFFG(nf_fg, session.id)
            Graph().setNodeID(session.id, Node().getNodeFromDomainID(new_node.domain_id).id)
            orchestrator.instantiateProfile(nf_fg, new_node)
        else:
            # Update the nffg
            try:
                orchestrator.updateProfile(nf_fg, old_nf_fg, new_node)
            except Exception as ex:
                logging.exception(ex)
                Session().set_error(session.id)
                raise ex
        
        Session().updateStatus(session.id, 'complete')
        Session().updateSessionNode(session.id, new_node.id, new_node.id)
        return session.id
        
    def put(self, nf_fg):
        """
        Manage the request of NF-FG instantiation
        """        
        nf_fg = NF_FG(nf_fg)
        logging.debug('Orchestrator - PUT - Checking session ')
        if self.checkNFFGStatus(nf_fg.id) is True:

            logging.debug('Orchestrator - PUT - Updating NF-FG')
            session_id = self.update(nf_fg)
            logging.debug('Orchestrator - PUT - Update success')
        else:
            session_id  = uuid.uuid4().hex
            Session().inizializeSession(session_id, None, nf_fg.id, nf_fg.name)
            try:
                # Manage profile
                nf_fg = self.prepareNF_FG(nf_fg)
                 
                # Save the NFFG in the database, with the state initializing
                Graph().addNFFG(nf_fg, session_id)
                
                # Take a decision about where we should schedule the serving graph (UN or HEAT), and the node
                scheduler = Scheduler(session_id, self.userdata)           
                orchestrator, node = scheduler.schedule(nf_fg)
                
                # Instantiate profile
                logging.info('Orchestrator - PUT - Call CA to instantiate NF-FG')
                logging.debug(nf_fg.getJSON())
                orchestrator.instantiateProfile(nf_fg, node)
                logging.debug('Orchestrator - PUT - NF-FG instantiated') 
                
                Session().updateSessionNode(session_id, node.id, node.id)    
                
            except Exception as ex:
                logging.exception(ex)
                Graph().delete_graph(session_id)
                Session().set_error(session_id)
                raise ex
        
        Session().updateStatus(session_id, 'complete')
                                
        return session_id
        
    def prepareNF_FG(self, nf_fg):
        manage = NF_FG_Management(nf_fg)  

        # Validate profile
        logging.debug('Orchestrator - prepareNF_FG - Validate JSON')
        ValidateNF_FG(json.loads(nf_fg.getJSON())).validate()
        
        # Retrieve the VNF templates (for the moment from glance), if a node is a new graph, expand it
        logging.debug('Orchestrator - prepareNF_FG - Add manifests')
        manage.addManifests()
        return nf_fg

    def checkNFFGStatus(self, service_graph_id):
        # TODO: Check if the graph exists, if true
        try:
            session_id = Session().get_active_user_session_by_nf_fg_id(service_graph_id).id
        except sessionNotFound:
            return False
        
        status = self.getResourcesStatus(session_id)
        
        # If the status of the graph is complete, return False
        if status['status'] == 'complete':
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
    
    def getResourcesStatus(self, session_id):
        # Check where the nffg is instantiated and get the instance of the CA and the endpoint of the node
        node = Node().getNode(Graph().getNodeID(session_id))
        
        # Get the status of the resources
        scheduler = Scheduler(session_id, self.userdata)  
        orchestrator = scheduler.getInstance(node)
        status = orchestrator.getStatus(session_id, node)
        logging.debug(status)
        return status

    def getControllerURL(self, nffg):
        node = Node().getNodeFromDomainID(Scheduler().checkEndpointLocation(nffg))
        return node.openstack_controller