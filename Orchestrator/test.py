'''
Created on 26 set 2015

@author: Andrea
'''
from Orchestrator.controller import UpperLayerOrchestratorController
from Common.userAuthentication import UserAuthentication

import json

username = "AdminPoliTO"
tenant = "PoliTO_chain1"
password = "AdminPoliTO"

userdata = UserAuthentication().authenticateUserFromCredentials(username, password, tenant)

with open('Graphs/jolnet_isp.json') as data_file:    
    nf_fg = json.load(data_file)
    controller = UpperLayerOrchestratorController(userdata)
    controller.put(nf_fg)