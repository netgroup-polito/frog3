'''
Created on May 14, 2015

@author: fabiomignini
'''
from constants import *
import json
import requests
from slapp import instantiate, delete
import logging
from requests.exceptions import Timeout
from exception import Unauthorized



global_match_id = 0
default_priority = "10"
ingress_endpoint = 'user_ingress'
egress_endpoint = 'user_egress'
ingress_port_id = "User:0"
egress_port_id = "WAN:0"
switch_ingress_port = "L2Port:0"
switch_egress_port = "L2Port:1"

class Node(object):
    def __init__(self, node_type, node_id, port_id = None):
        self.node_type = node_type
        self.node_id = node_id
        self.port_id = port_id
        
    def isVNF(self):
        if self.node_type == 'vnf':
            return True
        return False
    
    def isLAN(self):
        if self.node_type == 'lan':
            return True
        return False
    
    def isTrafficSplitter(self):
        if self.node_type == 'splittermerger':
            return True
        return False
        
    def isEndpoint(self):
        if self.node_type == 'endpoint':
            return True
        return False
        
    def setAsVNF(self):
        self.node_type = 'vnf'



def setFlowruleFromEndpoint(endpoint_id, match_id, vnf, port, priority=None):
    flowrule = {}
    flowrule['action'] = {}
    flowrule['action']['VNF'] = {}
    flowrule['action']['VNF']['id'] = vnf
    flowrule['action']['VNF']['port'] = port
    flowrule['action']['type'] =  "output"
    flowrule['flowspec'] = {}
    flowrule['flowspec']['matches'] = []
    match = {}
    if priority is None:
        match['priority'] = default_priority
    else:
        match['priority'] = priority
    match['id'] = match_id
    flowrule['flowspec']['matches'].append(match)
    flowrule['flowspec']['ingress_endpoint'] = endpoint_id
    return flowrule

def setFlowruleToEndpoint(endpoint_id, match_id, priority=None):
    flowrule = {}
    flowrule['action'] = {}
    flowrule['action']['endpoint'] = {}
    flowrule['action']['endpoint']['id'] = endpoint_id
    flowrule['action']['type'] =  "output"
    flowrule['flowspec'] = {}
    flowrule['flowspec']['matches'] = []
    match = {}
    if priority is None:
        match['priority'] = default_priority
    else:
        match['priority'] = priority
    match['id'] = match_id
    flowrule['flowspec']['matches'].append(match)
    return flowrule

def setFlowruleToVNF(output_vnf, output_port, match_id, flowspec=None):
    flowrule = {}
    flowrule['action'] = {}
    flowrule['action']['VNF'] = {}
    flowrule['action']['VNF']['id'] = output_vnf
    flowrule['action']['VNF']['port'] = output_port
    flowrule['action']['type'] =  "output"
    flowrule['flowspec'] = {}
    flowrule['flowspec']['matches'] = []
    match = {}
    
    match['priority'] = default_priority
    
    match['id'] = match_id
    flowrule['flowspec']['matches'].append(match)
    return flowrule
  
def createFlowrule(node_a, node_b, vnf_id, port_id, outgoing_flowrules_obj, ingoing_flowrules_obj):
    # Warning: in the NFFG in use, can't be directly connected two end-points
    global global_match_id
    if node_a.isVNF() and node_a.node_id == vnf_id and node_a.port_id == port_id:
        if node_b.isVNF():
            # TODO: match id
            outgoing_flowrules_obj.append(setFlowruleToVNF(node_b.node_id, str(node_b.port_id), str(global_match_id)))
            global_match_id = global_match_id +1
        if node_b.isEndpoint():
            # TODO: match id
            outgoing_flowrules_obj.append(setFlowruleToEndpoint(node_b.node_id, str(global_match_id)))
            global_match_id = global_match_id +1
            ingoing_flowrules_obj.append(setFlowruleFromEndpoint(node_b.node_id, str(global_match_id), node_a.node_id,  str(node_a.port_id)))
            global_match_id = global_match_id +1
        
