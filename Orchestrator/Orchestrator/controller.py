'''
@author: fabiomignini
'''

from __future__ import division

import json
import logging
import scheduler 
import uuid

from Common.exception import unauthorizedRequest
from Common.authentication import KeystoneAuthentication
from Common.SQL.session import set_ended, get_active_user_session_info_from_id, get_instantiated_profile, get_active_user_session_from_id, get_active_user_session, update_session, add_session
from Common.NF_FG.validator import ValidateNF_FG
from Common.config import Configuration
from Common.NF_FG.nf_fg import NF_FG
from Common.NF_FG.nf_fg_managment import NF_FG_Management
from ServiceLayerApplication.common.user_session import UserSession
from Common.SQL.nodes import getNodeID

# Specifies the type of authentication for the service layer toward the orchestrator.
# The service layer can either specify a user/password (that will be used by the orchestrator
# to authenticate in keystone) ('basic' authentication), or pass directly a token already 
# obtained previously from Keystone ('token').
AUTH_MODE = 'none'


class UpperLayerOrchestratorController(object):
    '''
        Class that performs the logic of orchestrator
    '''
    def __init__(self, keystone_server, OrchestratorToken = None, method = None, token = None, response = None, username = None, password = None, tenant = None):
        
        self.keystone_server = keystone_server
               
        if username is not None and password is not None and tenant is not None:
            AUTH_MODE = 'basic'
            self.username = username
            self.password = password
            self.tenant = tenant
                
        if token is not None:
            AUTH_MODE = 'token'       
            self.token = token
            
        if OrchestratorToken is not None:
            AUTH_MODE = 'token'     
            self.orchToken = OrchestratorToken
            
        if response is not None:
            self.response = response 
            
        if AUTH_MODE == 'none':
            raise unauthorizedRequest("Authentication parameters missing")

    def get(self):
         
        pass
    
    def delete(self,session_id):
        # Authenticate the User
        logging.debug("Authenticating the user - DELETE");
        if AUTH_MODE == 'basic':
            token = KeystoneAuthentication(self.keystone_server, self.tenant, self.username, self.password)
            self.token = token.get_token()
        elif AUTH_MODE == 'token':
            token = KeystoneAuthentication(self.keystone_server, user_token=self.token, orch_token=self.orchToken)
        
        # Retrieve the session data, from active session on a port of a switch passed, if no active session raise an exception
        # session = SessionSQL.get_active_user_device_session(token.get_userID(), self.session)
        logging.debug("session_id: "+session_id)
        
        # Get session
        infrastructure, profile = get_active_user_session_info_from_id(session_id) 
        
        # Get instantiated profile
        nf_fg = get_instantiated_profile(token.get_userID())
        
        # De-instantiate profile
        # TODO: manage the case in which there aren't session
        logging.debug("infra: "+str(infrastructure))

        orchestrator = scheduler.Select(json.loads(infrastructure), session_id, token.get_endpoints("orchestration"), token.get_endpoints("compute"))
        orchestrator.deinstantiateProfile(token, profile, nf_fg)
        
        # Set the field ended in the table session to the actual datatime
        set_ended(session_id)   
    
    def update(self, nf_fg, delete = False):
        logging.info('Orchestrator - UPDATE - Authenticating the user - UPDATE')
        if AUTH_MODE == 'basic':
            token = KeystoneAuthentication(self.keystone_server, self.tenant, self.username, self.password)
            self.token = token.get_token()
        elif AUTH_MODE == 'token':
            token = KeystoneAuthentication(self.keystone_server, user_token=self.token, orch_token=self.orchToken)
        
        # Get profile from session
        logging.debug('Orchestrator - UPDATE - get instantiate profile')
        old_profile = get_instantiated_profile(token.get_userID())
        logging.debug('Orchestrator - UPDATE - Old profile\n'+old_profile)
        old_profile = json.loads(old_profile)
        
        nf_fg = self.prepareNF_FG(token, nf_fg)
        # returns the number of active session for the user, 
        # and if exists the session for the requested device
        nf_fg_session = get_active_user_session(token.get_userID()) 
        
        orchestrator = scheduler.Select(json.loads(nf_fg_session.infrastructure), nf_fg_session.id, token.get_endpoints("orchestration"), token.get_endpoints("compute"))
        
        #orchestrator.updateProfile(nf_fg_session.user_id, json.loads(nf_fg.getJSON()), old_profile)
        orchestrator.updateProfile(nf_fg._id, json.loads(nf_fg.getJSON()), old_profile, token, delete)
        
        
        session_id = update_session(nf_fg._id,
           nf_fg.getJSON(),
           json.dumps({"infrastructure":{"name":type(orchestrator).__name__,"module": type(orchestrator).__module__}})
           )
        
        return session_id
        
        #raise NotImplemented("Update not implemented")  
        
    def put(self, nf_fg):
        """
        Manage the request of NF-FG instantiation
        """
        
        # Authenticate the User
        logging.info('Orchestrator - PUT - Authenticating the user')
        if AUTH_MODE == 'basic':
            token = KeystoneAuthentication(self.keystone_server, self.tenant, self.username, self.password)
            self.token = token.get_token()
        elif AUTH_MODE == 'token':
            token = KeystoneAuthentication(self.keystone_server, user_token=self.token, orch_token=self.orchToken)
        
        nf_fg = NF_FG(nf_fg)
        #logging.debug("Orchestrator - PUT - nf-fg: \n\n"+nf_fg.getJSON())
        
        logging.debug('Orchestrator - PUT - Checking session ')
        if UserSession(token.get_userID(), token, nf_fg.id).checkSession() is True:
            if token.get_username() == "nobody" or token.get_username() == "isp":
                logging.debug('Orchestrator - PUT - '+token.get_username()+' NF-FG is already instantiated')
            logging.debug('Orchestrator - PUT - Updating NF-FG')
            session_id = self.update(nf_fg)
            logging.debug('Orchestrator - PUT - Update success')
        else:
        
            # Manage profile
            #logging.info('Orchestrator - PUT - Manage NF-FG')
            nf_fg = self.prepareNF_FG(token, nf_fg)
                    
            # Take a decision about where we should schedule the serving graph (UN or HEAT)
            session_id  = uuid.uuid4().hex
            orchestrator = scheduler.Schedule(session_id, token.get_endpoints("orchestration"), token.get_endpoints("compute"))
        
            # Instantiate profile
            logging.info('Orchestrator - PUT - Call CA to instantiate NF-FG')
            #logging.debug('\n'+nf_fg.getJSON())
            orchestrator.instantiateProfile(json.loads(nf_fg.getJSON()), token)
            logging.debug('Orchestrator - PUT - NF-FG instantiated')
            #logging.debug('\n'+nf_fg.getJSON())
                 
            # Save instantiated NF-FG in db            
            
            add_session(session_id, 
                        token.get_userID(),
                        nf_fg._id,
                        nf_fg.getJSON(),
                        json.dumps({"infrastructure":{"name":type(orchestrator).__name__,"module": type(orchestrator).__module__}}),
                        getNodeID(token.get_userID()),
                        getNodeID(token.get_userID())
                        )
    
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
