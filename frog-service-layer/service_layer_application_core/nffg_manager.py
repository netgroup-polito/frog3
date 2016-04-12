'''
Created on Oct 20, 2015

@author: fabiomignini
'''
import logging, json, uuid, os, copy, inspect
from service_layer_application_core.config import Configuration
from nffg_library.validator import ValidateNF_FG
from nffg_library.nffg import NF_FG, VNF, Port, FlowRule, Action, Match, EndPoint


SWITCH_NAME = Configuration().SWITCH_NAME
SWITCH_TEMPLATE = Configuration().SWITCH_TEMPLATE

CONTROL_SWITCH_NAME = Configuration().CONTROL_SWITCH_NAME
EGRESS_GRAPH_FILE = Configuration().EGRESS_GRAPH_FILE
INGRESS_GRAPH_FILE = Configuration().INGRESS_GRAPH_FILE
SG_USER_EGRESS = Configuration().SG_USER_EGRESS
SG_USER_INGRESS = Configuration().SG_USER_INGRESS

class NFFG_Manager(object):
    
    def __init__(self, nffg):
        self.nffg = nffg
        self.control_switch = None  
        
    # Graph optimization
    def mergeUselessVNFs(self):
        '''
        This function try to optimize the NF-FG merging or deleting useless VNFs.
        In the current implementation only the merge of the switch NF (based on the name of the VNF) is done.
        '''
        self.findSwitchToMerge()
    
    def findSwitchToMerge(self):
        # To be merged, the two switch ports that are connected together should not filter the traffic.
        switches = {}
        for vnf in self.nffg.vnfs:
            for switch_name in SWITCH_NAME:
                if vnf.name == switch_name:
                    switches[vnf.id] = vnf
        for flow_rule in self.nffg.flow_rules:
            if flow_rule.match.port_in.split(':')[0] == 'vnf' and flow_rule.match.port_in.split(':')[1] in switches:
                for action in flow_rule.actions:
                    if action.output.split(':')[0] == 'vnf' and action.output.split(':')[1] in switches:
                        self.mergeSwitches(switches[flow_rule.match.port_in.split(':')[1]], 
                                           flow_rule.match.port_in.split(':')[2]+':'+flow_rule.match.port_in.split(':')[3],
                                           switches[action.output.split(':')[1]], 
                                           action.output.split(':')[2]+':'+action.output.split(':')[3])
                        self.findSwitchToMerge()
                        return
                
        
    def createEndPoint(self, name, _type="internal", node=None, switch_id=None,
                       interface=None, remote_ip=None, local_ip=None, ttl=None, status=None,
                       db_id=None, internal_id=None, vlan_id=None, interface_internal_id=None):
        # Create an ID
        _id = uuid.uuid4().hex
        # TODO: Check uniqueness of the ID
        end_point =  EndPoint(_id=_id, name=name, _type=_type, node=node, switch_id=switch_id,
                  interface=interface, remote_ip=remote_ip, local_ip=local_ip, ttl=ttl,
                   status=status, db_id=db_id, internal_id=internal_id, vlan_id=vlan_id,
                    interface_internal_id=interface_internal_id)
        self.nffg.addEndPoint(end_point)
        return end_point
    
    def createSwitchVNF(self):
        # Create an ID
        _id = uuid.uuid4().hex
        # TODO: Check uniqueness of the ID
        
        return VNF(_id=_id, name=SWITCH_NAME[0], vnf_template_location=SWITCH_TEMPLATE)
    
    def createControlSwitchVNF(self, end_point_name):
        # Create an ID
        _id = uuid.uuid4().hex
        # TODO: Check uniqueness of the ID
        
        self.control_switch = VNF(_id=_id, name=CONTROL_SWITCH_NAME, vnf_template_location=SWITCH_TEMPLATE)
        endpoint_port = self.createSwitchPort(self.control_switch)
        self.control_switch.ports.append(endpoint_port)
        
        # Connect to end-point
        end_point = self.createEndPoint(name=end_point_name)
        self.connectVNFAndEndPoint(vnf_id=self.control_switch.id, port_id=endpoint_port.id, end_point_id=end_point.id)
    
    def createSwitchPort(self, switch):
        # Create an ID. Check the switch to obtain the maximum relative ID
        maximum_relative_id = switch.getHigherReletiveIDForPortLabel("L2Port")
        new_relative_id = int(maximum_relative_id) + 1
        _id = "L2Port:"+str(new_relative_id)
        
        return Port(_id=_id, name="auto-generated-port")
    
    def connectEndPoints(self, end_point1_id, end_point2_id):
        self.connectNodes(node1="endpoint:"+end_point1_id, node2="endpoint:"+end_point2_id)
    
    def connectVNFAndEndPoint(self, vnf_id, port_id, end_point_id):
        self.connectNodes(node1="vnf:"+vnf_id+":"+port_id, node2="endpoint:"+end_point_id)
    
    def connectVNFs(self, vnf1_id, port1_id, vnf2_id, port2_id):
        self.connectNodes(node1="vnf:"+vnf1_id+":"+port1_id, node2="vnf:"+vnf2_id+":"+port2_id)
        
    def connectNodes(self, node1, node2):
        to_vnf1_action = Action(output=node1)
        to_vnf2_action = Action(output=node2)
        from_vnf1_match = Match(port_in=node1)
        from_vnf2_match = Match(port_in=node2)
        # Create an ID
        _id = uuid.uuid4().hex
        # TODO: Check uniqueness of the ID
        self.nffg.flow_rules.append(FlowRule(_id=_id, priority=200, match=from_vnf2_match, actions=[to_vnf1_action]))
        # Create an ID
        _id = uuid.uuid4().hex
        # TODO: Check uniqueness of the ID
        self.nffg.flow_rules.append(FlowRule(_id=_id, priority=200, match=from_vnf1_match, actions=[to_vnf2_action]))
    
    def mergeSwitches(self, switch1, port_switch1_id, switch2, port_switch2_id):
        
        # Create a new switch
        new_switch = self.createSwitchVNF()
        self.nffg.addVNF(new_switch)
        
        # Delete ports and flow-rules that connect the two switches
        self.nffg.deleteConnectionsBetweenVNFs(switch1.id, port_switch1_id, switch2.id, port_switch2_id)
        for port in switch1.ports:
            if port.id == port_switch1_id:
                port_switch1 = port
        switch1.ports.remove(port_switch1)
        for port in switch2.ports:
            if port.id == port_switch2_id:
                port_switch2 = port
        switch2.ports.remove(port_switch2)
        
        # Add to the new switch the ports of the other two
        for switch in [switch1, switch2]:
            
            for port in switch.ports:
                # TODO: If one of the two switches have a control port, this will be added only one time
                new_port = self.createSwitchPort(new_switch)
                new_switch.addPort(new_port)
                # Change the flow-rule of the ports of the old switches with the new port id
                for flow_rule in self.nffg.flow_rules:
                    flow_rule.changePortOfFlowRule('vnf:'+switch.id+':'+port.id, 'vnf:'+new_switch.id+':'+new_port.id)
            
        # Delete the previous switches and their flow-rules
        self.nffg.vnfs.remove(switch1)
        self.nffg.vnfs.remove(switch2)
        
    def checkIfControlNetIsNedeed(self, vnf, template):
        for port in template.ports:
            if port.label.split(":")[0] == "control":    
                higher_relative_id = vnf.getHigherReletiveIDForPortLabel(port.label)  
                new_relative_id = int(higher_relative_id) + 1
                new_port_id = port.label+':'+str(new_relative_id)
                return True, vnf.addPort(Port(_id = new_port_id, name="Control port"))
        return False, None
    
    def addPortToControlNet(self, vnf, port_id, end_point_name):
        if self.control_switch == None:
            self.createControlSwitchVNF(end_point_name)
            self.nffg.vnfs.append(self.control_switch)
        control_switch_port = self.createSwitchPort(self.control_switch)
        self.control_switch.ports.append(control_switch_port)
        self.connectVNFs(self.control_switch.id, control_switch_port.id, vnf.id, port_id)
        return self.control_switch
    
    def deleteMacAddressInFlows(self, mac_address, endpoint_name):
        '''
        UserDefnedServiceFunction function that connects the endpoint switch to the VNF
        '''
        endpoint = self.nffg.getEndPointsFromName(endpoint_name)[0]
        logging.debug("Deleting flow rule based on mac address: "+mac_address)
        flow_rules = self.nffg.getFlowRulesSendingTrafficFromEndPoint(endpoint.id)
        
        for flow_rule in flow_rules[:]:
            if flow_rule.match.source_mac == mac_address:
                self.nffg.flow_rules.remove(flow_rule)
        
    def deleteEndpointSwitch(self, switch, endpoint):
        '''
        UserDefnedServiceFunction function that connects the endpoint switch to the VNF
         
        TODO: Some dirty code
        '''
        
        ingoing_flow_rules = self.nffg.getFlowRulesSendingTrafficToVNF(switch)
        for ingoing_flow_rule in ingoing_flow_rules[:]:
            if ingoing_flow_rule.match.port_in.split(':')[0] == 'endpoint' and ingoing_flow_rule.match.port_in.split(':')[1] != endpoint.id:
                ingoing_flow_rule.action.output = "endpoint:"+endpoint.id
                new_id = uuid.uuid4().hex
                # TODO: check uniqueness of ID
                ingoing_flow_rule.id = new_id
            else:
                self.nffg.flow_rules.remove(ingoing_flow_rule)
        
        outgoing_flow_rules = self.nffg.getFlowRulesSendingTrafficFromVNF(switch)
        for outgoing_flow_rule in outgoing_flow_rules[:]:
            if outgoing_flow_rule.action.output.split(':')[0] == 'endpoint' and outgoing_flow_rule.action.output.split(':')[1] != endpoint.id:
                outgoing_flow_rule.match.port_in = "endpoint:"+endpoint.id
                new_id = uuid.uuid4().hex
                # TODO: check uniqueness of ID
                outgoing_flow_rule.id = new_id
            else:
                self.nffg.flow_rules.remove(outgoing_flow_rule)
                
        self.nffg.vnfs.remove(switch)
                    
    def connectEndpointSwitchToVNF(self, endpoint, endpoint_switch, switch_port):
        '''
        UserDefnedServiceFunction function that connects the endpoint switch to the VNF
         
        TODO: Warning: only one VNF directly connected to the endpoint is supported
        TODO: Some dirty code
        '''
        
        # Add connections from EndpointSwitch to VNFs
        ingoing_flow_rules = self.nffg.getFlowRuleSendingTrafficFromEndPoint(endpoint.id)
        for ingoing_flow_rule in ingoing_flow_rules:
            if ingoing_flow_rule.action.output.split(':')[0] == 'vnf' and ingoing_flow_rule.action.output.split(':')[1] != endpoint_switch.id:
                ingoing_flow_rule.match.port_in = "vnf:"+endpoint_switch.id+":"+switch_port.id
                new_id = uuid.uuid4().hex
                # TODO: check uniqueness of ID
                ingoing_flow_rule.id = new_id
        
        
        # Add connections from VNFs to EndpointSwitch
        outgoing_flow_rules = self.nffg.getFlowRulesSendingTrafficToEndPoint(endpoint.id)
        for outgoing_flow_rule in outgoing_flow_rules:
            if outgoing_flow_rule.match.port_in.split(':')[0] == 'vnf' and outgoing_flow_rule.match.port_in.split(':')[1] != endpoint_switch.id:
                outgoing_flow_rule.action.output = "vnf:"+endpoint_switch.id+":"+switch_port.id
                new_id = uuid.uuid4().hex
                # TODO: check uniqueness of ID
                outgoing_flow_rule.id = new_id
    
    def addDevicesFlows(self, mac_addresses):
        '''
        UserDefnedServiceFunction function that adds ingress flow for user new device
        '''
        logging.debug("Adding ingress flow rule for the following devices: "+str(mac_addresses))
            
        # Find ingress end-point
        ingress_endpoint = self.nffg.getEndPointsFromName("INGRESS")[0]
        # Find flow rules that connect the end-point
        original_ingress_flow_rules = self.nffg.getFlowRulesSendingTrafficFromEndPoint(ingress_endpoint.id)
        ingress_flow_rules = copy.deepcopy(original_ingress_flow_rules)
        for original_ingress_flow_rule in original_ingress_flow_rules:
            self.nffg.flow_rules.remove(original_ingress_flow_rule)
        for mac_address in mac_addresses:      
            for ingress_flow_rule in ingress_flow_rules:
                ingress_flow_rule.priority = 1000
                ingress_flow_rule.match.source_mac = mac_address
                ingress_flow_rule.id = uuid.uuid4().hex
                flow_copy = copy.deepcopy(ingress_flow_rule)
                self.nffg.flow_rules.append(flow_copy)
        
    def setDeviceFlows(self, mac_address):
        '''
        UserDefnedServiceFunction function that adds in the graph the ingress flow for a user device
        '''
        # Find ingress end-point
        ingress_endpoint = self.nffg.getEndPointsFromName("INGRESS")[0]
        # Find flow rules that connect the end-point
        ingress_flow_rules = self.nffg.getFlowRulesSendingTrafficFromEndPoint(ingress_endpoint.id)
        for ingress_flow_rule in ingress_flow_rules:
            ingress_flow_rule.priority = 1000
            ingress_flow_rule.match.source_mac = mac_address
            ingress_flow_rule.id = uuid.uuid4().hex
    
    def attachIngressNF_FG(self, ingress_nffg):
        self.nffg.attachNF_FG( ingress_nffg, SG_USER_INGRESS)
        
    def attachEgressNF_FG(self, egress_nffg):
        self.nffg.attachNF_FG( egress_nffg, SG_USER_EGRESS)
        
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
        '''
        Read from file a nf-fg
        Returns a NF_FG Object
        '''
        base_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0])).rpartition('/')[0]
        json_data=open(base_folder+"/graphs/"+file_name).read()
        nffg_dict = json.loads(json_data)
        ValidateNF_FG().validate(nffg_dict)
        nffg = NF_FG()
        nffg.parseDict(nffg_dict)
        return nffg