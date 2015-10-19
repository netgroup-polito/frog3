'''
Created on 13/mag/2015

@author: vida
'''

import json
import logging

'''
######################################################################################################
########################       Classes which represent ODL objects        ############################
######################################################################################################
'''

class Flow(object):
    def __init__(self, name, flow_id, table_id = 0, priority = 5, installHw = True, 
                 hard_timeout = 0, idle_timeout = 0, actions = [], match = None):
        '''
        Constructor for the Flow
        Args:
            name:
                flow name (not really useful)
            flow_id:
                identifier of the flow (to be recorded for further deletion)
            table_id:
                identifier of the table where to install the flow (in OF1.0 can be only table0!!)
            priority:
                flow priority
            installHw:
                boolean to force installation on the switch (default = True)
            hard_timeout:
                time before flow deletion (default = 0 = no timeout)
            idle_timeout:
                inactivity time before flow deletion (default = 0 = no timeout)
            actions:
                list of Actions for this flow
            match:
                Match for this flow
        '''
        self.strict = False
        self.name = name
        self.flow_id = flow_id
        self.table_id = table_id
        self.priority = priority
        self.installHw = installHw
        self.hard_timeout = hard_timeout
        self.idle_timeout = idle_timeout
        
        self.actions = actions
        self.match = match
    
    def getJSON(self, odl_version, node = None):
        '''
        Gets the JSON. In Hydrogen returns the JSON associated to the given node
        Args:
            node:
                The id of the node related to this JSON (only Hydrogen)
        '''
        j_flow = {}
        j_list_action = []

        if odl_version == "Hydrogen":
            j_flow['name'] = self.flow_id
            j_flow['node'] = {}
            j_flow['node']['id']= node
            j_flow['node']['type']="OF"
            j_flow['priority'] = self.priority
            j_flow['installInHw'] = self.installHw
            j_flow['hardTimeout'] = self.hard_timeout
            j_flow['idleTimeout'] = self.idle_timeout

            if (self.match.input_port is not None):
                j_flow['ingressPort'] = self.match.input_port                                    
            if (self.match.ip_source is not None):
                j_flow['nwSrc'] = self.match.ip_source
            if (self.match.ip_dest is not None):
                j_flow['nwDst'] = self.match.ip_dest
            if (self.match.vlan_id is not None):
                j_flow['vlanId'] = self.match.vlan_id
            if (self.match.ethertype is not None):
                j_flow['etherType'] = self.match.ethertype
            if (self.match.eth_source is not None):
                j_flow['dlSrc'] = self.match.eth_source
            if (self.match.eth_dest is not None):
                j_flow['dlDst'] = self.match.eth_dest
            if (self.match.ip_protocol is not None):
                j_flow['protocol'] = self.match.ip_protocol               
            
            if (self.match.ip_match is True and self.match.ethertype is None):
                j_flow['etherType'] = "0x800"
                logging.warning("Hydrogen requires ethertype set in order to perform ip match: ethertype has been set to 0x800")
            
            for action in self.actions:
                j_action = action.getActionsHydrogen()
                j_list_action.append(j_action)
                
            j_flow['actions'] = j_list_action;

        else:
            j_flow['flow'] = {}
            j_flow['flow']['strict'] = self.strict
            j_flow['flow']['flow-name'] = self.name
            j_flow['flow']['id'] = self.flow_id
            j_flow['flow']['table_id'] = self.table_id
            j_flow['flow']['priority'] = self.priority
            j_flow['flow']['installHw'] = self.installHw
            j_flow['flow']['hard-timeout'] = self.hard_timeout
            j_flow['flow']['idle-timeout'] = self.idle_timeout
            
            j_flow['flow']['instructions'] = {}
            j_flow['flow']['instructions']['instruction'] = {}
            j_flow['flow']['instructions']['instruction']['order'] = str(0)
            j_flow['flow']['instructions']['instruction']['apply-actions'] = {}
            
            i = 0
            for action in self.actions:
                j_action = action.getActions(i)
                j_list_action.append(j_action)
                i = i + 1
                   
            j_flow['flow']['instructions']['instruction']['apply-actions']['action'] = j_list_action
            
            if (self.match is not None):
                j_flow['flow']['match'] = {}
                
                if (self.match.input_port is not None):
                    j_flow['flow']['match']['in-port'] = self.match.input_port
                if (self.match.ip_source is not None):
                    j_flow['flow']['match']['ipv4-source'] = self.match.ip_source
                if (self.match.ip_dest is not None):
                    j_flow['flow']['match']['ipv4-destination'] = self.match.ip_dest
                if (self.match.ip_protocol is not None):
                    j_flow['flow']['match']['ip-match'] = {}
                    j_flow['flow']['match']['ip-match']['ip-protocol'] = self.match.ip_protocol
                if (self.match.vlan_id is not None):
                    j_flow['flow']['match']['vlan-match'] = {}
                    j_flow['flow']['match']['vlan-match']['vlan-id'] = {}
                    j_flow['flow']['match']['vlan-match']['vlan-id']['vlan-id'] = self.match.vlan_id
                    j_flow['flow']['match']['vlan-match']['vlan-id']['vlan-id-present'] = self.match.vlan_id_present
                if (self.match.eth_match is True):
                    j_flow['flow']['match']['ethernet-match'] = {}
                    if (self.match.ethertype is not None):
                        j_flow['flow']['match']['ethernet-match']['ethernet-type'] = {}
                        j_flow['flow']['match']['ethernet-match']['ethernet-type']['type'] = self.match.ethertype
                    if (self.match.eth_source is not None):
                        j_flow['flow']['match']['ethernet-match']['ethernet-source'] = {}
                        j_flow['flow']['match']['ethernet-match']['ethernet-source']['address'] = self.match.eth_source
                    if (self.match.eth_dest is not None):
                        j_flow['flow']['match']['ethernet-match']['ethernet-destination'] = {}
                        j_flow['flow']['match']['ethernet-match']['ethernet-destination']['address'] = self.match.eth_dest
        
        return json.dumps(j_flow)

