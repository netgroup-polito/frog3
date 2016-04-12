'''
Created on Nov 4, 2015

@author: fabiomignini
'''
import logging
from orchestrator_core.userAuthentication import UserData
from orchestrator_core.controller import UpperLayerOrchestratorController

nffg_id = '00000001'
username = 'demo2'
tenant = 'demo2'
password = 'stack'

logging.basicConfig(level=logging.DEBUG)
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)
sqlalchemy_log = logging.getLogger('sqlalchemy.engine')
sqlalchemy_log.setLevel(logging.WARNING)

controller = UpperLayerOrchestratorController(user_data=UserData(username, password, tenant))
controller.delete(nffg_id)

print 'Job completed'
exit()