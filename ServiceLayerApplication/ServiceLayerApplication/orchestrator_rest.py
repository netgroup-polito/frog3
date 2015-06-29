'''
Created on Jun 24, 2015

@author: fabiomignini
'''
import logging
import requests
import json
from Common.config import Configuration

class GlobalOrchestrator(object):
    

    timeout = Configuration().ORCH_TIMEOUT
        
    def __init__(self, token, ip, port):
        self.ip = ip
        self.port = port
        self.token = token
        self.base_url = "http://"+str(ip)+":"+str(port)
        self.put_url = self.base_url+"/NF-FG"
        self.delete_url = self.base_url+"/NF-FG/%s"
        self.get_url = self.base_url+"/NF-FG/%s"   
        
    def get(self, nffg_id):
        headers = {'Content-Type': 'application/json', "cache-control": "no-cache", 'X-Auth-Token': self.token}
        resp = requests.get(self.get_url % (nffg_id), headers=headers, timeout=long(self.timeout))
        resp.raise_for_status()
        return resp.text
        
    def put(self, nffg):
        headers = {'Content-Type': 'application/json', "cache-control": "no-cache", 'X-Auth-Token': self.token}
        logging.debug("Orchestrator url: "+self.put_url)
        resp = requests.put(self.put_url, data = json.dumps(nffg), headers=headers, timeout=long(self.timeout))
        resp.raise_for_status()
        logging.debug("Put completed")
        return resp.text
    
    def delete(self, nffg_id):
        headers = {'Content-Type': 'application/json', "cache-control": "no-cache", 'X-Auth-Token': self.token}
        resp = requests.delete(self.delete_url % (nffg_id), headers=headers, timeout=long(self.timeout))
        resp.raise_for_status()
        logging.debug("Delete completed")
        return resp.text
        
    def checkNFFG(self, nffg_id):
        self.get(nffg_id)
        logging.debug("Check completed")
        response = {}
        response['status']='CREATE_COMPLETE'
        return response
        