class Action(object):
    #Should support all possible actions on OpenFlow 1.0, currently supports only a couple of them
    def __init__(self):
        '''
        Represents an OpenFlow 1.0 possible action on the outgoing traffic
        '''
        self.action_type = None
        self.output_port = None
        self.max_length = None
        self.vlan_id = None
        self.vlan_id_present = False
    
    def setOutputAction(self, out_port, max_length):
        '''
        Define this action as an output port action
        Args:
            out_port:
                id of the output port where to send out the traffic
            max_lenght:
                max length of the packets
        '''
        self.action_type = "output-action"
        self.output_port = out_port
        self.max_length = max_length
    
    def setSwapVlanAction(self, vlan_id):
        '''
        Define this action as a vlan tag swapping action
        Args:
            vlan_id:
                vlan id for the new tag
        '''
        self.action_type = "vlan-match"
        self.vlan_id = vlan_id
        self.vlan_id_present = True
        
    def getActionsHydrogen(self):
        '''
        Returns actions formatted for Hydrogen
        '''
        j_action = None
        if (self.action_type == "output-action"):
            j_action = "OUTPUT="+self.output_port
        elif (self.action_type == "vlan-match"):
            j_action = "SET_VLAN_ID="+self.vlan_id
        return j_action
    
    def getActions(self, order):
        '''
        Get the Action as an object (to be inserted in Flow actions list)
        Args:
            order:
                the order number of this action in the Flow list
        '''
        j_action = {}
        j_action['order'] = order
        
        if (self.action_type == "output-action"):
            j_action['output-action'] = {}
            j_action['output-action']['output-node-connector'] = self.output_port
            j_action['output-action']['max-length'] = self.max_length
        elif (self.action_type == "vlan-match"):
            j_action['set-field'] = {}
            j_action['set-field']['vlan-match'] = {}
            j_action['set-field']['vlan-match']['vlan-id'] = {}
            j_action['set-field']['vlan-match']['vlan-id']['vlan-id'] = self.vlan_id
            j_action['set-field']['vlan-match']['vlan-id']['vlan-id-present'] = self.vlan_id_present
        
        return j_action
    
