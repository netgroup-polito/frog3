'''
Created on Feb 15, 2015

@author: fabiomignini
'''
import logging, json
from service_layer_application_core.nffg_manager import NFFG_Manager
from service_layer_application_core.config import Configuration
from service_layer_application_core.sql.node import Node

ISP_INGRESS = Configuration().ISP_INGRESS
ISP_EGRESS = Configuration().ISP_EGRESS
CONTROL_INGRESS = Configuration().CONTROL_INGRESS
USER_INGRESS = Configuration().USER_INGRESS
CONTROL_EGRESS = Configuration().CONTROL_EGRESS

INGRESS_PORT = Configuration().INGRESS_PORT
INGRESS_TYPE = Configuration().INGRESS_TYPE
EGRESS_PORT = Configuration().EGRESS_PORT
EGRESS_TYPE = Configuration().EGRESS_TYPE

ISP = Configuration().ISP


class Endpoint(object):
    def __init__(self, nffg):
        self.nffg = nffg
    
    def connectEndpointSwitchToVNFs(self):
        manage = NFFG_Manager(self.nffg)
            
        for endpoint in self.nffg.end_points:
            if endpoint.name == CONTROL_INGRESS or endpoint.name == ISP_INGRESS:
                manage.connectEndpointSwitchToVNF(endpoint)
                
    def characterizeEndpoint(self, user_id = None):
        # Characterize INGRESS endpoint
        for endpoint in self.nffg.end_points:
            # Connects directly vnf with endpoint_switch, that means get rid of egress_endpoint           
            if endpoint.name == ISP_EGRESS:
                endpoint.type = EGRESS_TYPE
                endpoint.interface = EGRESS_PORT
                if user_id is not None:
                    endpoint.node = Node().getNodeDomainID(Node().getUserLocation(user_id))
            elif endpoint.name == CONTROL_EGRESS and ISP is False:
                endpoint.type = EGRESS_TYPE
                endpoint.interface = EGRESS_PORT
                if user_id is not None:
                    endpoint.node = Node().getNodeDomainID(Node().getUserLocation(user_id))
            elif endpoint.name == USER_INGRESS:
                endpoint.type = INGRESS_TYPE
                endpoint.interface = INGRESS_PORT
                if user_id is not None:
                    endpoint.node = Node().getNodeDomainID(Node().getUserLocation(user_id))
            else:
                endpoint.type = 'internal'
            logging.debug("End-point characterized: "+json.dumps(endpoint.getDict()))
