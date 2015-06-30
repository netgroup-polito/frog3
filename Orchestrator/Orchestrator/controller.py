'''
@author: fabiomignini
'''

from __future__ import division

import json
import logging
from scheduler import Scheduler
import uuid

from Common.exception import unauthorizedRequest, sessionNotFound, GraphError
from Common.authentication import KeystoneAuthentication
from Common.SQL.session import Session
from Common.SQL.graph import Graph
from Common.SQL.node import Node 
from Common.NF_FG.validator import ValidateNF_FG
from Common.config import Configuration
from Common.NF_FG.nf_fg import NF_FG
from Common.NF_FG.nf_fg_managment import NF_FG_Management
from httplib import CONFLICT


class UpperLayerOrchestratorController(object):
    '''
        Class that performs the logic of orchestrator
    '''
    def __init__(self, keystone_server, OrchestratorToken = None, method = None, token = None, response = None, username = None, password = None, tenant = None):
        
        # Specifies the type of authentication for the service layer toward the orchestrator.
        # The service layer can either specify a user/password (that will be used by the orchestrator
        # to authenticate in keystone) ('basic' authentication), or pass directly a token already 
        # obtained previously from Keystone ('token').
        self.AUTH_MODE = 'none'
        self.keystone_server = keystone_server
        
        if username is not None and password is not None and tenant is not None:
            self.AUTH_MODE = 'basic'
            self.username = username
            self.password = password
            self.tenant = tenant
                
        if token is not None:
            self.AUTH_MODE = 'token'       
            self.token = token
            
        if OrchestratorToken is not None:
            self.AUTH_MODE = 'token'     
            self.orchToken = OrchestratorToken
            
        if response is not None:
            self.response = response 
            
        if self.AUTH_MODE == 'none':
            raise unauthorizedRequest("Authentication parameters missing")

    def get(self, nffg_id):
        '''
        Returns the status of the graph
        '''
        logging.debug("Authenticating the user - Get");
        if self.AUTH_MODE == 'basic':
            token = KeystoneAuthentication(self.keystone_server, self.tenant, self.username, self.password)
            self.token = token.get_token()
        elif self.AUTH_MODE == 'token':
            token = KeystoneAuthentication(self.keystone_server, user_token=self.token, orch_token=self.orchToken)
            
        # TODO: have I to manage a sort of cache? Reading from db the status, maybe
        session_id = Session().get_active_user_session_by_nf_fg_id(nffg_id).id
        status = self.getResourcesStatus(session_id)
        return json.dumps(status)
    
    def delete(self, nffg_id):        
        # Authenticate the User
        logging.debug("Authenticating the user - DELETE");
        if self.AUTH_MODE == 'basic':
            token = KeystoneAuthentication(self.keystone_server, self.tenant, self.username, self.password)
            self.token = token.get_token()
        elif self.AUTH_MODE == 'token':
            token = KeystoneAuthentication(self.keystone_server, user_token=self.token, orch_token=self.orchToken)
        
        # Retrieve the session data, from active session on a port of a switch passed, if no active session raise an exception
        # session = SessionSQL.get_active_user_device_session(token.get_userID(), self.session)
        logging.debug("nffg_id: "+nffg_id)
        
        # Get the component adapter associated  to the node where the nffg was instantiated
        session_id = Session().get_active_user_session_by_nf_fg_id(nffg_id, error_aware=False).id
        logging.debug("session_id: "+str(session_id))
        node = Node().getNode(Graph().getNodeID(session_id))
        
        # Get instantiated nffg
        instantiated_nffg = Graph().get_nffg(session_id)
        logging.debug('Instantiated_nffg that we are going to delete: '+instantiated_nffg.getJSON())
        
        # Get nffg
        nffg = Graph().get_nffg_by_id(nffg_id)
        
        # De-instantiate profile
        orchestrator, node_endpoint = Scheduler(session_id).getInstance(node)
        '''
        try:
            orchestrator.deinstantiateProfile(token, instantiated_nffg, node.domain_id)
        except Exception as ex:
            logging.exception(ex)
            Session().set_error(session_id)
            raise ex
        '''
        
        # Set the field ended in the table session to the actual datatime
        
        Graph().delete_graph(session_id)
        Session().set_ended(session_id)
    
    def update(self, nf_fg, delete = False):
        logging.info('Orchestrator - UPDATE - Authenticating the user - UPDATE')
        if self.AUTH_MODE == 'basic':
            token = KeystoneAuthentication(self.keystone_server, self.tenant, self.username, self.password)
            self.token = token.get_token()
        elif self.AUTH_MODE == 'token':
            token = KeystoneAuthentication(self.keystone_server, user_token=self.token, orch_token=self.orchToken)
        
        session = Session().get_active_user_session(token.get_userID()) 
        Session().updateStatus(session.session_id, 'updating')
        
        # Get profile from session
        logging.debug('Orchestrator - UPDATE - get instantiate profile')
        old_nf_fg = Graph().get_instantiated_nffg(token.get_userID())
        logging.debug('Orchestrator - UPDATE - Old profile\n'+old_nf_fg)
        old_nf_fg = json.loads(old_nf_fg)
        
        nf_fg = self.prepareNF_FG(token, nf_fg)
            
        
        
        # Get the component adapter associated  to the node where the nffg was instantiated
        node = Node().getNode(Graph().getNodeID(session.session_id))
        scheduler = Scheduler(session.session_id)
        old_orchestrator_instance, old_node_endpoint = scheduler.getInstance(node)
        orchestrator, new_node_endpoint = scheduler.schedule(nf_fg)
        
        if new_node_endpoint != old_node_endpoint:
            self.delete(nf_fg.id)

        # Update the nffg
        '''
        try:
            orchestrator.updateProfile(json.loads(nf_fg.getJSON()), old_nf_fg, token, new_node_endpoint)
        except Exception as ex:
            logging.exception(ex)
            Session().set_error(session.session_id)
            raise ex
        '''
        
        Session().updateSession(session.session_id, Node().getNodeID(token.get_userID()), Node().getNodeID(token.get_userID()), 'complete')


        # TODO: update nffg status
        return session.session_id
        
    def put(self, nf_fg):
        """
        Manage the request of NF-FG instantiation
        """
        
        # Authenticate the User
        logging.info('Orchestrator - PUT - Authenticating the user')
        if self.AUTH_MODE == 'basic':
            token = KeystoneAuthentication(self.keystone_server, self.tenant, self.username, self.password)
            self.token = token.get_token()
        elif self.AUTH_MODE == 'token':
            token = KeystoneAuthentication(self.keystone_server, user_token=self.token, orch_token=self.orchToken)
        
        nf_fg = NF_FG(nf_fg)
        #logging.debug("Orchestrator - PUT - nf-fg: \n\n"+nf_fg.getJSON())
        
        logging.debug('Orchestrator - PUT - Checking session ')
        #if UserSession(token.get_userID(), token, nf_fg.id).checkSession() is True:
        if self.checkNFFGStatus(nf_fg.id) is True:
            logging.debug('Orchestrator - PUT - Updating NF-FG')
            session_id = self.update(nf_fg)
            logging.debug('Orchestrator - PUT - Update success')
        else:
            session_id  = uuid.uuid4().hex
            Session().inizializeSession(session_id, token.get_userID(), nf_fg.id, nf_fg.name)
            try:
                # Manage profile
                nf_fg = self.prepareNF_FG(token, nf_fg)
                 
                # Save the NFFG in the database, with the state initializing
                Graph().addNFFG(nf_fg, session_id)
                
                # Take a decision about where we should schedule the serving graph (UN or HEAT), and the node
                scheduler = Scheduler(session_id)           
                orchestrator, node_endpoint = scheduler.schedule(nf_fg)
                
                # Instantiate profile
                logging.info('Orchestrator - PUT - Call CA to instantiate NF-FG')
                logging.debug(nf_fg.getJSON())
                '''
                orchestrator.instantiateProfile(json.loads(nf_fg.getJSON()), token, node_endpoint)
                '''
                logging.debug('Orchestrator - PUT - NF-FG instantiated')
                     
                # Save instantiated NF-FG in db            
                Session().updateSession(session_id, Node().getNodeID(token.get_userID()), Node().getNodeID(token.get_userID()), 'complete')
            except Exception as ex:
                logging.exception(ex)
                Session().set_error(session_id)
                raise ex
                                
        return session_id
        
    def prepareNF_FG(self, token, nf_fg):
        manage = NF_FG_Management(nf_fg, self.token)  

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
        if status['graph'] == 'complete':
            return True
        # If the graph is in ERROR.. raise a proper exception
        if status['graph'] == 'error':
            raise GraphError("The graph has encountered a fatal error, contact the administrator")
        # TODO:  If the graph is still under instantiation returns 409
        if status['graph'] == 'deploying':
            pass
        # If the graph is deleted, return True
        if status['graph'] == 'ended' or status['graph'] == 'not_found':
            return False
    
    def getResourcesStatus(self, session_id):
        # Check where the nffg is instantiated and get the instance of the CA and the endpoint of the node
        node = Node().getNode(Graph().getNodeID(session_id))
        
        # Get the status of the resources
        scheduler = Scheduler(session_id)  
        orchestrator, node_endpoint = scheduler.getInstance(node)
        return orchestrator.getStatus(session_id, node_endpoint)
