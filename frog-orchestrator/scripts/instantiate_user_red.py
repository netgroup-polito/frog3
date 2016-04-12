'''
Created on Oct 30, 2014

@author: fabiomignini
'''
import json, requests, sys, re

from Orchestrator.config import Configuration

keystone_authentication_url = Configuration().AUTH_SERVER+"/v2.0/tokens"

authenticationData = {"auth": {"tenantName": "red", "passwordCredentials": {"username": "red", "password": "stack"}}}


headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
resp = requests.post(keystone_authentication_url, data=json.dumps(authenticationData), headers=headers)
resp.raise_for_status()
tokendata = json.loads(resp.text)

if len(sys.argv) != 2:
    print "Usage: instantiate_user_blu <mac_address>"
    sys.exit()
print "Intantiating graph for device "+sys.argv[1]
matchObj = re.match( r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', sys.argv[1])
if not matchObj:
    print "Not valid mac address"
    sys.exit()
mac = sys.argv[1]


orchestrator = "http://localhost:8000/orchestrator"
request_body = {"session":{
                    "session_param" : {
                       "endpoint":{
                            "type": "bridged",
                            "interface": "veth1", 
                            "switch": "br-int"
                        },
                        "mac": mac,
                        "node_id": "00:00:8a:54:5d:05:48:4f",
                        "SW_endpoint": "3"
                }}} 


headers_graph = {'X-Auth-Token': tokendata['access']['token']['id']}
resp = requests.put(orchestrator, data=json.dumps(request_body), headers=headers_graph)
try:
    print "Response code by service layer: "+str(resp.status_code)
    resp.raise_for_status()
except:
    print "ERROR - User Green is NOT correctly instantiated"
    sys.exit()
print "User Green is now correctly instantiated"
