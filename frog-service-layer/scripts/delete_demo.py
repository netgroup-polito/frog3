'''
Created on Oct 30, 2014

@author: fabiomignini
'''
import json, requests, sys

from config import Configuration

keystone_authentication_url = Configuration().AUTH_SERVER+"/v2.0/tokens"

username = "demo"
tenant = "demo"
password = "stack"


authenticationData = {"auth": {"tenantName": tenant, "passwordCredentials": {"username": username, "password": password}}}


headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
resp = requests.post(keystone_authentication_url, data=json.dumps(authenticationData), headers=headers)
resp.raise_for_status()
tokendata = json.loads(resp.text)


orchestrator = "http://localhost:8000/orchestrator"
request_body = {"session":{
                    "session_param" : {
                        "SW_endpoint": "3"
                }}} 


headers_graph = {'X-Auth-Token': tokendata['access']['token']['id']}
resp = requests.delete(orchestrator, data=json.dumps(request_body), headers=headers_graph)
try:
    print "Response code by service layer: "+str(resp.status_code)
    resp.raise_for_status()
except:
    print "ERROR - User "+username+" is NOT correctly deleted"
    sys.exit()
print "User "+username+" is now correctly deleted"
