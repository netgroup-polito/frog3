'''
Created on Oct 23, 2015

@author: fabiomignini
'''
import requests, json, logging

from service_layer_application_core.controller import ServiceLayerController
from service_layer_application_core.user_authentication import UserData

username = 'demo2'
password = 'stack'
tenant = 'demo2'
logging.basicConfig(level=logging.DEBUG)

controller = ServiceLayerController(user_data=UserData(username, password, tenant))
controller.put(None)


exit()



orchestrator_endpoint = "http://127.0.0.1:8000/service-layer"

headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 
           'X-Auth-User': username, 'X-Auth-Pass': password, 'X-Auth-Tenant': tenant}
body = {"session":{"mac":"fc:4d:e2:56:9f:19"}}
requests.put(orchestrator_endpoint, json.dumps(body), headers=headers)
print 'Job completed'