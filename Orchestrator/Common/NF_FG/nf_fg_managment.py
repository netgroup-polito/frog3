'''
Created on Oct 2, 2014

@author: fabiomignini
'''
import requests
import json
import logging
import uuid
import copy
import os

from Common.Manifest.manifest import Manifest
from Common.Manifest.validator import ValidateManifest
from Common.NF_FG.validator import ValidateNF_FG
from Common.NF_FG.nf_fg import NF_FG, Match, Flowrule, VNF
from Common.config import Configuration
#from Common.SQL.session import checkSession
from Common.exception import connectionsError, NoPreviousDeviceFound

EGRESS_GRAPH_FILE = Configuration().EGRESS_GRAPH_FILE
INGRESS_GRAPH_FILE = Configuration().INGRESS_GRAPH_FILE
ISP_GRAPH_FILE = Configuration().ISP_GRAPH_FILE
TEMPLATE_SOURCE = Configuration().TEMPLATE_SOURCE
TEMPLATE_PATH = Configuration().TEMPLATE_PATH
SWITCH_NAME = Configuration().SWITCH_NAME

# End-points type
SG_USER_EGRESS = Configuration().SG_USER_EGRESS
SG_USER_INGRESS = Configuration().SG_USER_INGRESS


class NF_FG_Management(object):
    '''
    classdocs
    '''


    def __init__(self, nf_fg, token = None):
        '''
        Constructor
        '''
        self.nf_fg = nf_fg
        self.token = token     
        
    def deleteMacAddressInFlows(self, mac_address, endpoint_name):
        """
            Delete all flowrules with this 'mac_address' 
        """
        # TODO: TO GET RID OF Ingress_endpoint
        endpoint = self.nf_fg.getEndpointFromName(endpoint_name)
        logging.debug("NF_FG_Management - deleteMacAddressInFlows - mac: "+mac_address)
        
        """
        ports = self.nf_fg.getVNFPortsSendingTrafficToEndpoint("Ingress_endpoint")
        for port in ports:
            port.deleteIngoingRule("Ingress_endpoint")
            port.deleteConnectionToEndpoint("Ingress_endpoint")
        """
        ports = self.nf_fg.getVNFPortsReceivingTrafficFromEndpont(endpoint._id)
        for port in ports:
            port.deleteIngoingRuleByMac(endpoint._id, mac_address)
            #port.deleteConnectionToEndpoint("Ingress_endpoint")
        return self.nf_fg
        
        """
        self.nf_fg.listVNF
        self.nf_fg.listEndpoint
        id:Ingress_endpoint
        name:INGRESS
        """
        """
        for endpoint in profile_instantiated['profile']['endpoints']:
            if endpoint['user'] is True:
                for link in profile_instantiated['profile']['links']:
                    if "endpoint" in link['nodeA'] and link['nodeA']['endpoint'] == endpoint['id']:
                        new_ng_fg = self._deleteMacAddressInFlows(profile_instantiated, link['nodeB']['VNF'], link['nodeB']['port'], endpoint['id'], mac_address)
                        
                    elif "endpoint" in link['nodeB'] and link['nodeB']['endpoint'] == endpoint['id']:
                        new_ng_fg = self._deleteMacAddressInFlows(profile_instantiated, link['nodeA']['VNF'], link['nodeA']['port'], endpoint['id'], mac_address)
        return new_ng_fg
        """
        
    def connectEndpointSwitchToVNF(self, endpoint):
        logging.debug("NF_FG_Management - connectEndpointSwitchToVNF -NF-FG name: "+self.nf_fg.name)
        logging.debug("NF_FG_Management - connectEndpointSwitchToVNF -endpoint name: "+endpoint.name)
        logging.debug("NF_FG_Management - connectEndpointSwitchToVNF -endpoint id: "+endpoint.id)
        endpoint_switch = self.nf_fg.getEndpointSwithConnectedToEndpoint(endpoint.id)
        if endpoint_switch is None:
            logging.warning("NF_FG_Management - connectEndpointSwitchToVNF - EndpointSwitch not found")
            return
            #raise connectionsError("EndpointSwitch not found")
               
        # Add connections from EndpointSwitch to VNFs
        ports = self.nf_fg.getVNFPortsSendingTrafficToEndpoint(endpoint.id)
        vnfs_ingoing_flowrules = []
        for port in ports:
            if port.vnf_id != endpoint_switch.id:
                vnfs_ingoing_flowrules = vnfs_ingoing_flowrules + port.getIngoingFlowruleToSpecificEndpoint(endpoint.id)
    
        for port in ports:
            if port.vnf_id == endpoint_switch.id:
                switch_outgoing_flowrules = port.getVNFPortsFlowruleSendingTrafficToEndpoint(endpoint.id)
                port.list_outgoing_label = self.mergeFlowrules(switch_outgoing_flowrules, vnfs_ingoing_flowrules) 
        
        
        # Add connections from VNFs to EndpointSwitch
        switch_ingoing_flowrules = []
        for port in ports:
            if port.vnf_id == endpoint_switch.id:
                switch_ingoing_flowrules = switch_ingoing_flowrules + port.getIngoingFlowruleToSpecificEndpoint(endpoint.id)
    
        for port in ports:
            if port.vnf_id != endpoint_switch.id:
                vnfs_outgoing_flowrules = port.getVNFPortsFlowruleSendingTrafficToEndpoint(endpoint.id)
                port.list_outgoing_label = self.mergeFlowrules(vnfs_outgoing_flowrules, switch_ingoing_flowrules) 
        
        # delete ingoing rules
        for port in ports:
            port.deleteIngoingRule(endpoint.id)
    
    def getMacAddressFlows(self):
        """
        get the ingress mac address rule
        """
        mac_addresses = []
        
        ingress_endpoint = None
        # Find ingress endpoint
        for endpoint in self.nf_fg.listEndpoint:
            if endpoint.name == "INGRESS":
                ingress_endpoint = endpoint.id
        # Find flow connected to endpoint
        for vnf in self.nf_fg.listVNF:
            for port in vnf.listPort:
                new_flowrules = []
                if port.list_ingoing_label is not None:
                    for flowrule in port.list_ingoing_label:
                        new_flowrule = copy.deepcopy(flowrule)
                        if new_flowrule.flowspec['ingress_endpoint'] == ingress_endpoint:
                            for match in new_flowrule.matches:
                                if 'sourceMAC' in match.of_field:
                                    mac_addresses.append(match.of_field['sourceMAC'])
        return mac_addresses
    
    def getNewFlows(self, mac_addresses):
        flows = []
        
        ingress_endpoint = None
        # Find ingress endpoint
        for endpoint in self.nf_fg.listEndpoint:
            if endpoint.name == "INGRESS":
                ingress_endpoint = endpoint.id
        # Find flow connected to endpoint
        for vnf in self.nf_fg.listVNF:
            for port in vnf.listPort:
                new_flowrules = []
                if port.list_ingoing_label is not None:
                    for flowrule in port.list_ingoing_label:
                        new_flowrule = copy.deepcopy(flowrule)
                        if new_flowrule.flowspec['ingress_endpoint'] == ingress_endpoint:
                            for match in new_flowrule.matches:
                                found = False
                                for mac_address in mac_addresses:
                                    if 'sourceMAC' in match.of_field and match.of_field['sourceMAC'] == mac_address:
                                        found = True
                                if found is False:        
                                    flows.append(flowrule)
        return flows
        
    def addDeviceFlows(self, mac_address):
        """
        Add ingress flow for user new device
        """
        
        ingress_endpoint = None
        # Find ingress endpoint
        for endpoint in self.nf_fg.listEndpoint:
            if endpoint.name == "INGRESS":
                ingress_endpoint = endpoint.id
        # Find flow connected to endpoint
        for vnf in self.nf_fg.listVNF:
            for port in vnf.listPort:
                new_flowrules = []
                if port.list_ingoing_label is not None:
                    mac = None
                    for flowrule in port.list_ingoing_label:
                        new_flowrule = copy.deepcopy(flowrule)
                        if new_flowrule.flowspec['ingress_endpoint'] == ingress_endpoint:
                            for match in new_flowrule.matches:
                                if mac == None or mac == match.of_field['sourceMAC']:
                                    if 'sourceMAC' not in match.of_field:
                                        raise NoPreviousDeviceFound("No previous device found in this graph")
                                    mac = match.of_field['sourceMAC']
                                    match.of_field['sourceMAC'] = mac_address
                                    match._id = uuid.uuid4().hex
                                    new_flowrules.append(new_flowrule)
                    port.list_ingoing_label = port.list_ingoing_label + new_flowrules
                    
        logging.debug("ghent : "+self.nf_fg.getJSON())
    
    def setDeviceFlows(self, mac_address):
        """
        Add ingress flow for user device
        """
        
        ingress_endpoint = None
        # Find ingress endpoint
        for endpoint in self.nf_fg.listEndpoint:
            if endpoint.name == "INGRESS":
                ingress_endpoint = endpoint.id
        # Find flow connected to endpoint
        for vnf in self.nf_fg.listVNF:
            for port in vnf.listPort:
                if port.list_ingoing_label is not None:
                    for flowrule in port.list_ingoing_label:
                        if flowrule.flowspec['ingress_endpoint'] == ingress_endpoint:
                            for match in flowrule.matches:
                                match.of_field['sourceMAC'] = mac_address
                                match.of_field['id'] = uuid.uuid4().hex
    
    def getISPNF_FG(self):
        """
        Read from file ISP's nf-fg
        Returns a NF_FG Object
        """
        return self.getNF_FGFromFile(ISP_GRAPH_FILE)
        
    def getIngressNF_FG(self):
        """
        Read from file ingress nf-fg
        Returns a NF_FG Object
        """
        return self.getNF_FGFromFile(INGRESS_GRAPH_FILE)
    
    def getEgressNF_FG(self):
        """
        Read from file ingress nf-fg
        Returns a NF_FG Object
        """
        return self.getNF_FGFromFile(EGRESS_GRAPH_FILE)
        
    def getNF_FGFromFile(self, file_name):
        """
        Read from file a nf-fg
        Returns a NF_FG Object
        """
        
        json_data=open(os.path.join("Graphs", file_name)).read()
        nf_fg = json.loads(json_data)
        ValidateNF_FG(nf_fg).validate()
        return NF_FG(nf_fg)
        
    def attachIngressNF_FG(self, ingress_nf_fg):
        self.attachNF_FG( ingress_nf_fg, SG_USER_INGRESS)
        
    def attachEgressNF_FG(self, egress_nf_fg):
        self.attachNF_FG( egress_nf_fg, SG_USER_EGRESS)
        
    def attachNF_FGToISP(self, isp_token):
        
        # Check if endpoint nf-fg already instantiated
        """
        if checkSession(isp_token.get_userID(), isp_token.get_token()) is True:
            pass
        else:
            # Get ISP NF-FG
            isp_nf_fg = self.getISPNF_FG()
               
        # User nf-fg management
        user_endpoint_id = self.nf_fg.getEndpointFromName('USER_EGRESS')
        for endpoint in self.nf_fg.listEndpoint:
            if endpoint.id == user_endpoint_id:
                # TODO: Is this the right position of this information?
                endpoint.ext_nf_fg = isp_nf_fg.id
        # Create ENDPOINT SWITCH
        self.nf_fg.createEndpointSwitch(user_endpoint_id)
        
        # ISP nf-fg management
        for endpoint in isp_nf_fg.listEndpoint:
            if endpoint.id == isp_nf_fg.getEndpointFromName('USER_EGRESS'):
           
                endpoint.ext_nf_fg = self.nf_fg.id
        """    
          
    def attachNF_FG(self, nf_fg, endpoint_name):
        new_endpoint = nf_fg.getEndpointFromName(endpoint_name)
        old_endpoint = self.nf_fg.getEndpointFromName(endpoint_name)
        
        if new_endpoint is None or old_endpoint is None:
            logging.info("Nothing to attach: "+ endpoint_name)
            logging.info("Nothing to attach: "+ str(new_endpoint))
            logging.info("Nothing to attach: "+ str(old_endpoint))
            logging.info("Nothing to attach")
            return
        
        #logging.info(nf_fg.getJSON())
        # Check if there are connections between switches, in that case merge them in one
        switch = self.mergeSwitchesOfTwoGraph(nf_fg, new_endpoint, self.nf_fg, old_endpoint)
        for vnf in nf_fg.listVNF:
            logging.info("attachNF_FG - vnf: \n"+str(vnf.name))
            logging.info("attachNF_FG - vnf id: \n"+str(vnf.id))
        
        # Add connections from nf_fg to self.nf_fg
        old_ports = self.nf_fg.getVNFPortsSendingTrafficToEndpoint(old_endpoint.id)
        old_ingoing_flowrules = []
        for old_port in old_ports:
            old_ingoing_flowrules = old_ingoing_flowrules + old_port.getIngoingFlowruleToSpecificEndpoint(old_endpoint.id)
        
        new_ports = nf_fg.getVNFPortsSendingTrafficToEndpoint(new_endpoint.id)
        for new_port in new_ports:
            new_outgoing_flowrules = new_port.getVNFPortsFlowruleSendingTrafficToEndpoint(new_endpoint.id)

            new_port.list_outgoing_label = self.mergeFlowrules(new_outgoing_flowrules, old_ingoing_flowrules)  
            
        # Add connections from self.nf_fg to nf_fg
        logging.info("attachNF_FG - new_endpoint.id: "+new_endpoint.id)
        new_ports = nf_fg.getVNFPortsReceivingTrafficFromEndpont(new_endpoint.id)
        logging.info("STOP STOP")
        new_ingoing_flowrules = []
        for new_port in new_ports:
            logging.info("attachNF_FG - new_port.id: "+new_port.id)
            new_ingoing_flowrules = new_ingoing_flowrules + new_port.getIngoingFlowruleToSpecificEndpoint(new_endpoint.id)
        
        old_ports = self.nf_fg.getVNFPortsSendingTrafficToEndpoint(old_endpoint.id)
        for old_port in old_ports:
            logging.info("attachNF_FG - old_port.id: "+old_port.id)
            old_outgoing_flowrules = old_port.getVNFPortsFlowruleSendingTrafficToEndpoint(old_endpoint.id)
            old_port.list_outgoing_label = self.mergeFlowrules(old_outgoing_flowrules, new_ingoing_flowrules)  

        # TODO: add all vnf of new nf_fg in old
        for vnf in nf_fg.listVNF:  
            logging.info("nf_fg_managment - attachNF_FG - vnf attaching graph: \n"+vnf.name)              
            self.nf_fg.listVNF.append(vnf)
        for endpoint in nf_fg.listEndpoint:
            logging.info("nf_fg_managment - attachNF_FG - endpoint attaching graph: \n"+endpoint.name)
            self.nf_fg.listEndpoint.append(endpoint)
        
        # Delete the union endpoint
        self.nf_fg.deleteEndpointConnections(old_endpoint)
        self.nf_fg.deleteEndpointConnections(new_endpoint)
        self.nf_fg.listEndpoint.remove(old_endpoint)
        
        # TODO: Adjust switch ports
        if switch is not None:
            switch.deletePortsWithoutFlows()
            logging.debug("adjusting_port : pippo")
            self.nf_fg.adjustPortsOrder(switch)
        
    def mergeSwitches(self, switch_A, switch_B):
        
        #######################################################################
        # WARNING: only one switch connected to endpoint are supported        #
        #######################################################################    
        
        num_ports_switch_B = len(switch_B.listPort)
        
        # Delete connection between the two switches
        switch_B.deleteConnectionsToVNF(switch_A)
        switch_A.deleteConnectionsToVNF(switch_B)
        
        # Copy VNF connected to switch to listVNF_B
        vnfs_A = []
        for port_A in switch_A.listPort:
            ####################################################################################
            # WARNING : covers only one level of hierarchy, if the VNFs that we are going to   #
            #            select are also connected to other VNF, this code doesn't work        #
            ####################################################################################
            vnfs_A = vnfs_A + self.nf_fg.getVNFSendingTrafficToVNFPort(switch_A.id, port_A.id)
            
        # Delete switch_B from a vnf list connected to switch_A
        for vnf_A in vnfs_A:
            if vnf_A.id == switch_B.id:
                vnfs_A.remove(switch_B)
        
        # Delete Switch_A
        self.nf_fg.listVNF.remove(switch_A)
        
        # Adjust switch id in vnfA
        for vnf_A in vnfs_A:
            for port_A in vnf_A.listPort:
                for flowrule_A in port_A.list_outgoing_label:
                    if flowrule_A.action.vnf is not None and flowrule_A.action.vnf['id'] == switch_A.id:
                        flowrule_A.action.vnf['id'] = switch_B.id
                        flowrule_A.action.vnf['port'] = flowrule_A.action.vnf['port'].split(":")[0]+":"+str(int(flowrule_A.action.vnf['port'].split(":")[1])+num_ports_switch_B)
                port_A.list_ingoing_label = None
                if port_A.list_ingoing_label is not None:
                    for flowrule_A in port_A.list_ingoing_label:
                        
                        
                        flowrule_A.action.vnf['port'] = flowrule_A.action.vnf['port'].split(":")[0]+":"+str(int(flowrule_A.action.vnf['port'].split(":")[1])+num_ports_switch_B)
                        #flowrule_A.flowspec['ingress_endpoint'] = endpoint_B   
        
        # Copy switch_A ports to switch_B
        for port_A in switch_A.listPort:
            port_A._id = port_A.id.split(":")[0]+":"+str(int(port_A.id.split(":")[1])+num_ports_switch_B)
            # TODO: Manage endpoint (not union endpoint) attached to switch 
            for flowrule in port_A.list_ingoing_label:
                flowrule.action.vnf['id'] = switch_B._id
                flowrule.action.vnf['port'] = port_A._id
            
        switch_A.deletePortsWithoutFlows()
        switch_B.listPort = switch_B.listPort + switch_A.listPort  
             
        
    def mergeSwitchesOfTwoGraph(self, nf_fg_A, endpoint_A, nf_fg_B, endpoint_B):
        
        #######################################################################
        # WARNING: only one switch connected to endpoint are supported        #
        #######################################################################

        
        
        switch_A = nf_fg_A.getSwithConnectedToEndpoint(endpoint_A.id)
        switch_B  = nf_fg_B.getSwithConnectedToEndpoint(endpoint_B.id)
        
        
        if switch_A is None or switch_B is None:
            logging.info("Nothing to merge")
            return
        
        num_ports_switch_B = len(switch_B.listPort)
        

        
        
        # Copy VNF connected to switch to listVNF_B
        vnfs_A = []
        endpoints_A = []
        for port_A in switch_A.listPort:
            ####################################################################################
            # WARNING : covers only one level of hierarchy, if the VNFs that we are going to   #
            #            select are also connected to other VNF, this code doesn't work        #
            ####################################################################################
            vnfs_A = vnfs_A + nf_fg_A.getVNFSendingTrafficToVNFPort(switch_A.id, port_A.id)
            
            
            endpoints_A = endpoints_A + nf_fg_A.getEndpointsSendingTrafficToVNFPort(switch_A.id, port_A.id)
            for endpoint in endpoints_A:
                if endpoint.id == endpoint_A.id:
                    endpoints_A.remove(endpoint)
            
        # Delete Switch_A
        nf_fg_A.listVNF.remove(switch_A)
        
        # Adjust switch id in vnfA
        for vnf_A in vnfs_A:
            for port_A in vnf_A.listPort:
                for flowrule_A in port_A.list_outgoing_label:
                    if flowrule_A.action.vnf is not None and flowrule_A.action.vnf['id'] == switch_A.id:
                        flowrule_A.action.vnf['id'] = switch_B.id
                        flowrule_A.action.vnf['port'] = flowrule_A.action.vnf['port'].split(":")[0]+":"+str(int(flowrule_A.action.vnf['port'].split(":")[1])+num_ports_switch_B)
                port_A.list_ingoing_label = None
                if port_A.list_ingoing_label is not None:
                    for flowrule_A in port_A.list_ingoing_label:
                        
                        
                        flowrule_A.action.vnf['port'] = flowrule_A.action.vnf['port'].split(":")[0]+":"+str(int(flowrule_A.action.vnf['port'].split(":")[1])+num_ports_switch_B)
                        #flowrule_A.flowspec['ingress_endpoint'] = endpoint_B                            
            
        nf_fg_B.listVNF = nf_fg_B.listVNF + copy.deepcopy(vnfs_A) 
        nf_fg_B.listEndpoint = nf_fg_B.listEndpoint + copy.deepcopy(endpoints_A)

        # Copy switch_A ports to switch_B
        for port_A in switch_A.listPort:
            #  Delete flows to endpoint_A.id
            port_A.deleteConnectionToEndpoint(endpoint_A.id)
            port_A._id = port_A.id.split(":")[0]+":"+str(int(port_A.id.split(":")[1])+num_ports_switch_B)
            # Manage endpoint (not union endpoint) attached to switch 
            for flowrule in port_A.list_ingoing_label:
                flowrule.action.vnf['id'] = switch_B._id
                flowrule.action.vnf['port'] = port_A._id
            
        switch_A.deletePortsWithoutFlows()
        switch_B.listPort = switch_B.listPort + switch_A.listPort  
        
        # TODO: Adjust switch ports
        nf_fg_B.adjustPortsOrder(switch_B)
        
        # delete the switch and its connected VMs/Endpoints from nf_fg_B
        for vnf in nf_fg_A.listVNF[:]:
            for vnf_A in vnfs_A:
                if vnf.id == vnf_A.id:
                    nf_fg_A.listVNF.remove(vnf)
            if vnf.id == switch_A.id:
                nf_fg_A.listVNF.remove(vnf)
            
        for endpoint in nf_fg_A.listEndpoint[:]:
            for e_A in endpoints_A:
                if endpoint.id == e_A.id:  
                    nf_fg_A.listEndpoint.remove(endpoint)
            if endpoint.id == endpoint_A.id:
                nf_fg_A.listEndpoint.remove(endpoint)
                
        return switch_B
        
    def checkExpansion(self, manifest):
        """
        return True if the VNF is a new graph
        """
        if manifest.expandable is not None and manifest.expandable == True:
            return True
        return False
    
    def checkIfControlNetIsNedeed(self, vnf):
        manifest = self.getManigest(vnf.template)
        ValidateManifest(manifest).validate() 
        manifest = Manifest(manifest)
        
        #logging.debug('checkIfControlNetIsNedeed - id: '+vnf.template) 
        #logging.debug('checkIfControlNetIsNedeed - '+json.dumps(manifest))
        for port in manifest.ports:
            if port.label.split(":")[0] == "control":                   
                return True, self.nf_fg.addPortToVNF(vnf, port.label)
        return False, None
      
    def addManifests(self):
        expanded_list = []
        for vnf in self.nf_fg.listVNF:
            
            extended = self.addManifest(vnf, vnf.template)
            if extended is True:
                switches = self.nf_fg.getSwitches()
                for switch in switches:
                    switch.deletePortsWithoutFlows()
                    logging.debug("adjusting_port : after expansion")
                    self.nf_fg.adjustPortsOrder(switch)
                expanded_list.append(vnf)
                
        for vnf in expanded_list:
            logging.debug("remove")
            self.nf_fg.listVNF.remove(vnf)
  
    def addToControlNet(self, vnf, port_id, endpoint_name = None):
        if vnf.name != SWITCH_NAME:
            if endpoint_name is None: 
                switch = self.nf_fg.addControlSwitch()
            else:
                switch = self.nf_fg.addControlSwitch(endpoint_name)
            switch_port = self.nf_fg.addPortToSwitch(switch)
            self.nf_fg.connectTwoVNFs(switch, switch_port, vnf, port_id)
            
    def getProfile(self, uri):    
        logging.debug("NF-FG_management - getProfile - uri: "+uri)
        if TEMPLATE_SOURCE == "glance":
            return self.getImageFromGlance(uri)
        else:
            return self.getJsonFromFile(TEMPLATE_PATH, uri)
        #return self.getImageFromGlance(uri)
    
    def getManigest(self, uri):  
        logging.debug("NF-FG_management - getManigest - uri: "+uri)
        if TEMPLATE_SOURCE == "glance":
            return self.getImageFromGlance(uri)
        else:
            return self.getJsonFromFile(TEMPLATE_PATH, uri)
    
    def getJsonFromFile(self, path, filename):
        json_data=open(path+filename).read()
        return json.loads(json_data)
    
    def getImageFromGlance(self, uri):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': self.token}
        resp = requests.get(uri, headers=headers)
        resp.raise_for_status()
        return json.loads(resp.text)
        
    def addManifest(self, vnf,  uri):
        manifest = self.getManigest(uri)
        ValidateManifest(manifest).validate() 
        manifest = Manifest(manifest)
        
        if self.checkExpansion(manifest) is True:
            logging.debug("NF-FG_management - addManifest - expanded")
            profile = self.getProfile(manifest.uri)
            logging.debug("NF-FG_management - addManifest - profile: \n"+str(profile))
            self.expandNode(vnf, profile)
            extended = True
        else: 
            # TODO: check min port and max port
            
            # insert manifest in nf-fg
            vnf.manifest = manifest.getJSON()
            
            
            
            extended = False
        return extended
    
    def expandNode(self, node, manifest):
        ################################################################################################################
        ################################################################################################################
        ##############                                                                                    ##############
        ##############                                       WARNING                                      ##############
        ##############                 VM'Ports of internal graph, connected to ENDPOINTs                 ##############
        ##############                     MUST have have only link to ENDPOINTs                          ##############
        ##############                                                                                    ##############
        ################################################################################################################
        ################################################################################################################
        # TODO: Control that the port of VMs connected to ENDPOINTs of node that should be expansed have only link to Endpoints
        # if not throw NotImplemented exception
        
        # Validate profile
        ValidateNF_FG(manifest).validate()
        internal_nf_fg = NF_FG(manifest)
        
        internal_switches = []
        for internal_endpoint in internal_nf_fg.listEndpoint:
            #######################################################################
            # WARNING: only one switch connected to endpoint are supported        #
            #######################################################################
            
            # TODO: check if switch is connected to endpoint 
            internal_switch = internal_nf_fg.getSwithConnectedToEndpoint(internal_endpoint.id)
            if internal_switch is not None:                 
                internal_switches.append(internal_switch)
        
        # Add new VNFs in graph
        for internal_vnf in internal_nf_fg.listVNF:
            self.nf_fg.addVNF(internal_vnf)
             
        for endpoint_port in node.listPort:
            # Add connections from internal graph to external grap
            
            internal_ports = internal_nf_fg.getVNFPortsSendingTrafficToEndpoint(endpoint_port.id)
            for internal_port in internal_ports:
                internal_outgoing_flowrules = internal_port.getVNFPortsFlowruleSendingTrafficToEndpoint(endpoint_port.id)
                # WARNING: if the port isn't connected only on the ENDPOINT (endpoint_port) that flows will be deleted
                internal_port.list_outgoing_label = self.mergeFlowrules(internal_outgoing_flowrules, endpoint_port.flowrules)
            

            # Add connections from external graph to internal graph 
            internal_ingoing_flowrules = []
            for internal_port in internal_ports:
                internal_ingoing_flowrules = internal_ingoing_flowrules + internal_port.getIngoingFlowruleToSpecificEndpoint(endpoint_port.id)
            
            external_ports = self.nf_fg.getVNFPortsSendingTrafficToVNFPort(node.id, endpoint_port.id)
            for external_port in external_ports:
                external_outgoing_flowrules = external_port.getVNFPortsFlowruleSendingTrafficToVNFPort(node.id, endpoint_port.id)
                # WARNING: if the port isn't connected only on the ENDPOINT (endpoint_port) that flows will be deleted
                external_port.list_outgoing_label = self.mergeFlowrules(external_outgoing_flowrules, internal_ingoing_flowrules)    
            
            # TODO: manage external endpoint
            """
            for external_endpoint in self.nf_fg.getEndpointsSendingTrafficToVNFPort(node.id, endpoint_port.id):
                self.setConnectionFlowrules(internal_port.list_ingoing_label, external_endpoint)
            """
        # TODO: Delete ingoing connection to endpoint of internal nf-fg
        for endpoint_port in node.listPort:
            internal_ports = internal_nf_fg.getVNFPortsSendingTrafficToEndpoint(endpoint_port.id)
            
            for internal_port in internal_ports:
                internal_port.deleteConnectionToEndpoint(endpoint_port.id)
                
            internal_ports = internal_nf_fg.getVNFPortsReceivingTrafficFromEndpont(endpoint_port.id)
            for internal_port in internal_ports:
                internal_port.deleteConnectionToEndpoint(endpoint_port.id)

            
        # TODO: Find switch connected together
        for vnf in self.nf_fg.listVNF:
            for internal_vnf in internal_switches:
                logging.debug("vnf nf-fg: "+vnf.id)
                if vnf.id == internal_vnf.id:
                    logging.debug("vnf internal_vnf: "+internal_vnf.id)
                    connected_switch = self.nf_fg.getSwitchConnectedToVNF(vnf)
                    self.mergeSwitches(vnf, connected_switch)
                         
        
    def mergeFlowrules(self, first_flowrules, second_flowrules):
        flowrules = []
        for first_flowrule in first_flowrules:
            for second_flowrule in second_flowrules:
                final_matches = self.mergeMatches(first_flowrule.matches, second_flowrule.matches)
                flowrules.append(Flowrule(second_flowrule.action, matches = final_matches))
                
                #first_flowrule.changeMatches(final_matches)
                #first_flowrule.changeAction(second_flowrule.action)
        return flowrules    
                    
                
    def mergeMatches(self, first_matches, second_matches):
        final_matches = []
        match = Match()
        
        fields = ['sourceMac', 'destMAC', 'vlanId', 'etherType', 'sourceIP', 'destIP', 'protocol', 'sourcePort', 'destPort', 'tosBits']
        for first_match in first_matches:
            for second_match in second_matches:
                for field in fields:
                    if field in first_match.of_field and field in second_match.of_field:
                        if first_match.of_field[field] == second_match.of_field[field]:
                            match.of_field[field] = second_match.of_field[field]
                        else:
                            break
                    elif field in first_match.of_field:
                        match.of_field[field] = first_match.of_field[field]
                    elif field in second_match.of_field:
                        match.of_field[field] = second_match.of_field[field]

                match._id = uuid.uuid4().hex
                
                # WARNING: if the port isn't connected only on the ENDPOINT (endpoint_port) that flows will be deleted
                # set priority to ext priority - THANKS TO THE HYPOTHESIS MADE EARLIER
                match.priority = second_match.priority
                final_matches.append(match)
                
        return final_matches
        
        
    def setConnectionFlowrules(self, a, b):
        return
        
        
        
