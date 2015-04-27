'''
Created on Oct 30, 2014

@author: fabiomignini
'''
import json, requests, sys, re

from Common.config import Configuration

keystone_authentication_url = Configuration().AUTH_SERVER+"/v2.0/tokens"





if len(sys.argv) != 5:
    print "Usage: instantiate.py <user> <tenant> <pwd> <mac_address>"
    sys.exit()
print "Instantiating graph for device "+sys.argv[4]

matchObj = re.match( r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', sys.argv[4])
if not matchObj:
    print "Not valid mac address"
    sys.exit()
mac = sys.argv[4]

username = sys.argv[1]
tenant = sys.argv[2]
password = sys.argv[3]


authenticationData = {"auth": {"tenantName": tenant, "passwordCredentials": {"username": username, "password": password}}}


headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
resp = requests.post(keystone_authentication_url, data=json.dumps(authenticationData), headers=headers)
resp.raise_for_status()
tokendata = json.loads(resp.text)


orchestrator = "http://localhost:8000/orchestrator"
request_body = {"session":{
                    "session_param" : {
                        "mac": mac
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
