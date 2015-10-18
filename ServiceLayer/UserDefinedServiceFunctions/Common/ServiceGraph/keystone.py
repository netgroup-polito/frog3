'''
Created on Apr 23, 2015

@author: fabiomignini
'''

import requests
import json


from Common.config import Configuration 

ORCH_PASSWORD = Configuration().ORCH_PASSWORD
ORCH_TENANT = Configuration().ORCH_TENANT
ORCH_USERNAME = Configuration().ORCH_USERNAME
INGRESS_PORT = Configuration().INGRESS_PORT
FLOW_PRIORITY = Configuration().FLOW_PRIORITY
MAXIMUM_NUMBER_OF_VNF_IN_GRAPH = Configuration().MAXIMUM_NUMBER_OF_VNF_IN_GRAPH

class KeystoneProfile(object):
    '''
    Class used to store the user profile information and executes the REST call to OpenStack API
    '''
    
    def __init__(self, keystone_server, user_id):
        '''
        Constructor
        Args:
            keystone_server:
                URL of the keystone server (example http://serverAddr:keystonePort)
            user_id:
                ID of the user for that we retrieve the profile
        '''
        self.keystone_profile_uri = keystone_server + "/v2.0/OS-UPROF/profile/users/" + user_id
         
        
    def _get(self, token): 
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        return requests.get(self.keystone_profile_uri, headers=headers)   
                   
    def get(self, token):
        '''
        Return the profile of the user
        '''
        resp = self._get(token)
        resp.raise_for_status()
        self.profile = json.loads(resp.text)
        return self.profile
    
    def check(self, token):
        resp = self._get(token)
        if resp.status_code == 200 or resp.status_code == 201:
            return True
        return False
    
    def post(self, token, profile):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.post(self.keystone_profile_uri, data=profile, headers=headers)
        resp.raise_for_status() 
    
