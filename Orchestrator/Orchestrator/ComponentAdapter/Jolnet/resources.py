'''
Created on 13/mag/2015

@author: vida
'''

import json

'''
######################################################################################################
########################       Classes which represent ODL objects        ############################
######################################################################################################
'''

class Flow(object):
    '''
    Allows to create a flow and to get its representation in JSON (to be passed to Openflow REST API)
    '''
    def __init__(self, name, flow_id, table_id = 0, priority = 5, installHw = True, 
                 hard_timeout = 0, idle_timeout = 0, actions = [], match = None):
        
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
    
    def getJSON(self):
        j_flow = {}
        j_list_action = []
        
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
    '''
    Should support all possible actions on OpenFlow 1.0, currently supports only a couple of them
    '''
    def __init__(self):
        self.action_type = None
        self.output_port = None
        self.max_length = None
        self.vlan_id = None
        self.vlan_id_present = False
    
    def setOutputAction(self, out_port, max_length):
        self.action_type = "output-action"
        self.output_port = out_port
        self.max_length = max_length
    
    def setSwapVlanAction(self, vlan_id):
        self.action_type = "vlan-match"
        self.vlan_id = vlan_id
        self.vlan_id_present = True
    
    def getActions(self, order):
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
    '''
    Should support all possible matches on OpenFlow 1.0, currently supports only a couple of them
    '''
    def __init__(self):
        self.input_port = None
        self.vlan_id = None
        self.vlan_id_present = None
        self.eth_match = False
        self.ethertype = None
        self.eth_source = None
        self.eth_dest = None
    
    def setInputMatch(self, in_port):
        self.input_port = in_port
    
    def setVlanMatch(self, vlan_id):
        self.vlan_id = vlan_id
        self.vlan_id_present = True
        
    def setEthernetMatch(self, ethertype = None, eth_source = None, eth_dest = None):
        self.eth_match = True
        self.ethertype = ethertype
        self.eth_source = eth_source
        self.eth_dest = eth_dest
    
'''
######################################################################################################
#####################       Classes which represent resources into graphs       ######################
######################################################################################################
'''
class VNFTemplate(object):

    def __init__(self, vnf):
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
        #Port id returned after port creation with Neutron API
        self.port_id = port_id
    
    def getResourceJSON(self):
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
    Class that contains the VNF data that will be used on the profile generation
    '''
    def __init__(self, end_id, name, connection, end_type, node, interface, status = 'new', remote_graph = None, remote_id = None):
        self.id = end_id
        self.name = name
        self.connection = connection
        self.type = end_type
        self.node = node
        self.interface = interface
        self.status = status
        self.remote_graph = remote_graph
        self.remote_id = remote_id
    
class ProfileGraph(object):
    '''
    Class that stores the profile graph of the user which will be used for template generation
    '''
    def __init__(self):
        self._id = None
        self.functions = {}
        self.endpoints = {}
    
    @property
    def id(self):
        return self._id
    
    def setId(self, profile_id):
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
    