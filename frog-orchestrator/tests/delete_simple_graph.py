'''
Created on Oct 23, 2015

@author: fabiomignini
'''
import requests, json

orchestrator_endpoint = "http://127.0.0.1:9000/NF-FG/00000001"
username = 'demo'
password = 'stack'
tenant = 'demo'
headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 
           'X-Auth-User': username, 'X-Auth-Pass': password, 'X-Auth-Tenant': tenant}
requests.delete(orchestrator_endpoint, headers=headers)
print 'Job completed'