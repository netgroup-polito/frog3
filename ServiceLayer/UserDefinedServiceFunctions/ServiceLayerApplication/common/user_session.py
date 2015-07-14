'''
Created on Feb 15, 2015

@author: fabiomignini
'''
import json
import logging
from Common.SQL.session import Session
from Common.exception import ResourceAlreadyExistsOnNode

class UserSession(object):
    def __init__(self, user_id, token, profile_id = None):
        self.user_id = user_id
        self.token = token
        self.profile_id = profile_id
        
    def checkSession(self, nffg_id, orchestrator):
        '''
        return true if there is already an active session of the user 
        and it is really instantiated in a node
        '''

        session_status = Session().checkSession(self.user_id, self.token, self.profile_id)
        user_session = Session().get_active_session(self.user_id, self.token, self.profile_id)
        if session_status is True:
            
            response = json.loads(orchestrator.checkNFFG(nffg_id, self.token.get_token()))
            if response['status'] != 'error' or response['status'] != 'not_found':
                # The user profile is really instantiated
                return True
            else:
                # Set error state for all active session for the user
                logging.debug("ERROR in NF-FG for user "+user_session.user_id);
                Session().set_error_by_nffg_id(nffg_id)  
        return False

