'''
Created on Jul 1, 2015

@author: fabiomignini
'''
import collections
import logging
import copy
from Common.config import Configuration
from Common.SQL.graph import Graph


INGRESS_PORT = Configuration().INGRESS_PORT

class VNFTemplate(object):

    def __init__(self, vnf):
        self.ports_label = {}
        self.id = vnf.id
        template = vnf.manifest
        for port in template['ports']:
            tmp = int(port['position'].split("-")[0])
            self.ports_label[port['label']] = tmp
            
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
        self.trashNetwork = None
        
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
        if(arch.VNF2 != None):
            self.edges[arch.VNF1].ports[arch.port1].archs.append(arch)
            self.edges[arch.VNF2].ports[arch.port2].archs.append(arch)
        
    def vistGraph(self):
        '''
        Visit the graph for Net creation for the OpenStack Heat template (breadth-first search)
        '''
        self.edgeToVisit = collections.deque()
        for edge in self.edges.values():
            if not edge.visit:
                edge.visit = True
                self.edgeToVisit.append(edge)
                while True:
                    try:
                        visitedEdge = self.edgeToVisit.popleft()
                        self.visit(visitedEdge)
                    except IndexError:
                        break
    
    def visit(self, edge):
        '''
        Visiting the single edge attaching the network to the ports
        '''        
        for port in edge.ports.values():
            newNet = None
            if port.net == None:
                for arch in port.archs:
                    if arch.VNF1 == edge.id:
                        if self.edges[arch.VNF2].ports[arch.port2].net != None:
                            edge.setNetwork(self.edges[arch.VNF2].ports[arch.port2].net, arch.port1)                            
                            newNet = self.edges[arch.VNF2].ports[arch.port2].net
                            break
                    else:
                        if self.edges[arch.VNF1].ports[arch.port1].net != None:
                            edge.setNetwork(self.edges[arch.VNF1].ports[arch.port1].net, arch.port2)
                            newNet = self.edges[arch.VNF1].ports[arch.port1].net
                            break
                if newNet == None:
                    
                    newNet = Net('fakenet_'+str(self.num_net))
                    self.num_net += 1
                    self.networks.append(newNet)
                    '''
                    # One network for all ports (to avoid problems during the updates of the graph)
                    newNet = Net('fakenet')
                    self.num_net = 1
                    self.networks = []
                    self.networks.append(newNet)
                    '''

            else:
                newNet = port.net
                if(port.network != None):
                    if('net' in port.network):
                        if newNet.subnet != port.network['net']:
                            newNet.subnet = port.network['net']
            if newNet.name in edge.network.values() and port.trash == None:
                if self.trashNetwork == None:
                    self.trashNetwork = Net('trashNetwork')
                    self.networks.append(self.trashNetwork)
                port.trash = self.trashNetwork
            else:
                edge.network[port.name] = newNet.name
            '''
            # One network for all ports (to avoid problems during the updates of the graph)
            edge.network[port.name] = newNet.name
            '''
            port.net = newNet
            for arch in port.archs:
                if arch.VNF1 == edge.id:
                    self.edges[arch.VNF2].setNetwork(newNet, arch.port2)
                    if not self.edges[arch.VNF2].visit:
                        self.edges[arch.VNF2].visit = True
                        self.edgeToVisit.append(self.edges[arch.VNF2])
                else:
                    self.edges[arch.VNF1].setNetwork(newNet, arch.port1)
                    if not self.edges[arch.VNF1].visit:
                        self.edges[arch.VNF1].visit = True
                        self.edgeToVisit.append(self.edges[arch.VNF1])
    
    def getStackTemplate(self):
        '''
        Return the Heat template of the graph (requires the visit)
        '''
        ingressFlows = []

        stackTemplate = {}
        stackTemplate["heat_template_version"] = "2013-05-23"
        stackTemplate['resources'] = {}
        for vnf in self.edges.values():
            if self.switch is not None and vnf == self.switch.VNF:
                continue
            stackTemplate['resources'][vnf.id] = vnf.getResourceTemplate()
            for port in vnf.listPort:
                stackTemplate['resources'][vnf.id+port.name] = port.getResourceTemplate()
                if port.fip != None:
                    stackTemplate['resources']['floatingIP'] = port.fip
        for network in self.networks:
            stackTemplate['resources'][network.name] = network.getNetResourceTemplate()
            stackTemplate['resources']['sub'+network.name] = network.getSubNetResourceTemplate()
        for flow in self.archs:
            vect = flow.getVectResourceTemplate()
            for flowroute in vect:
                if(flow.ingress):
                    if 'ingressPort' in flowroute['properties'] and flowroute['properties']['ingressPort'] == INGRESS_PORT:
                        ingressFlows.append(flowroute['properties']['id'])

                stackTemplate['resources'][flowroute['properties']['id']] = flowroute
                
        for ingressFlow in ingressFlows:
            stackTemplate['resources'][ingressFlow]['depends_on'] = []
            for key in stackTemplate['resources'].keys():
                logging.debug("key: "+str(key))
                if  not any(key == ingressFlow_check for ingressFlow_check in ingressFlows):
                    logging.debug("in dependency")
                    stackTemplate['resources'][ingressFlow]['depends_on'].append(key)
            logging.debug("ingressFlow: "+str(ingressFlow))
        return stackTemplate
            
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
    
    def getNetResourceTemplate(self):
        '''
        Return the Resource template of the network
        '''
        resource = {}
        resource["type"] = "OS::Neutron::Net"
        resource['properties'] = {}
        resource['properties']['name'] = self.name
        return resource
        
    def getSubNetResourceTemplate(self):
        '''
        Return the Resource template of the associated subnetwork
        '''
        resource = {}
        resource["type"] = "OS::Neutron::Subnet"
        resource['properties'] = {}
        resource['properties']['name'] = 'sub'+self.name
        resource['properties']['enable_dhcp'] = self.dhcp
        resource['properties']['network_id'] = { "Ref" : self.name }
        resource['properties']['ip_version'] = 4
        resource['properties']['cidr'] = self.subnet
        return resource
    
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
        for port in vnf.listPort:
            if hasattr(port, 'status') and port.status is not None:
                port_status = port.status
            else:
                port_status = 'new'
            if port.status != 'new' and port.status != None:
                logging.debug("port.db_id: "+str(port.db_id))
                net = Net(Graph().getNetwork(port.db_id).name)
                net.network_id = Graph().getNetwork(port.db_id).id
            else:
                net = None
            logging.debug("port.status: "+str(port.status))
            logging.debug("port_status: "+str(port_status))
            self.ports[port.id] = Port(port, VNFId, status = port_status, net = net, internal_id = port.internal_id)
            position = template_info.ports_label[port.id.split(":")[0]] + int(port.id.split(":")[1])
            self.listPort.insert(position,self.ports[port.id])
        
    @property
    def id(self):
        return self._id
    
    def getResourceTemplate(self):
        '''
        Return the Resource template of the VNF
        '''
        resource = {}
        resource["type"] = "OS::Nova::Server"
        resource['properties'] = {}
        resource['properties']['flavor'] = self.flavor
        resource['properties']['image'] = self.URIImage
        resource['properties']['name'] = self.id
        resource['properties']['availability_zone'] = self.availability_zone
        resource['properties']['networks'] = []
        
        for port in self.listPort:
            resource['properties']['networks'].append({ "port": { "Ref": self.id+port.name}})
        return resource
    
    def setNetwork(self, net, port):
        '''
        Set the given network to the given port
        '''
        duplicate = False
        for item in self.ports.values():
            if item.net == net and item.name != port:
                duplicate = True
                break
        if duplicate == True and self.ports[port].trash == None:
            self.ports[port].trash = self.ports[port].net
        self.ports[port].net = net
        return duplicate
    
    def getResourceJSON(self):
        resource = {}
        resource['server'] = {}
        resource['server']['name'] = self.id
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
    
    def __init__(self, portTemplate, VNFId, status='new', net=None, internal_id=None):
        '''
        Constructor for the port
        params:
            portTemplate:
                The template of the port from the user profile graph
            VNFId:
                The Id of the VNF associated to that port
        '''
        self.net = net
        self.trash = net
        self.fip = None
        self.name = portTemplate.id
        self.network = None
        self.type = None
        self.VNFId = VNFId
        self.archs = []
        self.status = status
        self.port_id = internal_id
        
    def getResourceTemplate(self):
        '''
        Return the Resource template of the port
        '''
        resource = {}
        resource["type"] = "OS::Neutron::Port"
        resource['properties'] = {}
        resource['properties']['name'] = self.VNFId+self.name
        if self.trash == None:
            resource['properties']['network_id'] = { "Ref": self.net.name }
            if not self.network==None:
                if "ip" in self.network:
                    resource['properties']['fixed_ips'] = []
                    fixIP = {}
                    fixIP['ip_address'] = self.network["ip"]
                    if "net" in self.network:
                        fixIP['subnet_id']={ "Ref": 'sub'+self.net.name }
                        resource['properties']['fixed_ips'].append(fixIP)
                if "mac" in self.network:
                    resource['properties']['mac_address'] = self.network['mac']
                if "floating_ip" in self.network:
                    if self.network["floating_ip"]:
                        self.fip = {}
                        self.fip["type"] = "OS::Neutron::FloatingIPAssociation"
                        self.fip['properties'] = {}
                        self.fip['properties']['port_id'] = {"Ref": self.VNFId+self.name}
                        self.fip['properties']['floatingip_id'] = "37e11391-cf8a-4847-b1e9-c7ad2d8e7f5f"
        else:
            resource['properties']['network_id'] = { "Ref": self.trash.name }
        return resource
    
    def getResourceJSON(self):
        resource = {}
        resource['port'] = {}
        resource['port']['name'] = self.VNFId+self.name
        resource['port']['network_id'] = self.net.network_id
        return resource
       
