'''
Created on May 27, 2015

@author: vida
'''
from Orchestrator.controller import UpperLayerOrchestratorController
from Common.config import Configuration
from Common.authentication import KeystoneAuthentication

import json
import time

conf = Configuration()

keystone_authentication_url = Configuration().AUTH_SERVER+"/v2.0/tokens"

username = "AdminPoliTO"
tenant = "PoliTO_chain1"
password = "AdminPoliTO"
keystone_server = conf.AUTH_SERVER;

token = KeystoneAuthentication(keystone_server, tenant, username, password)

controller = UpperLayerOrchestratorController(keystone_server, method = "ServiceLayerApplication", username = username, password = password, tenant = tenant)

with open('Graphs/jolnet_isp.json') as data_file:    
    nf_fg = json.load(data_file)
    '''print(str(time.time()))'''
    session_id = controller.put(nf_fg)
    '''while (True):
        try:
            if controller.checkNFFGStatus(nf_fg['profile']['id'], token) is True:
                break;
        except:
            continue
    print(str(time.time()))'''