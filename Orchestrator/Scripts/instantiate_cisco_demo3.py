'''
Created on Oct 30, 2014

@author: fabiomignini
'''
import json, requests, sys

from Common.config import Configuration

keystone_authentication_url = Configuration().AUTH_SERVER+"/v2.0/tokens"

username = "cisco-demo3"
tenant = "cisco-demo3"
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
resp = requests.put(orchestrator, data=json.dumps(request_body), headers=headers_graph)
try:
    print "Response code by service layer: "+str(resp.status_code)
    resp.raise_for_status()
except:
    print "ERROR - User "+username+" is NOT correctly instantiated"
    sys.exit()
print "User "+username+" is now correctly instantiated"
