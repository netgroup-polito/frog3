'''
Created on May 27, 2015

@author: vida
'''
from Common.config import Configuration

import json
import requests
import sys

conf = Configuration()

username = "AdminPoliTO"
tenant = "PoliTO_chain1"
password = "AdminPoliTO"
orchestrator = "http://" + conf.ORCH_IP + ":" + conf.ORCH_PORT + "/NF-FG"

with open('Graphs/jolnet_isp.json') as data_file:    
    nf_fg = json.load(data_file)
    headers = {'Content-Type': 'application/json', 'X-Auth-User': username, 'X-Auth-Pass': password, 'X-Auth-Tenant': tenant}
    resp = requests.post(orchestrator, data=json.dumps(nf_fg), headers=headers)

try:
    print "Response code by service layer: "+str(resp.status_code)
    resp.raise_for_status()
except:
    print "ERROR - User "+username+" is NOT correctly instantiated"
    sys.exit()
print "User "+username+" is now correctly instantiated"