class Match(object):
    #Should support all possible matches on OpenFlow 1.0, currently supports only a couple of them
    def __init__(self):
        '''
        Represents an OpenFlow 1.0 possible matching rules for the incoming traffic
        '''
        self.input_port = None
        self.vlan_id = None
        self.vlan_id_present = None
        self.eth_match = False
        self.ethertype = None
        self.eth_source = None
        self.eth_dest = None
        self.ip_protocol = None
        self.ip_match = None
        self.ip_source = None
        self.ip_dest = None
        self.tp_match = None
        self.port_source = None
        self.port_dest = None
    
    def setInputMatch(self, in_port):
        '''
        Define this Match as an input port matching
        Args:
            in_port:
                the input port identifier
        '''
        self.input_port = in_port
    
    def setVlanMatch(self, vlan_id):
        '''
        Define this Match as an input port matching
        Args:
            vlan_id:
                the vlan identifier
        '''
        self.vlan_id = vlan_id
        self.vlan_id_present = True
        
    def setEtherTypeMatch(self, ethertype):
        self.eth_match = True
        self.ethertype = ethertype
        
    def setEthernetMatch(self, eth_source = None, eth_dest = None):
        self.eth_match = True
        self.eth_source = eth_source
        self.eth_dest = eth_dest
        
    def setIPProtocol(self, protocol):
        self.ip_protocol = protocol
        
    def setIPMatch(self, ip_source = None, ip_dest = None):
        self.ip_match = True
        self.ip_source = ip_source
        self.ip_dest = ip_dest
        
    def setTpMatch(self, port_source = None, port_dest = None):
        '''
        Sets a transport protocol match
        '''
        self.tp_match = True
        self.port_source = port_source
        self.port_dest = port_dest
    
'''
######################################################################################################
#####################       Classes which represent resources into graphs       ######################
######################################################################################################
'''
class VNFTemplate(object):
    def __init__(self, vnf):
        '''
        Constructor for the template
        params:
            vnf:
                JSON structure containing template data
        '''
        self.ports_label = {}
        self.id = vnf.id
        template = vnf.manifest
        for port in template['ports']:
            tmp = int(port['position'].split("-")[0])
            self.ports_label[port['label']] = tmp

class Port(object):
    '''
    Class that contains the port data for the VNF
    '''    
    def __init__(self, portTemplate, VNFId, status='new'):
        '''
        Constructor for the port
        params:
            portTemplate:
                The template of the port from the user profile graph
            VNFId:
                The Id of the VNF associated to that port
            status:
                useful when updating graphs, can be new, already_present or to_be_deleted
        '''
        self.net = None
        self.vlan = None
        self.name = portTemplate.id
        self.VNFId = VNFId
        self.port_id = None
        self.status = status
        self.device_id = None
    
    def setNetwork(self, net_id, vlan_id):
        #Network id retrieved through Neutron REST API call
        self.net = net_id
        self.vlan = vlan_id
        
    def setDeviceId(self, device_id):
        self.device_id = device_id
    
    def setId(self, port_id):
        '''
        Set the OpenStack port id to a port object
        Args:
            port_id:
                Port id returned after port creation with Neutron API
        '''
        self.port_id = port_id
    
    def getResourceJSON(self):
        '''
        Get the JSON representation of the port
        '''
        resource = {}
        resource['port'] = {}
        resource['port']['name'] = self.VNFId+self.name
        resource['port']['network_id'] = self.net
        if self.device_id is not None:
            resource['port']['device_id'] = self.device_id
        return resource