class FlowRoute(object):
    '''
    Class that contains the flow route of the profile graph
    '''


    def __init__(self, link):
        '''
        Constructor of the flow
        '''
        self.ingress = False
        if link.node1.vnf_id is not None:
            self.VNF1 =  link.node1.vnf_id
            self.port1 = link.node1.port_id
        if link.node1.interface is not None:
            self.port1 = link.node1.port_id
        if link.node2 is not None:
            if link.node2.vnf_id is not None:
                self.VNF2 = link.node2.vnf_id
                self.port2 = link.node2.port_id
            else:
                self.VNF2 = None
            if link.node2.interface is not None:
                self.port2 = link.node2.port_id
                # if ingress is True i will set the other resources as dependency 
                self.ingress = True
            if link.node2.endpoint is not None:
                self.port2 = link.node2.port_id
                # if ingress is True i will set the other resources as dependency 
                self.ingress = True
        else:
            self.VNF2 = None
            self.port2 = None
            self.ingress = None
        self.flowrules = link.flowrules
        
    def getVectResourceTemplate(self):
        '''
        Return the vector of Resource template associate to the matches of the FLowRoute
        '''
        VNFdependencies = {}
        VNFdependencies['VNF1'] = {"Ref": self.VNF1}
        if(self.VNF2 != None):
            VNFdependencies['VNF2'] = {"Ref": self.VNF2}
        vector = []
        
        for flowspec in self.flowrules:
            logging.debug("flows: "+str(flowspec.getJSON()))
            flowspec = flowspec.getJSON()
            #logging.debug(json.dumps(flowspec))
            flow = flowspec['flowspec']
            if('source_VNF_id' in flow):
                ingressPort = {"Ref": flow['source_VNF_id']+flow['ingressPort']}
            else:
                ingressPort = flow['ingressPort']
            action = {}
            action['type'] = flowspec['action']['type'].upper()
            if action['type'] == "OUTPUT":
                if("VNF" in flowspec['action']):
                    action['outputPort'] = {"Ref": flowspec['action']['VNF']['id']+flowspec['action']['VNF']['port']}
                else:
                    if "type" in flowspec['action']['endpoint']:
                        if "interface" in flowspec['action']['endpoint']['type']:
                            action['outputPort'] = flowspec['action']['endpoint']['interface']                
            for match in flow['matches']:
                flowrule = {}
                flowrule['type'] = "OS::Neutron::FlowRoute"
                flowrule['properties'] = {}
                for key, value in match.iteritems():
                    if key == 'sourceMAC':
                        flowrule['properties']['dlSrc'] = value.upper()
                    elif key == 'destMAC':
                        flowrule['properties']['dlDst'] = value.upper()
                    elif key == 'sourceIP':
                        flowrule['properties']['nwSrc'] = value
                    elif key == 'destIP':
                        flowrule['properties']['nwDst'] = value
                    elif key == 'sourcePort':
                        flowrule['properties']['tpSrc'] = value
                    elif key == 'destPort':
                        flowrule['properties']['tpDst'] = value
                    else:
                        flowrule['properties'][key] = value
                flowrule['properties']['actions'] = action
                flowrule['properties']['ingressPort'] = ingressPort
                flowrule['properties']['VNFDependencies'] = VNFdependencies
                vector.append(flowrule)     
        return vector
    
    def getResourcesJSON(self, tenant_id, edges):
        resources = []
        for flowspec in self.flowrules:
            resource = {}
            resource['flowrule'] = {}
            flowspec = flowspec.getJSON()
            flow = flowspec['flowspec']
            if('source_VNF_id' in flow):
                ingressPort = edges[flow['source_VNF_id']].ports[flow['ingressPort']].port_id
                #ingressPort = Neutron().getPort(flow['source_VNF_id']+flow['ingressPort'])
            else:
                ingressPort = flow['ingressPort']
            resource['flowrule']['ingressPort'] = ingressPort
            action = {}
            action['type'] = flowspec['action']['type'].upper()            
            if action['type']=='OUTPUT':
                if("VNF" in flowspec['action']):
                    action['outputPort'] = edges[flowspec['action']['VNF']['id']].ports[flowspec['action']['VNF']['port']].port_id
                else:
                    if "type" in flowspec['action']['endpoint']:
                        if "interface" in flowspec['action']['endpoint']['type']:
                            action['outputPort'] = flowspec['action']['endpoint']['interface']
                resource['flowrule']['actions']='OUTPUT='+str(action['outputPort'])
            elif action['type']=='DROP':
                resource['flowrule']['actions']='DROP'
            for match in flow['matches']:
                for key, value in match.iteritems():
                    if key == 'sourceMAC':
                        resource['flowrule']['dlSrc'] = value.upper()
                    elif key == 'destMAC':
                        resource['flowrule']['dlDst'] = value.upper()
                    elif key == 'sourceIP':
                        resource['flowrule']['nwSrc'] = value
                    elif key == 'destIP':
                        resource['flowrule']['nwDst'] = value
                    elif key == 'sourcePort':
                        resource['flowrule']['tpSrc'] = value
                    elif key == 'destPort':
                        resource['flowrule']['tpDst'] = value
                    elif key == 'id':
                        resource['flowrule']['id'] = tenant_id+"-"+value
                    else:
                        resource['flowrule'][key] = str(value)
            resources.append(copy.deepcopy(resource))
        return resources
