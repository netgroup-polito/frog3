'''
Created on Oct 1, 2014

@author: fabiomignini
'''
import logging
import json
import cPickle as pickle

from Common.users import User
from Common.authentication import KeystoneAuthentication
from Common.ServiceGraph.keystone import KeystoneProfile
from Common.NF_FG.nf_fg import NF_FG
from Common.config import Configuration
from Common.exception import Wrong_ISP_Graph
from Common.NF_FG.nf_fg_managment import NF_FG_Management
from ServiceLayerApplication.common.user_session import UserSession
from ServiceLayerApplication.common.endpoint import Endpoint


UNIFY_NUM_ENDPOINTS = Configuration().UNIFY_NUM_ENDPOINTS
INGRESS_PORT = Configuration().INGRESS_PORT
INGRESS_TYPE = Configuration().INGRESS_TYPE
EGRESS_PORT = Configuration().EGRESS_PORT
EGRESS_TYPE = Configuration().EGRESS_TYPE
ISP_EGRESS = Configuration().ISP_EGRESS
USER_EGRESS = Configuration().USER_EGRESS

# End-points type
ISP_INGRESS = Configuration().ISP_INGRESS
CONTROL_INGRESS = Configuration().CONTROL_INGRESS

class ISP(object):
    
    def __init__(self, keystone_server, ISP_username, ISP_password, ISP_tenant_name, ISP_email, ISP_description, ISP_role_name, orch_username, orch_password, orch_tenant):
        self.keystone_server = keystone_server
        self.ISP_username = ISP_username
        self.ISP_password = ISP_password
        self.ISP_tenant_name = ISP_tenant_name
        self.ISP_email = ISP_email
        self.ISP_description = ISP_description
        self.ISP_role_name = ISP_role_name
        
        self.orch_username = orch_username
        self.orch_tenant = orch_tenant
        self.orch_password = orch_password
        
        self.sw_endpoint = Configuration().SW_ENDPOINT
        
    def createISPTenant(self, user):
        if user.controlTenant() == False:
            user.creatTenant()
            logging.debug("ISP - Instantiate ISP - CREATE TENANT");
        else:
            logging.debug("ISP - Instantiate ISP - TENANT ALREADY EXISTENT");
    
    def createISPUser(self, user):
        if user.controlUser()== False:
            user.createAndLinkUserTenatRole()
            logging.debug("ISP - Instantiate ISP - CREATE USER");
        else:
            logging.debug("ISP - Instantiate ISP - USER ALREADY EXISTENT");
    
    def controlISPProfile(self, ISP_id, ISP_token):
        logging.debug("ISP - User ID: "+ISP_id)
        if KeystoneProfile(self.keystone_server, ISP_id).check(ISP_token) == False:
            
            logging.debug("ISP - CREATE GRAPH IN DATABASE")
            
            # If ISP's graph already exists, we update it, otherwise we create it
            json_data=open("isp_graph.json").read()
            graph = json.loads(json_data)
            #logging.debug("ISP graph - "+json.dumps(graph))

            #  Create ISP profile with json taken into "ISP.json" file
            KeystoneProfile(self.keystone_server, ISP_id).post(ISP_token, json.dumps(graph))
        else:
            logging.debug("ISP - Graph - GRAPH ALREADY EXISTENT")
            
    def addControlNetwork(self, nf_fg, manage):
        logging.debug('ISP - Adding controll network')
        for vnf in nf_fg.listVNF:
            #logging.info("Nobody - Control vnf : "+vnf.name)
            
            need_control_net, port = manage.checkIfControlNetIsNedeed(vnf)
            #logging.info("Nobody - Control port")
            
            if need_control_net is True:
                logging.info(port.id)
                manage.addToControlNet(vnf, port, CONTROL_INGRESS)
                
    def createControlNetwork(self, nf_fg):
        if nf_fg.control_switch_label is False:
            nf_fg.addControlSwitch()
            logging.debug("rete di controllo: "+CONTROL_INGRESS)
            user_control_egress  = self.createEndpoint(CONTROL_INGRESS)
            port = self.addPortToSwitch(self.control_switch)
            port.setFlowRuleToEndpoint(user_control_egress.id)
            port.setFlowRuleFromEndpoint(self.control_switch.id, user_control_egress.id)
    
    def addEgressSwitch(self, nf_fg):
        port_e = nf_fg.addPortToSwitch(nf_fg.control_switch)
        egress_sw = nf_fg.getVNFByID("Exit_Switch")
        port_egress = nf_fg.addPortToSwitch(egress_sw)
        port_e.setFlowRuleToVNF(egress_sw.id, port_egress.id)
        port_egress.setFlowRuleToVNF(nf_fg.control_switch.id, port_e.id)
    
    def addEdgeEndpointToISP(self, nf_fg, endpoint_switch, endpoint_id = None):
        index = 0
        while index < UNIFY_NUM_ENDPOINTS:
            if endpoint_id is not None:
                edge_endpoint = nf_fg.createEndpoint(str(endpoint_id)+"_EDGE_ENDPOINT", True)
            else:
                edge_endpoint = nf_fg.createEndpoint("EDGE_ENDPOINT")
            #logging.debug(endpoint_switch)

            port = nf_fg.addPortToSwitch(endpoint_switch)
            port.setFlowRuleToEndpoint(edge_endpoint.id)
            port.setFlowRuleFromEndpoint(endpoint_switch.id, edge_endpoint.id)
            index = index + 1             
        
    def instatiateISP(self):
        
        user = User(self.keystone_server, self.ISP_username, self.ISP_password, self.ISP_tenant_name, self.ISP_email, self.ISP_description, self.ISP_role_name)

        # If ISP tenant doesn't exist, we create it!
        self.createISPTenant(user)
        
        # If ISP user in ISP tenant doesn't exist, we create it!
        self.createISPUser(user)
        
        # Obtain ISP's id
        ISP_id = user.get_user_id()
        
        #Get orchestrator token 
        orchestrator_token = KeystoneAuthentication(self.keystone_server, self.orch_tenant, self.orch_username, self.orch_password).get_token()
        
        # Get ISP token 
        ISP = KeystoneAuthentication(self.keystone_server,self.ISP_tenant_name,self.ISP_username, self.ISP_password)
        ISP_token = ISP.get_token()
        
        # Control if ISP user already have a profile in db
        self.controlISPProfile(ISP_id, ISP_token)      
            
        # Retrieve the user profile
        profile = KeystoneProfile(self.keystone_server, ISP_id)
        graph = profile.get(ISP_token)['profile']['graph']
                
        # TODO: Transform profile in NF_FG
        nf_fg = NF_FG(graph)
        manage = NF_FG_Management(nf_fg, ISP_token) 
        
        # Add control network
        self.addControlNetwork(nf_fg, manage)
        
        # Create control network even if no one vnfs have a control interface.
        self.createControlNetwork(nf_fg)

        # Add egress switch
        self.addEgressSwitch(nf_fg)
        
        '''
        #port_e.setFlowRuleToEndpoint(egress_sw.id)
        #port_e.setFlowRuleFromEndpoint(c_switch.id, egress_sw.id)
        '''
        
        
        
        # Create endpoint switch
        endpoint_switch_control = nf_fg.addEndpointSwitch(CONTROL_INGRESS)
        endpoint_switch = nf_fg.addEndpointSwitch(ISP_INGRESS)
        
        # Add an arbitrary number of endpoints connected to endpoint_switch. Only if the nf-fg is not yet deployed
        self.addEdgeEndpointToISP(nf_fg, endpoint_switch_control, CONTROL_INGRESS)
        self.addEdgeEndpointToISP(nf_fg, endpoint_switch, ISP_INGRESS)
        
        # Characterize endpoint
        Endpoint(nf_fg).characterizeEndpoint()
        Endpoint(nf_fg).connectEndpointSwitchToVNFs()
        
        # Control if the graph is already instantiate
        logging.debug("ISP - Deploy of ISP's graph")
        logging.debug("ISP - ISP's graph - "+nf_fg.getJSON())
        if UserSession(ISP_id, ISP).checkSession() == False: 
            logging.debug("ISP - ISP graph - INSTANTIATE GRAPH")
            # Instantiate nobody graph (call put function in Controller)
            #controller = UpperLayerOrchestratorController(self.keystone_server, orchestrator_token,"Nobody", ISP_token)
            #controller.put(json.loads(nf_fg.getJSON()))
        else:
            logging.debug("ISP - ISP graph - GRAPH ALREADY INSTANTIATED")