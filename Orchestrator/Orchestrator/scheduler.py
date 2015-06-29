'''
Created on Oct 1, 2014

@author: fabiomignini
''''''
Created on 30/mag/2014

@author: fabiomignini
'''
from Orchestrator.ComponentAdapter.Openstack.heat import HeatOrchestrator
from Orchestrator.ComponentAdapter.Jolnet.jolnet import JolnetAdapter
from Orchestrator.ComponentAdapter.Unify.unify import UnifyCA
from Common.config import Configuration
from Common.SQL.node import Node
from Common.SQL.graph import Graph

import logging




def Schedule(session_id, nffg):
    '''
    Method that create a concrete instance of the orchestrator
    '''
    node = Node().getNodeFromIPAddress(checkEndpointLocation(nffg))
    changeAvialabilityZone(nffg, Node().getAvailabilityZone(node.id))
    
    if node.type == "HeatCA" or node.type == "OpenStack_compute":
        node_endpoint = findNode("HeatCA", node)
        orchestratorCA_instance = HeatOrchestrator(session_id)
    elif node.type == "Jolnet":
        node_endpoint = node.ip_ddress
        orchestratorCA_instance = JolnetAdapter(session_id)
    elif node.type == "UnifiedNode":
        node_endpoint = node.ip_ddress
        endpoints = Configuration().UNIFY_ENDPOINTS
        endpoints = endpoints.split(',')
        
        if endpoints[0] is not None:
            pass
        else:
            logging.error("No Unify endpoint found")
        if len(endpoints) > 1:
            logging.warning("Only first unify endpoint is used")
            
        core_port = Configuration().EGRESS_PORT
        if core_port is not None:
            # endpoints[0] is the url of the UN
            orchestratorCA_instance = UnifyCA(session_id);
        else: 
            logging.error("No core port defined")
        
    else:
        logging.error("Driver not supported: "+node.type)
        raise
    
    # TODO: qui il grafo non esiste ancora
    # Set n the db the node chose for instantiate the nffg
    Graph().setNodeID(session_id, node.id)
    
        
    return orchestratorCA_instance, node_endpoint


def changeAvialabilityZone(nffg, avialability_zone):
    for vnf in nffg.listVNF:
        vnf.availability_zone = avialability_zone

def checkEndpointLocation(nffg):
    '''
    Define the node where to instantiate the nffg.
    Returns the ip address of the node
    '''
    for endpoint in nffg.listEndpoint:
        if endpoint.node is not None:
            return endpoint.node

def findNode(component_adapter, node = None):
    #  In this research the openstack compute nodes do not should be taken in account
    # Get node belonging to the component_adapter passed
    if node is not None:
        node = Node().getNode(node.controller_node)
    
    return node.ip_address

def Select(session_id, node, nffg):
    
    '''
    the nffg will be instantiated in the node where the user is connected, 
    independently of where the nffg is currently instantiated 
    '''
    
    new_node = Node().getNodeFromIPAddress(checkEndpointLocation(nffg))
    
    component_adapter = Node().getComponentAdapter(Node().getNodeFromIPAddress(new_node.ip_address).id)
    
    logging.debug("Component adapter used to delete the nffg: "+str(component_adapter))
    
    if node.type == "HeatCA" or node.type == "OpenStack_compute":
        node_endpoint = findNode("HeatCA", node)
        orchestratorCA_instance = HeatOrchestrator(session_id)
    if component_adapter == 'UnifiedNode':
        endpoints = Configuration().UNIFY_ENDPOINTS
        endpoints = endpoints.split(',')
        
        if endpoints[0] is not None:
            pass
        else:
            logging.error("No Unify endpoint found")
        if len(endpoints) > 1:
            logging.warning("Only first  unify endpoint is used")
            
        core_port = Configuration().EGRESS_PORT
        if core_port is not None:
            orchestratorCA_instance = UnifyCA(endpoints[0], core_port);
        else: 
            logging.error("No core port defined")
            raise
    if component_adapter == 'Jolnet':
        orchestratorCA_instance = JolnetAdapter(session_id)
    
    
    
    return orchestratorCA_instance, node_endpoint

def GetInstance(node, session_id):
    if node.type == "HeatCA" or node.type == "OpenStack_compute":
        orchestratorCA_instance = HeatOrchestrator(session_id)
    elif node.type == "Jolnet":
        orchestratorCA_instance = JolnetAdapter(session_id)
    elif node.type == "UnifiedNode":
        node_endpoint = node.ip_ddress
        endpoints = Configuration().UNIFY_ENDPOINTS
        endpoints = endpoints.split(',')
        
        if endpoints[0] is not None:
            pass
        else:
            logging.error("No Unify endpoint found")
        if len(endpoints) > 1:
            logging.warning("Only first unify endpoint is used")
            
        core_port = Configuration().EGRESS_PORT
        if core_port is not None:
            # endpoints[0] is the url of the UN
            orchestratorCA_instance = UnifyCA(endpoints[0], core_port);
        else: 
            logging.error("No core port defined")
        
    else:
        logging.error("Driver not supported: "+node.type)
        raise
    return orchestratorCA_instance
