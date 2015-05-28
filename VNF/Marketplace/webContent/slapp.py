'''
Created on May 19, 2015

@author: fabiomignini
'''
from constants import TIMEOUT, SERVICE_LAYER
import requests
import json
import logging
from exception import Unauthorized

def instantiate(token):
    request_body = {"session":{"session_param" : {}}} 
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
    resp = requests.put(SERVICE_LAYER, headers=headers, data=json.dumps(request_body), timeout=(TIMEOUT*8))
    if resp.status_code == 401:
        logging.error("Orchestrator returns 401 unauthorized")
        raise Unauthorized('Keystone returns 401 Unauthorized')
    resp.raise_for_status()

def delete(token):
    request_body = {"session":{"session_param" : {}}} 
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
    resp = requests.delete(SERVICE_LAYER, headers=headers, data=json.dumps(request_body), timeout=(TIMEOUT*8))
    if resp.status_code == 401:
        logging.error("Orchestrator returns 401 unauthorized")
        raise Unauthorized('Keystone returns 401 Unauthorized')
    resp.raise_for_status()
