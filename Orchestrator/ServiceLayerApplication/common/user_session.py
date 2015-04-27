'''
Created on Feb 15, 2015

@author: fabiomignini
'''
import json
import logging
from Common.SQL.session import checkSession as checkSessionDB
from Common.SQL.session import set_error
from Common.exception import ResourceAlreadyExistsOnNode
from Orchestrator.scheduler import Select

class UserSession(object):
    def __init__(self, user_id, token):
        self.user_id = user_id
        self.token = token
        
    def checkSession(self):
        '''
        return true if there is already an active session of the user 
        and it is really instantiated in a node
        '''
        res,user_session = checkSessionDB(self.user_id, self.token)
        if res is True:
            orchestratorCA_instance = Select(json.loads(user_session.infrastructure), user_session.id, self.token.get_endpoints("orchestration"), self.token.get_endpoints("compute"))
            if orchestratorCA_instance.checkProfile(user_session.id, self.token) is True:
                # The user profile is really instantiated
                return True
            else:
                # Set error state for all active session for the user
                logging.debug("ERROR in NF-FG for user "+user_session.user_id);
                set_error(self.user_id)  
                orchestratorCA_instance.deleteGraphResorces(user_session.profile, self.token)
                # TODO: set active FALSE for ENDPOINT and ENDPOINT connection of this session
                logging.debug("DELETED NF-FG for user "+user_session.user_id);
        return False