def createGraph(vnf_list, user_id, encode=True):    
    # TODO: if no one vnfs in list, I should add a switch default vm
    nffg = {}
    nffg['profile'] = {}
    nffg['profile']['id'] = user_id
    nffg['profile']['name'] = user_id
    vnfs = []
    for index, vnf in enumerate(vnf_list):
        if vnf['psa_id'] == "switch":
            _ingress_port_id = switch_ingress_port
            _egress_port_id = switch_egress_port
        else:
            _ingress_port_id = ingress_port_id
            _egress_port_id = egress_port_id
        
        vnf_obj = {}
        vnf_obj['vnf_descriptor'] = vnf['psa_id']+'.json'
        vnf_obj['id'] = vnf['psa_id']
        vnf_obj['name'] = vnf['psa_id']
        vnf_obj['ports'] = []
        if index == 0:
            port_obj = {}
            port_obj['id'] = _ingress_port_id
            outgoing_flowrules_obj = []
            ingoing_flowrules_obj = []
            node1 = Node('endpoint', ingress_endpoint)
            node2 = Node('vnf', vnf['psa_id'], _ingress_port_id)
        else:
            port_obj = {}
            port_obj['id'] = _ingress_port_id
            outgoing_flowrules_obj = []
            ingoing_flowrules_obj = []
            node1 = Node('vnf', vnf_list[index-1]['psa_id'], _egress_port_id)
            node2 = Node('vnf', vnf['psa_id'], _ingress_port_id)
            
        createFlowrule(node1, node2, vnf['psa_id'], _ingress_port_id, outgoing_flowrules_obj, ingoing_flowrules_obj)
        createFlowrule(node2, node1, vnf['psa_id'], _ingress_port_id, outgoing_flowrules_obj, ingoing_flowrules_obj)
        if len(outgoing_flowrules_obj) != 0:
                port_obj['outgoing_label'] = {}
                port_obj['outgoing_label']['flowrules'] = outgoing_flowrules_obj
        if len(ingoing_flowrules_obj) != 0:
            port_obj['ingoing_label'] = {}
            port_obj['ingoing_label']['flowrules'] = ingoing_flowrules_obj
        vnf_obj['ports'].append(port_obj)
            
        if index == (len(vnf_list) - 1):
            port_obj = {}
            port_obj['id'] = _egress_port_id
            outgoing_flowrules_obj = []
            ingoing_flowrules_obj = []
            node1 = Node('vnf', vnf['psa_id'], _egress_port_id)
            node2 = Node('endpoint', egress_endpoint)
        else:
            port_obj = {}
            port_obj['id'] = _egress_port_id
            outgoing_flowrules_obj = []
            ingoing_flowrules_obj = []
            node1 = Node('vnf', vnf['psa_id'], _egress_port_id)
            node2 = Node('vnf', vnf_list[index+1]['psa_id'], _ingress_port_id)
            
        createFlowrule(node1, node2, vnf['psa_id'], _egress_port_id, outgoing_flowrules_obj, ingoing_flowrules_obj)
        createFlowrule(node2, node1, vnf['psa_id'], _egress_port_id, outgoing_flowrules_obj, ingoing_flowrules_obj)  
        if len(outgoing_flowrules_obj) != 0:
                port_obj['outgoing_label'] = {}
                port_obj['outgoing_label']['flowrules'] = outgoing_flowrules_obj
        if len(ingoing_flowrules_obj) != 0:
            port_obj['ingoing_label'] = {}
            port_obj['ingoing_label']['flowrules'] = ingoing_flowrules_obj
        vnf_obj['ports'].append(port_obj)
        
        vnfs.append(vnf_obj)
    nffg['profile']['VNFs'] = vnfs
    endpoints = []
   
    # End points
    endpoint_obj = {}
    endpoint_obj['id'] = ingress_endpoint
    endpoint_obj['name'] = 'INGRESS'
    endpoints.append(endpoint_obj)
    endpoint_obj = {}
    endpoint_obj['id'] = egress_endpoint
    endpoint_obj['name'] = 'EGRESS'
    endpoints.append(endpoint_obj)
    
    nffg['profile']['endpoints'] = endpoints
    if encode:
        return json.dumps(nffg, sort_keys=True).encode()
    else:
        return nffg

def putServiceGraphInKeystone(token, user_id, graph):
    data = json.dumps(graph)
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
    resp = requests.post(URL_SERVICE_GRAPH+user_id, headers=headers, data=data, timeout=TIMEOUT)
    if resp.status_code == 401:
        logging.error("Keystone returns 401 unauthorized")
        raise Unauthorized('Keystone returns 401 Unauthorized')
    resp.raise_for_status()
    return resp.text

def waitInstantiation(token=None):
    try:
        while True:
            headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
            resp = requests.get(SERVICE_LAYER, headers=headers, timeout=(TIMEOUT))
            if resp.status_code == 201:
                break
            elif resp.status_code == 202:
                continue
            elif resp.status_code == 401:
                logging.error("Orchestrator returns 401 unauthorized")
                raise Unauthorized('Orchestrator returns 401 Unauthorized')
            else:
                logging.error('Orchestrator returns '+resp.status_code)
                raise
    except Timeout as err:
        logging.error("Orchestrator request timeout")
        raise err
          
def saveAndInstantiateServiceGraph(session, vnfs):
    '''
    Crate a Service graph for a user, and trigger the instantiation of it in the SLApp
    '''
    
    # Create a list of selected app
    active_vnfs = []
    for vnf in vnfs['list']:
        if vnf['checked'] == 1:
            active_vnfs.append(vnf)
        
    
    if len(active_vnfs) == 0:
        psa = {}
        psa['psa_name'] = "switch"
        psa['psa_id'] = "switch"
        active_vnfs.append(psa)
        
        graph = createGraph(active_vnfs, vnfs['user'], False)
        
        # Put the service graph in keystone
        putServiceGraphInKeystone(session['token'], session['user_id'], graph)  
        
        instantiate(session['token'])
        #delete(session['token'])
    else:
        graph = createGraph(active_vnfs, vnfs['user'], False)
        
        # Put the service graph in keystone
        putServiceGraphInKeystone(session['token'], session['user_id'], graph)  
        logging.debug("Service graph stored in keystone: "+json.dumps(graph))
        
        # Call the service layer application to instantiate the user profile
        instantiate(session['token'])
        
        waitInstantiation(session['token'])
        
        logging.debug("Service graph instantiated")
        




    