'''
Created on Jul 14, 2015

@author: stack
'''
from Orchestrator.controller import UpperLayerOrchestratorController
from Common.config import Configuration

import json
from Common.NF_FG.nf_fg import NF_FG

conf = Configuration()

keystone_authentication_url = Configuration().AUTH_SERVER+"/v2.0/tokens"

username = "AdminPoliTO"
tenant = "PoliTO_chain1"
password = "AdminPoliTO"
keystone_server = conf.AUTH_SERVER;

controller = UpperLayerOrchestratorController(keystone_server, method = "ServiceLayerApplication", username = username, password = password, tenant = tenant)

with open('Graphs/jolnet_isp_update3.json') as data_file:    
    nf_fg = json.load(data_file)
    nffg = NF_FG(nf_fg)
    session_id = controller.update(nffg)