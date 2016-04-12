'''
Created on Feb 15, 2015

@author: fabiomignini
'''
import json
import logging
from service_layer_application_core.sql.session import Session
from service_layer_application_core.config import Configuration

DEBUG_MODE = Configuration().DEBUG_MODE

class UserSession(object):
    def __init__(self, user_id, token):
        self.user_id = user_id
        self.token = token
        
    def checkSession(self, nffg_id, orchestrator):
        '''
        return true if there is already an active session of the user 
        and it is really instantiated in a node
        '''

        session_status = Session().checkSession(self.user_id)
        if session_status is True:
            user_session = Session().get_active_user_session(self.user_id)
            if DEBUG_MODE is False:
                response = json.loads(orchestrator.getNFFGStatus(nffg_id))
                if response['status'] != 'error' or response['status'] != 'not_found':
                    # The user profile is really instantiated
                    return True
                if response['status'] != 'in_progress':
                    logging.debug("NFFG: "+str(nffg_id)+" in progress!");
                else:
                    # Set error state for all active session for the user
                    logging.debug("ERROR in NF-FG for user "+user_session.user_id);
                    Session().set_error_by_nffg_id(nffg_id)
            else:
                return True
        return False

