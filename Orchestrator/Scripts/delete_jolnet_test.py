'''
Created on May 27, 2015

@author: vida
'''
from Orchestrator.controller import UpperLayerOrchestratorController
from Common.config import Configuration

import json

conf = Configuration()

keystone_authentication_url = Configuration().AUTH_SERVER+"/v2.0/tokens"

username = "AdminPoliTO"
tenant = "PoliTO_chain1"
password = "AdminPoliTO"
keystone_server = conf.AUTH_SERVER;

controller = UpperLayerOrchestratorController(keystone_server, method = "ServiceLayerApplication", username = username, password = password, tenant = tenant)

with open('Graphs/jolnet_only_flows.json') as data_file:    
    nf_fg = json.load(data_file)
    profile_id = nf_fg['profile']['id']  
    controller.delete(profile_id)