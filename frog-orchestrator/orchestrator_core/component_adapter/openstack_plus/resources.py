'''
Created on Jul 1, 2015

@author: fabiomignini
'''
import collections
import logging
import copy
from orchestrator_core.component_adapter.common import utils
from orchestrator_core.sql.graph import Graph

class VNFTemplate(object):

    def __init__(self, vnf):
        self.ports_label = {}
        self.id = vnf.id
        template = vnf.template
        for port in template.ports:
            tmp = int(port.position.split("-")[0])
            self.ports_label[port.label] = tmp
            
class ProfileGraph(object):
    '''
    Class that stores the profile graph of the user it will be used for the template generation
    '''


    def __init__(self, num_net = 0):
        '''
        Constructor of the Graph
        '''
        self.edges = {}
        self.archs = []
        self.networks = []
        #self.router = Router()
        self.switch = None
        self.num_net = num_net
        
    def addEdge(self, edge):
        '''
        Add a new edge to the graph it is a VNF object
        '''
        self.edges[edge.id] = edge
        
    def addArch(self, arch):
        '''
        Add a new arch to the graph it is a FlowRoute object
        '''
        self.archs.append(arch)
        
    def associateNetworks(self):
        '''
        Associate to each port a different Neutron net
        '''
        for edge in self.edges.values():
            for port in edge.ports.values():
                if port.status == "new" or port.status is None:
                    new_net = Net('fakenet_'+str(self.num_net))
                    self.num_net = self.num_net + 1 
                    self.networks.append(new_net)
                    port.net = new_net
                    edge.network[port.name] = new_net.name
        
class Net(object):
    '''
    Class that contains a network object on the user graph, it contains also the network created for the VM nova constraint
    '''

    def __init__(self, name, subnet="10.0.0.0/24"):
        '''
        Constructor of the network
        '''
        self.name = name
        self.subnet = subnet
        self.dhcp = False
    
    def getNetResourceJSON(self):
        resource = {}
        resource['network'] = {}
        resource['network']['name'] = self.name
        resource['network']['admin_state_up'] = True
        return resource
    
    def getSubNetResourceJSON(self):
        resource = {}
        resource['subnet'] = {}
        resource['subnet']['name'] = 'sub'+self.name
        resource['subnet']['ip_version'] = 4
        resource['subnet']['cidr'] = self.subnet
        resource['subnet']['enable_dhcp'] = self.dhcp
        resource['subnet']['network_id'] = self.network_id
        return resource
                
class VNF(object):
    '''
    Class that contains the VNF data that will be used on the profile generation
    '''


    def __init__(self, VNFId, vnf, imageName, flavor, availability_zone = None, status='new'):
        '''
        Constructor of the VNF data
        '''
        self.availability_zone = availability_zone
        self.visit = False
        self._id = VNFId
        self.name = vnf.name
        self.ports = {}
        self.listPort = []
        self.network = {}
        self.flavor = flavor
        #self.vnfType = VNFTemplate["vnfType"]
        self.URIImage = imageName
        self.status = status
        if self.status != 'new' and self.status is not None:
            self.vnf_id = vnf.internal_id
        template_info = VNFTemplate(vnf)
        for port in vnf.ports:
            if hasattr(port, 'status') and port.status is not None:
                port_status = port.status
            else:
                port_status = 'new'
            if port.status != 'new' and port.status != None:
                #logging.debug("vnf.name: "+str(vnf.name))
                #logging.debug("vnf.id: "+str(vnf.id))
                #logging.debug("port.id: "+str(port.id))
                #logging.debug("port.db_id: "+str(port.db_id))
                net = Net(Graph().getNetwork(port.db_id).name)
                net.network_id = Graph().getNetwork(port.db_id).id
            else:
                net = None
            #logging.debug("port.status: "+str(port.status))
            #logging.debug("port_status: "+str(port_status))
            self.ports[port.id] = Port(port, VNFId, status = port_status, net = net, internal_id = port.internal_id)
            position = template_info.ports_label[port.id.split(":")[0]] + int(port.id.split(":")[1])
            self.listPort.insert(position,self.ports[port.id])
        
    @property
    def id(self):
        return self._id
    
    def getResourceJSON(self):
        resource = {}
        resource['server'] = {}
        resource['server']['name'] = str(self.id)+'-'+str(self.name)
        resource['server']['imageRef'] = self.URIImage        
        resource['server']['flavorRef'] = self.flavor
        resource['server']['availability_zone'] = self.availability_zone
        resource['server']['networks'] = []
        
        for port in self.listPort:
            resource['server']['networks'].append({ "port": port.port_id})
        return resource
                            
class Port(object):
    '''
    Class that contains the port data for the VNF
    '''        
    
    def __init__(self, port_info, VNFId, status='new', net=None, internal_id=None):
        '''
        Constructor for the port
        params:
            port_info:
                The template of the port from the user profile graph
            VNFId:
                The Id of the VNF associated to that port
        '''
        self.net = net
        self.fip = None
        self.name = port_info.id
        if hasattr(port_info, 'mac_address'):
            self.mac_address = port_info.mac_address
        else:
            self.mac_address = utils.getMacAddress(port_info)
        self.network = None
        self.type = None
        self.VNFId = VNFId
        self.archs = []
        self.status = status
        self.port_id = internal_id
        
    def getResourceJSON(self):
        resource = {}
        resource['port'] = {}
        resource['port']['name'] = self.VNFId+self.name
        resource['port']['network_id'] = self.net.network_id
        resource['port']['mac_address'] = self.mac_address
        return resource
       
