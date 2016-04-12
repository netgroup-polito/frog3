'''
Created on Nov 3, 2015

@author: fabiomignini
'''
import copy, uuid
from orchestrator_core.config import Configuration
from nffg_library.nffg import VNF, FlowRule, Action, Match, Port
from orchestrator_core.sql.graph import Graph

import logging, json, requests, os, inspect
from vnf_template_library.template import Template
from vnf_template_library.validator import ValidateTemplate
from nffg_library.validator import ValidateNF_FG
from nffg_library.nffg import NF_FG

TEMPLATE_SOURCE = Configuration().TEMPLATE_SOURCE
TEMPLATE_PATH = Configuration().TEMPLATE_PATH
SWITCH_TEMPLATE = Configuration().SWITCH_TEMPLATE

class NFFGManagerCA(object):
    def __init__(self, nffg):
        self.nffg = nffg
    
    def connectEndPointSwitchToGraph(self, end_point_switch, old_end_point):
        end_point_switch_port = self.createSwitchPort(end_point_switch)
        end_point_switch.addPort(end_point_switch_port)
        
        original_flow_rules = []
        original_flow_rules += self.nffg.getFlowRulesSendingTrafficFromEndPoint(old_end_point.id)
        original_flow_rules += self.nffg.getFlowRulesSendingTrafficToEndPoint(old_end_point.id)
        new_flow_rules = copy.deepcopy(original_flow_rules)
        for new_flow_rule in new_flow_rules:
            _id = uuid.uuid4().hex
            # TODO: Check uniqueness of the ID
            new_flow_rule.id = _id
            new_flow_rule.status = 'new'
            if new_flow_rule.match.port_in.split(':')[0] == 'endpoint' and new_flow_rule.match.port_in.split(':')[1] == old_end_point.id:
                new_flow_rule.match.port_in = 'vnf:'+end_point_switch.id+':'+end_point_switch_port.id
            for action in new_flow_rule.actions:
                if action.output.split(':')[0] == 'endpoint' and action.output.split(':')[1] == old_end_point.id:
                    action.output = 'vnf:'+end_point_switch.id+':'+end_point_switch_port.id
        return new_flow_rules
    
    def connectToRemoteEndPoint(self, ovsdb, graph_id, end_point, remote_nffg, remote_end_point_id, new_flow_rule_type='connection_end_point',
                                    end_point_and_flow_rule_type='shall_not_be_installed'):
        # Get the flow-rules from or to remote_endpoint 
        external_flow_rules = []
        external_flow_rules += remote_nffg.getFlowRulesSendingTrafficFromEndPoint(remote_end_point_id)
        external_flow_rules += remote_nffg.getFlowRulesSendingTrafficToEndPoint(remote_end_point_id)
        
        internal_flow_rules = []
        internal_flow_rules += self.nffg.getFlowRulesSendingTrafficFromEndPoint(end_point.id)
        internal_flow_rules += self.nffg.getFlowRulesSendingTrafficToEndPoint(end_point.id)
        # set the end_point together its flow rules to shall_not_be_installed type
        #end_point.type = end_point_and_flow_rule_type
        #Graph().updateEndpointType(graph_endpoint_id=end_point.id, graph_id=graph_id, endpoint_type=end_point.type)
        #for internal_flow_rule in internal_flow_rules:
        #    internal_flow_rule.type = end_point_and_flow_rule_type
        #    Graph().updateFlowRuleType(flow_rule_id=internal_flow_rule.db_id, _type=internal_flow_rule.type)
        
        
        # Change the end-point id in the flows of the graph with all the interfaces of the flow-rules just obtained
        #  this interfaces are external to the graph, so we have to manage them with him internal id.
        #  example: "INGRESS_tap"+interface_internal_id[:11]
        new_flow_rules = []
        for external_flow_rule in external_flow_rules:
            for internal_flow_rule in internal_flow_rules[:]:
                new_flow_rule = copy.deepcopy(internal_flow_rule)
                new_flow_rule.type = new_flow_rule_type
                if new_flow_rule.match.port_in.split(':')[0] == 'endpoint' and new_flow_rule.match.port_in.split(':')[1] == end_point.id:
                    if not (external_flow_rule.match.port_in.split(':')[0] == 'endpoint' and external_flow_rule.match.port_in.split(':')[1] == remote_end_point_id):
                        self.nffg.flow_rules.append(new_flow_rule)
                        new_flow_rules.append(new_flow_rule)
                        if external_flow_rule.match.port_in.split(':')[0] == 'endpoint':
                            interface = remote_nffg.getEndPoint(external_flow_rule.match.port_in.split(':')[1]).interface_internal_id
                            bridge_datapath_id = ovsdb.getBridgeDatapath_id(interface)
                            if bridge_datapath_id is None:
                                raise Exception("Bridge datapath id doesn't found for this interface: "+str(interface))
                            new_flow_rule.match.port_in = 'connection_port:INGRESS_'+bridge_datapath_id+':'+interface
                        elif external_flow_rule.match.port_in.split(':')[0] == 'vnf':
                            interface = 'tap'+remote_nffg.getVNF(external_flow_rule.match.port_in.split(':')[1]).\
                                getPort(external_flow_rule.match.port_in.split(':')[2]+':'+external_flow_rule.match.port_in.split(':')[3]).internal_id[:11]
                            bridge_datapath_id = ovsdb.getBridgeDatapath_id(interface)
                            if bridge_datapath_id is None:
                                raise Exception("Bridge datapath id doesn't found for this interface: "+str(interface))
                            new_flow_rule.match.port_in = 'connection_port:INGRESS_'+bridge_datapath_id+':'+interface
                for action in new_flow_rule.actions:
                    if action.output.split(':')[0] == 'endpoint' and action.output.split(':')[1] == end_point.id:
                        for remote_action in external_flow_rule.actions:
                            if not (remote_action.output.split(':')[0] == 'endpoint' and remote_action.output.split(':')[1] == remote_end_point_id):
                                self.nffg.flow_rules.append(new_flow_rule)
                                new_flow_rules.append(new_flow_rule)
                                if remote_action.output.split(':')[0] == 'endpoint':
                                    interface = remote_nffg.getEndPoint(remote_action.output.split(':')[1]).interface_internal_id
                                    bridge_datapath_id = ovsdb.getBridgeDatapath_id(interface)
                                    if bridge_datapath_id is None:
                                        raise Exception("Bridge datapath id doesn't found for this interface: "+str(interface))
                                    action.output = 'connection_port:INGRESS_'+bridge_datapath_id+':'+interface
                                elif remote_action.output.split(':')[0] == 'vnf':
                                    interface = 'tap'+remote_nffg.getVNF(remote_action.output.split(':')[1]).\
                                        getPort(remote_action.output.split(':')[2]+':'+remote_action.output.split(':')[3]).internal_id[:11]
                                    bridge_datapath_id = ovsdb.getBridgeDatapath_id(interface)
                                    if bridge_datapath_id is None:
                                        raise Exception("Bridge datapath id doesn't found for this interface: "+str(interface))
                                    
                                    action.output = 'connection_port:INGRESS_'+bridge_datapath_id+':'+interface
        
        # TODO: Save this flows as end-point resource, this flow-rules will have as graph_id: graph_id:remote_graph_id
        #        as in the graph_connection table
        # Save new flow-rules into the DB
        for new_flow_rule in new_flow_rules:
            Graph().addFlowRule(graph_id=graph_id, flow_rule=new_flow_rule, nffg=self.nffg)
    
    def connectNewEndPointToNFFG(self, old_end_point, new_end_point):
        original_flow_rules = []
        original_flow_rules += self.nffg.getFlowRulesSendingTrafficFromEndPoint(old_end_point.id)
        original_flow_rules += self.nffg.getFlowRulesSendingTrafficToEndPoint(old_end_point.id)
        new_flow_rules = copy.deepcopy(original_flow_rules)
        for new_flow_rule in new_flow_rules:
            _id = uuid.uuid4().hex
            # TODO: Check uniqueness of the ID
            new_flow_rule.id = _id
            if new_flow_rule.match.port_in.split(':')[0] == 'endpoint' and new_flow_rule.match.port_in.split(':')[1] == old_end_point.id:
                new_flow_rule.match.port_in = 'endpoint:'+new_end_point.id
            for action in new_flow_rule.actions:
                if action.output.split(':')[0] == 'endpoint' and action.output.split(':')[1] == old_end_point.id:
                    action.output = 'endpoint:'+new_end_point.id
        return new_flow_rules

    def deleteEndPointFlows(self, end_point_id):
        flow_rules = []
        flow_rules += self.nffg.getFlowRulesSendingTrafficFromEndPoint(end_point_id)
        flow_rules += self.nffg.getFlowRulesSendingTrafficToEndPoint(end_point_id)
        return flow_rules
    
    def deleteEndPointSwitchFlows(self, end_point_switch):
        flow_rules = []
        flow_rules += self.nffg.getFlowRulesSendingTrafficFromVNF(end_point_switch)
        flow_rules += self.nffg.getFlowRulesSendingTrafficToVNF(end_point_switch)
        return flow_rules
        
    
    def deleteEndPointSwitch(self, end_point_id):
        end_point_switch = self.getEndPointSwitch(end_point_id)
        assert (end_point_switch is not None)
        flow_rules = self.deleteEndPointSwitchFlows(end_point_switch)
        return end_point_switch, flow_rules
        

    def createEndPointSwitch(self, old_end_point, availability_zone):
        # Create an ID
        _id = uuid.uuid4().hex
        # TODO: Check uniqueness of the ID
        end_point_switch = VNF(_id=_id, name='end-point-switch-'+old_end_point.id, vnf_template_location=SWITCH_TEMPLATE)
        self.addTemplate(end_point_switch, end_point_switch.vnf_template_location)
        end_point_switch.availability_zone = availability_zone
        self.nffg.addVNF(end_point_switch)
        return end_point_switch
    
    def createSwitchPort(self, switch):
        # Create an ID. Check the switch to obtain the maximum relative ID
        maximum_relative_id = switch.getHigherReletiveIDForPortLabel("L2Port")
        new_relative_id = int(maximum_relative_id) + 1
        _id = "L2Port:"+str(new_relative_id)
        
        return Port(_id=_id, name="auto-generated-port")
    
    def connectNewEndPointToEndPointSwitch(self, old_end_point, new_end_point):
        end_point_switch = self.getEndPointSwitch(old_end_point.id)
        end_point_switch_port = self.createSwitchPort(end_point_switch)
        end_point_switch.addPort(end_point_switch_port)
        return self.connectVNFAndEndPoint(vnf_id=end_point_switch.id, port_id=end_point_switch_port.id, end_point_id=new_end_point.id)
    
    def getEndPointSwitch(self, origina_end_point_id):
        end_point_switch_name = 'end-point-switch-'+origina_end_point_id
        for vnf in self.nffg.vnfs:
            if vnf.name == end_point_switch_name:
                return vnf
    
    def setFlowRuleOfEndPointType(self, end_point_id, _type):
        flow_rules_origina_endpoint = []
        flow_rules_origina_endpoint += self.nffg.getFlowRulesSendingTrafficFromEndPoint(end_point_id)
        flow_rules_origina_endpoint += self.nffg.getFlowRulesSendingTrafficToEndPoint(end_point_id)
        for flow_rule_origina_endpoint in flow_rules_origina_endpoint:
            flow_rule_origina_endpoint.type = _type
        return flow_rules_origina_endpoint
    
    def connectVNFAndEndPoint(self, vnf_id, port_id, end_point_id):
        return self.connectNodes(node1="vnf:"+vnf_id+":"+port_id, node2="endpoint:"+end_point_id)
        
    def connectNodes(self, node1, node2):
        flow_rules = []
        to_vnf1_action = Action(output=node1)
        to_vnf2_action = Action(output=node2)
        from_vnf1_match = Match(port_in=node1)
        from_vnf2_match = Match(port_in=node2)
        # Create an ID
        _id = uuid.uuid4().hex
        # TODO: Check uniqueness of the ID
        
        flow_rules.append(FlowRule(_id=_id, priority=200, match=from_vnf2_match, actions=[to_vnf1_action]))
        # Create an ID
        _id = uuid.uuid4().hex
        # TODO: Check uniqueness of the ID
        flow_rules.append(FlowRule(_id=_id, priority=200, match=from_vnf1_match, actions=[to_vnf2_action]))
        return flow_rules
    
    def addTemplate(self, vnf,  uri):
        '''
        Retrieve the Template of a specific VNF.
        It is possible that the template of a VNF is a graph,
        in that case that VNF will be expanded.
        The two graph will be connected together,
        accordingly to the original connection of the VNF that has been expanded.
        '''
        logging.debug("Getting manifest: "+str(uri)+" of vnf :"+str(vnf.name)) 
        template = self.getTemplate(uri)
        
        if template.checkExpansion() is True:
            logging.debug("Expanding a VNF: "+str(vnf.name))
            nffg_from_template = self.getNFFGDict(template.uri)
            # Validate forwarding graph
            ValidateNF_FG().validate(nffg_from_template)
            
            internal_nffg = NF_FG()
            internal_nffg.parseDict(nffg_from_template)
            NFFGManagerCA(internal_nffg).addTemplates()
            
            self.nffg.expandNode(vnf, internal_nffg)
        
        else:    
            vnf.addTemplate(template)
            # Check min port and max port
            vnf.checkPortsAgainstTemplate()
    
    def getTemplate(self, uri):
        temlate_dict = self.getTemplateDict(uri)
        ValidateTemplate().validate(temlate_dict)
        template = Template()
        template.parseDict(temlate_dict)
        return template
    
    def getNFFGDict(self, filename): 
        base_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0])).rpartition('/')[0]
        return self.getDictFromFile(base_folder+"/graphs/", filename)
    
    def getTemplateDict(self, uri):  
        if TEMPLATE_SOURCE == "glance":
            return self.getDictFromGlance(uri)
        else:
            base_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0])).rpartition('/')[0]
            base_folder = base_folder.split('orchestrator_core')[0]
            logging.debug("Base folder: "+str(base_folder))
            return self.getDictFromFile(base_folder+TEMPLATE_PATH, uri)
        
    def getDictFromFile(self, path, filename):
        json_data=open(path+filename).read()
        return json.loads(json_data)
    
    def getDictFromGlance(self, uri):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': self.token}
        resp = requests.get(uri, headers=headers)
        resp.raise_for_status()
        return json.loads(resp.text)