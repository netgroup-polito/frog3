'''
Created on Oct 1, 2014

@author: fabiomignini
''''''
Created on 30/mag/2014

@author: fabiomignini
'''
from Common.config import Configuration
from Orchestrator.ComponentAdapter.Openstack.openstack import HeatOrchestrator
from Orchestrator.ComponentAdapter.Jolnet.jolnet import JolnetAdapter
from Orchestrator.ComponentAdapter.Unify.unify import UnifyCA
from Common.exception import NodeNotFound
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
        Graph().setNodeID(self.session_id, node.id)
        
        orchestratorCA_instance = self.getInstance(node)
        return orchestratorCA_instance, node
    
    def getInstance(self, node):
        if node.type == "HeatCA" or node.type == "OpenStack_compute":
            orchestratorCA_instance = HeatOrchestrator(self.session_id, self.userdata)
        elif node.type == "JolnetCA":
            orchestratorCA_instance = JolnetAdapter(self.session_id, self.userdata)
        elif node.type == "UniversalNodeCA":
            orchestratorCA_instance = UnifyCA(self.session_id);
        else:
            logging.error("Driver not supported: "+node.type)
            raise
        return orchestratorCA_instance

    def changeAvailabilityZone(self, nffg, availability_zone):
        for vnf in nffg.listVNF:
            vnf.availability_zone = availability_zone
    
    def checkEndpointLocation(self, nffg):
        '''
        Define the node where to instantiate the nffg
        '''
        node = None
        for endpoint in nffg.listEndpoint:
            if endpoint.node is not None:
                node = endpoint.node
                break
        if node is None:
            '''
            The nffg does not specify any particular node or zone 
            '''
            #TODO: mechanism to choose where to place the graph
            #node = Node().getInstantiationNode().domain_id
            raise NodeNotFound("Unable to determine where to place this graph (endpoint.node missing?)")
        return node
