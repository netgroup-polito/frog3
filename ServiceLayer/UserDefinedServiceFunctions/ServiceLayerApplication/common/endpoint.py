'''
Created on Feb 15, 2015

@author: fabiomignini
'''
import logging
from Common.NF_FG.nf_fg_managment import NF_FG_Management
from Common.config import Configuration
from Common.SQL.node import Node

ISP_INGRESS = Configuration().ISP_INGRESS
ISP_EGRESS = Configuration().ISP_EGRESS
CONTROL_INGRESS = Configuration().CONTROL_INGRESS
USER_INGRESS = Configuration().USER_INGRESS

INGRESS_PORT = Configuration().INGRESS_PORT
INGRESS_TYPE = Configuration().INGRESS_TYPE
EGRESS_PORT = Configuration().EGRESS_PORT
EGRESS_TYPE = Configuration().EGRESS_TYPE


class Endpoint(object):
    def __init__(self, nf_fg):
        self.nf_fg = nf_fg
    
    def connectEndpointSwitchToVNFs(self):
        manage = NF_FG_Management(self.nf_fg)
            
        for endpoint in self.nf_fg.listEndpoint:
            if endpoint.name == CONTROL_INGRESS or endpoint.name == ISP_INGRESS:
                manage.connectEndpointSwitchToVNF(endpoint)
                
    def characterizeEndpoint(self, user_id = None):
        # Characterize INGRESS endpoint
        for endpoint in self.nf_fg.listEndpoint:
            # Connects directly vnf with endpoint_switch, that means get rid of egress_endpoint           
            if endpoint.name == ISP_EGRESS:
                endpoint.type = EGRESS_TYPE
                endpoint.interface = EGRESS_PORT
                logging.debug("NF-FG name: "+self.nf_fg.name)
                logging.debug("endpoint name: "+endpoint.name)
                self.nf_fg.characterizeEndpoint(endpoint, endpoint_type = endpoint.type, interface = endpoint.interface)
                endpoint.attached = True
            if endpoint.name == USER_INGRESS:
                endpoint.type = INGRESS_TYPE
                endpoint.interface = INGRESS_PORT
                if user_id is not None:
                    endpoint.node = Node().getNodeDomainID(Node().getUserLocation(user_id))
                logging.debug("NF-FG name: "+self.nf_fg.name)
                logging.debug("endpoint name: "+endpoint.name)
                self.nf_fg.characterizeEndpoint(endpoint, endpoint_type = endpoint.type, interface = endpoint.interface)
                endpoint.attached = True
