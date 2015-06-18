'''
Created on May 27, 2015

@author: vida
'''
from Orchestrator.controller import UpperLayerOrchestratorController
from Common.config import Configuration

import json
from Common.authentication import KeystoneAuthentication
from Common.SQL.session import get_active_user_session_by_nf_fg_id

conf = Configuration()

keystone_authentication_url = Configuration().AUTH_SERVER+"/v2.0/tokens"

username = "AdminPoliTO"
tenant = "PoliTO_chain1"
password = "AdminPoliTO"
keystone_server = conf.AUTH_SERVER;

keystoneAuth = KeystoneAuthentication(keystone_server, tenant, username, password)
controller = UpperLayerOrchestratorController(keystone_server, method = "ServiceLayerApplication", username = username, password = password, tenant = tenant)

with open('Graphs/jolnet_graph2.json') as data_file:    
    nf_fg = json.load(data_file)
    profile_id = nf_fg['profile']['id']

session = get_active_user_session_by_nf_fg_id(profile_id)    
controller.delete(session.id)