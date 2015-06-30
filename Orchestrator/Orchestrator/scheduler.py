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
from Common.SQL.node import Node
from Common.SQL.graph import Graph

import logging

class Scheduler(object):
    
    def __init__(self, session_id):
        self.session_id = session_id
    
    def schedule(self, nffg):
        
        node = Node().getNodeFromDomainID(self.checkEndpointLocation(nffg))
        self.changeAvialabilityZone(nffg, Node().getAvailabilityZone(node.id))
        
        orchestratorCA_instance, node_endpoint = self.getInstance(node)
        
        # Set n the db the node chose for instantiate the nffg
        Graph().setNodeID(self.session_id, node.id)
        return orchestratorCA_instance, node_endpoint
    
    def getInstance(self, node):
        if node.type == "HeatCA" or node.type == "OpenStack_compute":
            node_endpoint = self.findNode("HeatCA", node)
            orchestratorCA_instance = HeatOrchestrator(self.session_id)
        elif node.type == "JolnetCA":
            node_endpoint = node.ip_ddress
            orchestratorCA_instance = JolnetAdapter(self.session_id)
        elif node.type == "UniversalNodeCA":
            node_endpoint = node.ip_ddress
            orchestratorCA_instance = UnifyCA(self.session_id);
        else:
            logging.error("Driver not supported: "+node.type)
            raise
        return orchestratorCA_instance, node_endpoint

    def changeAvialabilityZone(self, nffg, avialability_zone):
        for vnf in nffg.listVNF:
            vnf.availability_zone = avialability_zone
    
    def checkEndpointLocation(self, nffg):
        '''
        Define the node where to instantiate the nffg.
        Returns the ip address of the node
        '''
        for endpoint in nffg.listEndpoint:
            if endpoint.node is not None:
                return endpoint.node
    
    def findNode(self, component_adapter, node = None):
        #  In this research the openstack compute nodes do not should be taken in account
        # Get node belonging to the component_adapter passed
        if node is not None:
            node = Node().getNode(node.controller_node)
        
        return node.domain_id

