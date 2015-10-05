'''
Created on Oct 1, 2014

@author: fabiomignini
''''''
Created on 30/mag/2014

@author: fabiomignini
'''
from Orchestrator.ComponentAdapter.Openstack.openstack import HeatOrchestrator
from Orchestrator.ComponentAdapter.Jolnet.jolnet import JolnetAdapter
from Orchestrator.ComponentAdapter.Unify.unify import UnifyCA
from Orchestrator.ComponentAdapter.OpenstackCommon.authentication import KeystoneAuthentication
from Common.SQL.node import Node
from Common.SQL.graph import Graph

import logging

class Scheduler(object):
    
    def __init__(self, session_id, userdata):
        self.session_id = session_id
        self.userdata = userdata
    
    def schedule(self, nffg):      
        
        node = Node().getNodeFromDomainID(self.checkEndpointLocation(nffg))
        self.changeAvailabilityZone(nffg, Node().getAvailabilityZone(node.id))
        
        orchestratorCA_instance, node_endpoint = self.getInstance(node)
        
        # Set n the db the node chose for instantiate the nffg
        Graph().setNodeID(self.session_id, node.id)
        
        return orchestratorCA_instance, node_endpoint
    
    def getInstance(self, node):
        token = None
        if node.type == "HeatCA" or node.type == "OpenStack_compute":
            node_endpoint = self.findNode("HeatCA", node)
            #TODO: modify HeatCA constructor to get userdata instead of token (like JolnetCA)
            orchestratorCA_instance = HeatOrchestrator(self.session_id, self.userdata, node)
        elif node.type == "JolnetCA":
            node_endpoint = node.domain_id
            orchestratorCA_instance = JolnetAdapter(self.session_id, self.userdata, node)
        elif node.type == "UniversalNodeCA":
            node_endpoint = node.domain_id
            orchestratorCA_instance = UnifyCA(self.session_id);
        else:
            logging.error("Driver not supported: "+node.type)
            raise
        return orchestratorCA_instance, node_endpoint

    def changeAvailabilityZone(self, nffg, availability_zone):
        for vnf in nffg.listVNF:
            vnf.availability_zone = availability_zone
    
    def checkEndpointLocation(self, nffg):
        '''
        Define the node where to instantiate the nffg.
        Returns the ip address of the node
        '''
        node = None
        for endpoint in nffg.listEndpoint:
            if endpoint.node is not None:
                node = endpoint.node
                break
        if node is None:
            node = Node().getInstantiationNode().domain_id
        return node
    
    def findNode(self, component_adapter, node = None):
        #  In this research the openstack compute nodes do not should be taken in account
        # Get node belonging to the component_adapter passed
        if node is not None:
            node = Node().getNode(node.controller_node)
        
        return node.domain_id