class FlowRoute(object):
    '''
    Class that contains the flow route of the profile graph
    '''


    def __init__(self, flow_rule, end_points):
        '''
        Constructor of the flow
        '''
        self.status = flow_rule.status
        self.flow_rule = flow_rule
        self.end_points = {}
        for end_point in end_points:
            self.end_points[end_point.id] = end_point
        
    def getResourcesJSON(self, tenant_id, edges):
        resource = {}
        resource['flowrule'] = {}
        
        if self.flow_rule.match.port_in is not None and self.flow_rule.match.port_in.split(':')[0] == 'vnf':
            port_id = self.flow_rule.match.port_in.split(':')[2]+':'+self.flow_rule.match.port_in.split(':')[3]
            ingressPort = edges[self.flow_rule.match.port_in.split(':')[1]].ports[port_id].port_id
        elif self.flow_rule.match.port_in is not None and self.flow_rule.match.port_in.split(':')[0] == 'endpoint':
            ingressPort = self.end_points[self.flow_rule.match.port_in.split(':')[1]].interface_internal_id
        elif self.flow_rule.match.port_in is not None and self.flow_rule.match.port_in.split(':')[0] == 'connection_port':
            if len(self.flow_rule.match.port_in.split(':')) == 2:
                ingressPort = self.flow_rule.match.port_in.split(':')[1]
            else:
                ingressPort = self.flow_rule.match.port_in.split(':')[1]+':'+self.flow_rule.match.port_in.split(':')[2]
        else:
            raise NotImplementedError()    
        resource['flowrule']['ingressPort'] = ingressPort
        
        if self.flow_rule.match.source_mac is not None:
            resource['flowrule']['dlSrc'] = self.flow_rule.match.source_mac
        if self.flow_rule.match.dest_mac is not None:
            resource['flowrule']['dlDst'] = self.flow_rule.match.dest_mac
        if self.flow_rule.match.source_ip is not None:
            resource['flowrule']['nwSrc'] = self.flow_rule.match.source_ip
        if self.flow_rule.match.dest_ip is not None:
            resource['flowrule']['nwDst'] = self.flow_rule.match.dest_ip
        if self.flow_rule.match.source_port is not None:
            resource['flowrule']['tpSrc'] = self.flow_rule.match.source_port
        if self.flow_rule.match.dest_port is not None:
            resource['flowrule']['tpDst'] = self.flow_rule.match.dest_port
        if self.flow_rule.match.ether_type is not None:
            resource['flowrule']['etherType'] = self.flow_rule.match.ether_type
        if self.flow_rule.match.tos_bits is not None:
            resource['flowrule']['tosBits'] = self.flow_rule.match.tos_bits
        if self.flow_rule.match.vlan_id is not None:
            resource['flowrule']['vlanId'] = self.flow_rule.match.vlan_id
        if self.flow_rule.match.vlan_priority is not None:
            resource['flowrule']['vlanPriority'] = self.flow_rule.match.vlan_priority
        if self.flow_rule.match.protocol is not None:
            resource['flowrule']['protocol'] = self.flow_rule.match.protocol
        
        resource['flowrule']['id'] = tenant_id+"-"+self.flow_rule.id
        if self.flow_rule.priority < 65535:
            normalized_priority = self.flow_rule.priority + 1
        else:
            normalized_priority = self.flow_rule.priority 
        resource['flowrule']['priority'] = str(normalized_priority)
        
        if len(self.flow_rule.actions) > 1:
            raise NotImplementedError("More then one action is not supported by the infrastructure layer")
        action = {}
        if self.flow_rule.actions[0].output is not None:
            action['type'] = 'OUTPUT'     
        if action['type']=='OUTPUT':
            if self.flow_rule.actions[0].output is not None and self.flow_rule.actions[0].output.split(':')[0] == 'vnf':
                port_id = self.flow_rule.actions[0].output.split(':')[2]+':'+self.flow_rule.actions[0].output.split(':')[3]
                action['outputPort'] = edges[self.flow_rule.actions[0].output.split(':')[1]].ports[port_id].port_id
            elif self.flow_rule.actions[0].output is not None and self.flow_rule.actions[0].output.split(':')[0] == 'endpoint':
                action['outputPort'] = self.end_points[self.flow_rule.actions[0].output.split(':')[1]].interface_internal_id
            elif self.flow_rule.actions[0].output is not None and self.flow_rule.actions[0].output.split(':')[0] == 'connection_port':
                if len(self.flow_rule.actions[0].output.split(':')) == 2:
                    action['outputPort'] = self.flow_rule.actions[0].output.split(':')[1]
                else:
                    action['outputPort'] = self.flow_rule.actions[0].output.split(':')[1]+':'+self.flow_rule.actions[0].output.split(':')[2]
            else:
                raise NotImplementedError()    
            resource['flowrule']['actions']='OUTPUT='+str(action['outputPort'])
        elif action['type'] == 'DROP':
            resource['flowrule']['actions']='DROP'
        elif action['type'] == 'CONTROLLER':
            resource['flowrule']['actions']='CONTROLLER'
        else:
            raise NotImplementedError()    
        return resource
