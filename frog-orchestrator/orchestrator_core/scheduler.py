'''
Created on Oct 1, 2014

@author: fabiomignini
'''
from orchestrator_core.component_adapter.openstack_plus.controller import OpenStackPlusOrchestrator
from orchestrator_core.component_adapter.jolnet.controller import JolnetAdapter
from orchestrator_core.component_adapter.unify.controller import UnifyCA
from orchestrator_core.exception import NodeNotFound
from orchestrator_core.sql.node import Node
from orchestrator_core.sql.graph import Graph

import logging

class Scheduler(object):
    
    def __init__(self, graph_id, userdata):
        self.graph_id = graph_id
        self.userdata = userdata
    
    def schedule(self, nffg):      
        node = Node().getNodeFromDomainID(self.checkEndpointLocation(nffg))
        self.changeAvailabilityZone(nffg, Node().getAvailabilityZone(node.id))
        
        orchestratorCA_instance = self.getInstance(node)
        return orchestratorCA_instance, node
        
    def getInstance(self, node):
        if node.type == "OpenStack+CA" or node.type == "OpenStack+_compute":
            orchestratorCA_instance = OpenStackPlusOrchestrator(self.graph_id, self.userdata)
        elif node.type == "JolnetCA":
            orchestratorCA_instance = JolnetAdapter(self.graph_id, self.userdata)
        elif node.type == "UniversalNodeCA":
            orchestratorCA_instance = UnifyCA(self.graph_id, node.domain_id, self.userdata);
        else:
            logging.error("Driver not supported: "+node.type)
            raise
        return orchestratorCA_instance

    def changeAvailabilityZone(self, nffg, availability_zone):
        for vnf in nffg.vnfs:
            vnf.availability_zone = availability_zone
    
    def checkEndpointLocation(self, nffg):
        '''
        Define the node where to instantiate the nffg
        '''
        node = None
        for end_point in nffg.end_points:
            if end_point.node is not None:
                node = end_point.node
                break
            elif end_point.switch_id is not None:
                node = end_point.switch_id
                break
        if node is None:
            raise NodeNotFound("Unable to determine where to place this graph (endpoint.node or endpoint.switch_id missing)")
        return node
