import json, requests, sys, re

keystone_authentication_url = "http://controller:35357/v2.0/tokens"

if len(sys.argv) != 6 and len(sys.argv) != 5:
    print "Usage: service_graph.py <user> <tenant> <pwd> [<mac_address>] <method>"
    sys.exit()
elif len(sys.argv) == 6: 
    matchObj = re.match( r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', sys.argv[4])
    if not matchObj:
        print "Not valid mac address"
    sys.exit()
    mac = sys.argv[4]
    method = sys.argv[5]
else:
    mac = None
    method = sys.argv[4]
    
username = sys.argv[1]
tenant = sys.argv[2]
password = sys.argv[3]


if method != "PUT" and method != "DELETE":
    print "wrong param!"
    print "method: [PUT|DELETE]"
    sys.exit()
if method == "PUT":
    print "Intantiating graph for device "+sys.argv[4]
else:
    print "Deleting graph for device "+sys.argv[4]

authenticationData = {"auth": {"tenantName": tenant, "passwordCredentials": {"username": username, "password": password}}}


headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
resp = requests.post(keystone_authentication_url, data=json.dumps(authenticationData), headers=headers)
resp.raise_for_status()
tokendata = json.loads(resp.text)

if method == "PUT":
    orchestrator = "http://orchestrator:8000/orchestrator"
else:
    if mac == None:
        orchestrator = "http://orchestrator:8000/orchestrator"
    else:
        orchestrator = "http://orchestrator:8000/orchestrator/"+mac

if mac != None:
    request_body = {"session":{"session_param" : {"mac": mac}}} 
else:
    request_body = {"session":{"session_param" : {}}} 
    
headers_graph = {'X-Auth-Token': tokendata['access']['token']['id']}
if method == "PUT":
    resp = requests.request(method, url=orchestrator, data=json.dumps(request_body), headers=headers_graph)
else:
    resp = requests.request(method, url=orchestrator, headers=headers_graph)
try:
    print "Response code by service layer: "+str(resp.status_code)
    resp.raise_for_status()
except:
    if method == "PUT":
        print "ERROR - User "+username+" is NOT correctly instantiated"
    else:
        print "ERROR - User "+username+" is NOT correctly deleted"
    sys.exit()
if method == "PUT":
    print "User "+username+" is now correctly instantiated"
else:
    print "User "+username+" is now correctly deleted"