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
    
    def getJSON(self):
        '''
        Get a JSON structure representing the flow
        It is ready to be passed to OpenDaylight REST API
        '''
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
        
    def setEthernetMatch(self, ethertype = None, eth_source = None, eth_dest = None):
        '''
        Define this Match as an ethernet address (source or dest) matching
        Args:
            in_port:
                the input port identifier
        '''
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
    def __init__(self, portTemplate, VNFId):
        '''
        Constructor for the port
        params:
            portTemplate:
                The template of the port from the user profile graph
            VNFId:
                The Id of the VNF associated to that port
        '''
        self.net = None
        self.name = portTemplate.id
        self.VNFId = VNFId
        self.port_id = None
    
    def setNetwork(self, net_id):
        '''
        Set the OpenStack network id to a port object
        Args:
            net_id:
                Network id retrieved through Neutron REST API call
        '''
        self.net = net_id
    
    def setId(self, port_id):
        '''
        Set the OpenStack port id to a port object
        Args:
            port_id:
                Port id returned after port creation with Neutron API
        '''
        self.port_id = port_id
    
    def getResourceTemplate(self):
        '''
        Get the Heat resource template of the port
        '''
        resource = {}
        resource["type"] = "OS::Neutron::Port"
        resource['properties'] = {}
        resource['properties']['name'] = self.VNFId+self.name
        resource['properties']['network_id'] = self.net        
        return resource
    
    def getResourceJSON(self):
        '''
        Get the JSON representation of the port
        '''
        resource = {}
        resource['port'] = {}
        resource['port']['name'] = self.VNFId+self.name
        resource['port']['network_id'] = self.net
        return resource

class VNF(object):
    def __init__(self, VNFId, vnf, image, flavor, availability_zone):
        '''
        Constructor for the VNF (params obtained from FG completed with the template)
        params:
            VNFId:
                VNF identifier
            vnf:
                JSON representation of the VNF
            image:
                URI of the image on Glance
            flavor:
                OpenStack flavor to be used for this VNF
            availability_zone:
                OpenStack zone where the VNF will be instantiated
        '''
        self.availability_zone = availability_zone
        self._id = VNFId
        self.ports = {}
        self.listPort = []
        self.flavor = flavor
        self.URIImage = image
        self._OSid = None
        
        template_info = VNFTemplate(vnf)
        for port in vnf.listPort:
            self.ports[port.id] = Port(port, VNFId)
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
    
    def getResourceTemplate(self):
        '''
        Return the Heat resource template of the VNF
        '''
        resource = {}
        resource["type"] = "OS::Nova::Server"
        resource['properties'] = {}
        resource['properties']['flavor'] = self.flavor['name']
        resource['properties']['image'] = self.URIImage['name']
        resource['properties']['name'] = self.id
        resource['properties']['availability_zone'] = self.availability_zone
        resource['properties']['networks'] = []
        
        for port in self.listPort:
            resource['properties']['networks'].append({ "port": { "Ref": self.id+port.name}})
        return resource
    
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
    
class ProfileGraph(object):
    def __init__(self):
        '''
        Class that stores the profile graph of the user which will be used for Heat template generation
        '''
        self._id = None
        self.functions = {}
    
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
        Add a new edge to the graph: it is a VNF object
        '''
        self.functions[vnf.id] = vnf
    
    def getStackTemplate(self):
        '''
        Return the Heat template of the graph
        '''
        stackTemplate = {}
        stackTemplate["heat_template_version"] = "2013-05-23"
        stackTemplate['resources'] = {}
        
        for vnf in self.functions.values():
            stackTemplate['resources'][vnf.id] = vnf.getResourceTemplate()
            for port in vnf.listPort:
                if port.net is not None:
                    stackTemplate['resources'][vnf.id+port.name] = port.getResourceTemplate()
                
        return stackTemplate