class VNF(object):
    '''
    Class that contains the VNF data that will be used on the profile generation
    '''
    def __init__(self, VNFId, vnf, image, flavor, availability_zone, status='new'):
        '''
        Constructor for the vnf
        params:
            VNFId:
                The Id of the VNF
            vnf:
                the VNF object extracted from the nf_fg
            image:
                the URI of the image (taken from the Template)
            flavor:
                the flavor which best suits this VNF
            availability_zone:
                the zone where to place it
            status:
                useful when updating graphs, can be new, already_present or to_be_deleted
        '''
        self.availability_zone = availability_zone
        self._id = VNFId
        self.ports = {}
        self.listPort = []
        self.flavor = flavor
        self.URIImage = image
        self._OSid = None
        self.status = status
        
        template_info = VNFTemplate(vnf)
        for port in vnf.listPort:
            if port.status is None:
                status = "new"
            else:
                status = port.status
            self.ports[port.id] = Port(port, VNFId, status)
            position = template_info.ports_label[port.id.split(":")[0]] + int(port.id.split(":")[1])
            self.listPort.insert(position,self.ports[port.id])
        
    @property
    def id(self):
        return self._id
    
    @property
    def OSid(self):
        return self._OSid
    
    @OSid.setter
    def OSid(self, value):
        self._OSid = value
    
    def getResourceJSON(self):
        '''
        Get the JSON representation of the VNF
        '''
        resource = {}
        resource['server'] = {}
        resource['server']['name'] = self.id
        resource['server']['imageRef'] = self.URIImage['id']
        resource['server']['flavorRef'] = self.flavor['id']
        resource['server']['availability_zone'] = self.availability_zone
        resource['server']['networks'] = []
        
        for port in self.listPort:
            if port.port_id is not None:
                resource['server']['networks'].append({ "port": port.port_id})
        return resource

class Endpoint(object):
    '''
    Class that contains the endpoints data
    '''
    def __init__(self, end_id, name, connection, end_type, node, interface, status, remote_graph = None, remote_id = None):
        self.id = end_id
        self.name = name
        self.connection = connection
        self.type = end_type
        self.node = node
        self.interface = interface
        self.status = status
        self.remote_graph = remote_graph
        self.remote_id = remote_id
        self.user_source_mac = None
        self.user_dest_mac = None
        self.user_vlan = None
        self.user_node = None
        self.user_interface = None
        self.user_source_ip = None
        self.user_dest_ip = None
        self.user_etherType = None
        self.user_protocol = None
        
    def setUserParams(self, user_source_mac, user_dest_mac, user_vlan, user_node, user_interface, user_source_ip, user_dest_ip, ether_type, user_protocol):
        self.user_source_mac = user_source_mac
        self.user_dest_mac = user_dest_mac
        self.user_vlan = user_vlan
        self.user_node = user_node
        self.user_interface = user_interface
        self.user_source_ip = user_source_ip
        self.user_dest_ip = user_dest_ip
        self.user_etherType = ether_type
        self.user_protocol = user_protocol
        self.connection = True
        self.status = 'new'
    
class ProfileGraph(object):
    def __init__(self):
        '''
        Class that stores the profile graph of the user which will be used for Heat template generation
        '''
        self._id = None
        self.functions = {}
        self.endpoints = {}
    
    @property
    def id(self):
        return self._id
    
    def setId(self, profile_id):
        '''
        Set profile id
        '''
        self._id = profile_id
    
    def addVNF(self, vnf):
        '''
        Add a new vnf to the graph
        '''
        self.functions[vnf.id] = vnf
    
    def addEndpoint(self, endpoint):
        '''
        Add a new endpoint to the graph
        '''
        self.endpoints[endpoint.id] = endpoint
        
    def getIngressEndpoint(self, endpoint_id):
        for endpoint in self.endpoints.values():
            if endpoint.type == "vlan-ingress":   
                if endpoint.id == endpoint_id:
                    return endpoint
    
    def getVlanEgressEndpoints(self):
        endpoints = []
        for endpoint in self.endpoints.values():
            if endpoint.type == "vlan-egress":   
                endpoints.append(endpoint)
        return endpoints
    
    def getVlanIngressEndpoints(self):
        endpoints = []
        for endpoint in self.endpoints.values():
            if endpoint.type == "vlan-ingress":   
                endpoints.append(endpoint)
        return endpoints
    