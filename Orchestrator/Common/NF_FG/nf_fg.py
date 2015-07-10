import uuid
import json
import logging
import copy

from Common.config import Configuration
from Common.exception import Wrong_ISP_Graph, connectionsError

SWITCH_TEMPLATE = Configuration().SWITCH_TEMPLATE
DEFAULT_PRIORITY = Configuration().DEFAULT_PRIORITY
CONTROL_SWITCH_NAME = Configuration().CONTROL_SWITCH_NAME
SWITCH_NAME = Configuration().SWITCH_NAME

ISP_EGRESS = Configuration().ISP_EGRESS
ISP_INGRESS = Configuration().ISP_INGRESS
USER_INGRESS = Configuration().USER_INGRESS
CONTROL_EGRESS = Configuration().CONTROL_EGRESS
ISP = Configuration().ISP

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]




class EndpointCounter( object):
    __metaclass__ = Singleton
    def __init__(self):
        self.endpoint_counter = 1
        
    def get(self):
        return self.endpoint_counter
    
    def inc(self):
        self.endpoint_counter = self.endpoint_counter + 1

class NF_FG(object):
    '''
    Represent the NF-FG
    '''
    def __init__(self, nf_fg=None):
        '''
        Constructor
        '''
        # TODO: Validate nf_fg
        
        self.listVNF = []
        self.listEndpoint = []
        self.endpoint_map = None
        if nf_fg is not None:
            self._id = nf_fg['profile']['id']
            self.name = nf_fg['profile']['name']
    
            for vnf in nf_fg['profile']['VNFs']:
                manifest = None
                availability_zone = None
                if 'availability_zone' in vnf:
                    availability_zone = vnf['availability_zone']
                if 'manifest' in vnf: 
                    manifest = vnf['manifest']
                    
                self.vnf = VNF(vnf['name'], vnf['vnf_descriptor'], vnf['id'], vnf['ports'], manifest = manifest, availability_zone=availability_zone)
                self.listVNF.append(self.vnf)
            if 'endpoints' in nf_fg['profile']:
                for endpoint in nf_fg['profile']['endpoints']:
                    attached = False
                    endpoint_switch = None
                    connection = False
                    remote_id = None
                    remote_graph = None
                    remote_graph_name = None
                    remote_interface = None
                    edge = False
                    endpoint_type = None
                    port = None
                    interface = None
                    node = None
                    user_mac = None
                    if 'edge' in endpoint:
                        edge = endpoint['edge']
                    if 'remote_graph_name' in endpoint:
                        remote_graph_name = endpoint['remote_graph_name']
                    if 'remote_id' in endpoint:
                        remote_id = endpoint['remote_id']
                    if 'remote_graph' in endpoint:
                        remote_graph = endpoint['remote_graph']
                    if 'connection' in endpoint:
                        connection = endpoint['connection']
                    if 'remote_interface' in endpoint:
                        remote_interface = endpoint['remote_interface']
                    if 'attached' in endpoint:
                        attached = endpoint['attached']
                    if 'endpoint_switch' in endpoint:             
                        endpoint_switch = self.getVNFByID(endpoint['endpoint_switch'])
                    if 'type' in endpoint:
                        endpoint_type = endpoint['type']
                    if 'port' in endpoint:
                        port = endpoint['port']
                    if 'interface' in endpoint:
                        interface = endpoint['interface']
                    if 'node' in endpoint:
                        node = endpoint['node']
                    if 'user_mac_address' in endpoint:
                        user_mac = endpoint['user_mac_address']
                    connections = []
                    if 'connections' in endpoint:
                        for connection in endpoint['connections']:
                            """
                            ext_nf_fg = json.loads(get_profile(connection['ext_nf_fg']))
                            ext_nf_fg = NF_FG(ext_nf_fg)
                            logging.debug("NF-FG - __init__ - connection found: "+connection['ext_nf_fg'])
                            ext_edge_endpoint = ext_nf_fg.getEndpointByID(connection['ext_edge_endpoint'])
                            logging.debug("NF-FG - __init__ - connection found ext_edge_endpoint: "+
                                connection['ext_edge_endpoint'])
                            logging.debug("NF-FG - __init__ - connection found : "+str(ext_edge_endpoint))
                            """
                            connections.append(Connection(connection['ext_nf_fg'], connection['ext_edge_endpoint']))
                    self.endpoint = Endpoint(endpoint['id'], endpoint['name'], connections = connections,
                                              endpoint_switch = endpoint_switch, attached = attached,
                                               connection=connection, remote_id=remote_id, remote_graph=remote_graph,
                                               remote_graph_name=remote_graph_name, remote_interface = remote_interface, 
                                               edge=edge, endpoint_type = endpoint_type, 
                                               port=port, interface=interface, node = node, user_mac = user_mac)
                    self.listEndpoint.append(self.endpoint)
                
        # True when control switch will be created
        self.control_switch_label = False
    
    @property
    def id(self):
        return self._id 

        
    def characterizeEndpoint(self, endpoint, endpoint_type = None, interface = None, endpoint_id = None, node=None):
        if endpoint_id is not None:
            endpoint.port = endpoint_id
        if endpoint_type is not None:
            endpoint.type = endpoint_type
        if interface is not None:
            endpoint.interface = interface
        if node is not None:
            endpoint.node = node
        
        
    def getVNFByID(self, vnf_id):
        for vnf in self.listVNF:
            if vnf.id == vnf_id:
                return vnf
            
    def addVNF(self, vnf):
        self.listVNF.append(vnf)
        
    def createEndpoint(self, name, edge = False, endpoint_id=None, db_id=None):
        if endpoint_id is None:
            #endpoint_id = uuid.uuid4().hex
            #endpoint_id = uuid.uuid4().int & (1<<32)-1
            e = EndpointCounter()
            #logging.debug("Created endpoint id:"+str(id(e)))
            endpoint_id = e.get()
            
            #logging.debug("Created endpoint: "+str(e.get()))
            e.inc()
            #logging.debug("Created endpoint dopo: "+str(e.get()))
            
        
        logging.debug("Created endpoint: "+str(endpoint_id))
        endpoint_id = str(endpoint_id)
        endpoint = Endpoint(endpoint_id, name, edge=edge, db_id=db_id)
        self.listEndpoint.append(endpoint)
        return endpoint
    
    def createVNF(self, name, vnf_descriptor, vnf_id, ports=None, manifest=None, db_id=None, internal_id=None):
        vnf = VNF(name, vnf_descriptor, vnf_id, ports=ports, manifest = manifest, db_id = db_id, internal_id = internal_id)
        self.listVNF.append(vnf)
        return vnf
        
    def addControlSwitch(self, endpoint_name = None):
        if self.control_switch_label is False:
            self.control_switch_label = True
            name = CONTROL_SWITCH_NAME
            template = SWITCH_TEMPLATE
            self.control_switch = VNF(name, template)
            self.listVNF.append(self.control_switch)
            
            # create link towards  ENDPOINT CONTROL_EGRESS or USER_CONTROL_EGRESS
            if endpoint_name is None:
                if ISP is True:
                    user_control_egress  = self.createEndpoint("USER_CONTROL_EGRESS")
                else:
                    user_control_egress  = self.createEndpoint("EGRESS")
            else:
                user_control_egress  = self.createEndpoint(endpoint_name)
            port = self.addPortToSwitch(self.control_switch)
            port.setFlowRuleToEndpoint(user_control_egress.id)
            port.setFlowRuleFromEndpoint(self.control_switch.id, user_control_egress.id)
        return self.control_switch
    
    def addPortToSwitch(self, vnf):
        return self.addPortToVNF(vnf, "L2Port")
        
    def addPortToVNF(self, vnf, label):   
        return vnf.addPort(vnf, label)
            
    def connectVNFToEndpoint(self, vnf, port, endpoint):
        port.setFlowRuleToEndpoint(endpoint.id)
        port.setFlowRuleFromEndpoint(endpoint.id)
          
    def connectTwoVNFs(self, vnfA, portA, vnfB, portB):
        portB.setFlowRuleToVNF(vnfA.id, portA.id)
        portA.setFlowRuleToVNF(vnfB.id, portB.id)
    
    def getEndpointFromName(self, endpoint_name):
        for endpoint in self.listEndpoint:
            if endpoint.name == endpoint_name:
                return endpoint
            
    def getEdgeEndpointsByName(self, endpoint_name):
        endpoints = []
        for endpoint in self.listEndpoint:
            if endpoint.name == endpoint_name:
                endpoints.append(endpoint)
        return endpoints
            
    def getEndpointSwithConnectedToEndpoint(self, endpoint_id):   
        for vnf in self.listVNF:
            for port in vnf.listPort:
                for flowrule in port.list_ingoing_label:
                    if flowrule.flowspec['ingress_endpoint'] is not None and flowrule.flowspec['ingress_endpoint']  == endpoint_id:
                        if vnf.name == "Endpoint_Switch":
                            return vnf
                                           
    def deleteEndpointConnections(self, endpoint):
        ports = self.getVNFPortsSendingTrafficToEndpoint(endpoint.id)
        for port in ports[:]:            
            for flowrule in port.list_outgoing_label[:]:
                if flowrule.action.endpoint is not None and getEndpointID(flowrule.action.endpoint) == endpoint.id:
                    port.list_outgoing_label.remove(flowrule)
                    
                    
        ports = self.getVNFPortsReceivingTrafficFromEndpont(endpoint.id)
        for port in ports[:]:
            for flowrule in port.list_ingoing_label[:]:
                if 'ingress_endpoint' in flowrule.flowspec and flowrule.flowspec['ingress_endpoint'] == endpoint.id:
                    port.list_ingoing_label.remove(flowrule)
                         
    def getVNFPortsReceivingTrafficFromEndpont(self,  endpoint_id):
        connected_ports  = []
        for vnf in self.listVNF:
            for port in vnf.listPort:
                if port.list_ingoing_label is not None:
                    for flowrule in port.list_ingoing_label:
                        if 'ingress_endpoint' in flowrule.flowspec and flowrule.flowspec['ingress_endpoint'] == endpoint_id:
                            connected_ports.append(port)
        return connected_ports
            
    def getVNFPortsConnectedToEndpoint(self, endpoint_id):
        in_ports = self.getVNFPortsReceivingTrafficFromEndpont(endpoint_id)
        out_ports = self.getVNFPortsSendingTrafficToEndpoint(endpoint_id)   
        ports = in_ports
        for out_port in out_ports:
            equal = False
            for port in ports:
                if out_port.id == port.id:
                    equal = True
            if equal is False:
                ports.append(out_port)
        return ports
            
    def getSwitches(self):
        switches = [] 
        for vnf in self.listVNF:
            if vnf.name == SWITCH_NAME or vnf.name == CONTROL_SWITCH_NAME:
                switches.append(vnf)
        return switches
    
    def getSwithConnectedToEndpoint(self, endpoint):
        for vnf in self.listVNF:
            for port in vnf.listPort:
                if port.list_ingoing_label is not None:
                    for flowrule in port.list_ingoing_label:
                        if flowrule.flowspec['ingress_endpoint'] is not None and flowrule.flowspec['ingress_endpoint']  == endpoint:
                            if vnf.name == CONTROL_SWITCH_NAME or vnf.name == SWITCH_NAME:
                                return vnf
                            
    def getSwitchConnectedToVNF(self, vnf):
        # Maximum one switch
        num_switch = 0
        switch = None
        for nf_fg_vnf in self.listVNF:
            if nf_fg_vnf.name == CONTROL_SWITCH_NAME or nf_fg_vnf.name == SWITCH_NAME:
                for port in nf_fg_vnf.listPort:
                    for flowrule in port.list_outgoing_label: 
                        if flowrule.action.vnf is not None and flowrule.action.vnf['id'] == vnf.id:
                            if num_switch != 0:
                                raise connectionsError("Trying to connect too many switch together.")
                            switch = nf_fg_vnf
                            num_switch = num_switch + 1
        return switch
                             
    def getVNFSendingTrafficToVNFPort(self, vnf_id, port_id):
        connected_vnfs  = []
        for vnf in self.listVNF:
            for port in vnf.listPort:
                for flowrule in port.list_outgoing_label:
                    if flowrule.action.vnf is not None and flowrule.action.vnf['id'] == vnf_id and flowrule.action.vnf['port'] == port_id:
                        connected_vnfs.append(vnf) 
        return connected_vnfs
    
    def getVNFConnectedToEndpoint(self, endpoint_id):
        connected_vnfs  = []
        for vnf in self.listVNF:
            connected = False
            for port in vnf.listPort:
                for flowrule in port.list_outgoing_label: 
                    if flowrule.action.endpoint is not None and getEndpointID(flowrule.action.endpoint) == endpoint_id:
                        connected = True
                if port.list_ingoing_label is not None:
                    for flowrule in port.list_ingoing_label:
                        if 'ingress_endpoint' in flowrule.flowspec and flowrule.flowspec['ingress_endpoint'] == endpoint_id:
                            connected = True
            if connected:
                connected_vnfs.append(vnf)
                        
        return connected_vnfs
               
    def getVNFPortsSendingTrafficToEndpoint(self, endpoint_id):
        connected_vnfs  = []
        for vnf in self.listVNF:
            for port in vnf.listPort:
                for flowrule in port.list_outgoing_label: 
                    if flowrule.action.endpoint is not None and getEndpointID(flowrule.action.endpoint) == endpoint_id:
                        connected_vnfs.append(port) 
        return connected_vnfs
    
    def getVNFPortsSendingTrafficToVNFPort(self, vnf_id, port_id):
        connected_vnfs  = []
        for vnf in self.listVNF:
            for port in vnf.listPort:
                for flowrule in port.list_outgoing_label:
                    if flowrule.action.vnf is not None and flowrule.action.vnf['id'] == vnf_id and flowrule.action.vnf['port'] == port_id:
                        connected_vnfs.append(port) 
        return connected_vnfs

    def getEndpointsSendingTrafficToVNFPort(self, vnf_id, port_id):
        '''
        Returns a list of endpoint object
        '''
        connected_endpoints  = []
        for vnf in self.listVNF:
            for port in vnf.listPort:
                for flowrule in port.list_ingoing_label:
                    if flowrule.action.vnf is not None and flowrule.action.vnf['id'] == vnf_id and flowrule.action.vnf['port'] == port_id:
                        for endpoint in self.listEndpoint:
                            if flowrule.flowspec['ingress_endpoint'] == endpoint.id:          
                                connected_endpoints.append(endpoint)
        return connected_endpoints
    
    def getEndpointsSendingTrafficToVNF(self, vnf_id):
        '''
        Returns a list of Endpoint object
        '''
        connected_endpoint_ids  = []
        for vnf in self.listVNF:
            for port in vnf.listPort:
                for flowrule in port.list_ingoing_label:
                    if flowrule.action.vnf is not None and flowrule.action.vnf['id'] == vnf_id:
                        connected_endpoint_ids.append(flowrule.flowspec['ingress_endpoint'])
        connected_endpoints = []
        for endpoint in self.listEndpoint:
            for connected_endpoint_id in connected_endpoint_ids:
                if endpoint.id == connected_endpoint_id:
                    connected_endpoints.append(endpoint)
        return connected_endpoints
        
    def addEndpointSwitch(self, endpoint_name):
        '''
        Make a wrapper of  createEndpointSwitch function
        '''
        control_user_endpoint = self.getEndpointFromName(endpoint_name)
        assert isinstance(control_user_endpoint, Endpoint)
        if control_user_endpoint is None:
            raise Wrong_ISP_Graph(endpoint_name+" is not in the NF-FG")
        endpoint_switch  = self.createEndpointSwitch(control_user_endpoint)
        control_user_endpoint.endpoint_switch = endpoint_switch
        logging.debug("addEndpointSwitch - control_user_endpoint id: "+control_user_endpoint._id)
        logging.debug("addEndpointSwitch - control_user_endpoint.endpoint_switch id: "+control_user_endpoint.endpoint_switch.id)

        return endpoint_switch
    
    def createEndpointSwitch(self, endpoint):
        ''' 
        Create a switch named "Endpoint_Switch" and connect it to a passed endpoint
        '''
        
        # TODO: what a fuck?
        self.control_switch_label = True
        
        name = "Endpoint_Switch"
        template = SWITCH_TEMPLATE
        endpoint_switch = VNF(name, template)
        self.listVNF.append(endpoint_switch)
        
        # create link towards  end-point
        port = self.addPortToSwitch(endpoint_switch)
        port.setFlowRuleToEndpoint(endpoint.id)
        port.setFlowRuleFromEndpoint(endpoint_switch.id, endpoint.id)
        return endpoint_switch
        
    def getEndpointSwitch(self, endpoint):
        return self.getEndpointSwithConnectedToEndpoint(endpoint.id)
    
    def getEndpointSwitchByEdgeEndpoints(self, edge_endpoint):
        return self.getEndpointSwithConnectedToEndpoint(edge_endpoint.id)
    
    def findEdgeEndpoint(self, ext_nf_fg, endpoint_name):
        # TODO: transform this find function in a create function
        '''
        Find a free Edge Endpoint
        '''     
        endpoint = ext_nf_fg.getEndpointFromName(endpoint_name)
        edge_endpoint_list = ext_nf_fg.getEdgeEndpoint(endpoint.endpoint_switch)
        #logging.debug("NF-FG - findEdgeEndpoint - listEndpoint: "+str(len(edge_endpoint_list)))
        for edge_endpoint in edge_endpoint_list:
            #logging.debug("NF-FG - findEdgeEndpoint - edge endpoint id: "+str(edge_endpoint.id))
            #logging.debug("NF-FG - findEdgeEndpoint - edge endpoint attached: "+str(edge_endpoint.attached))
            assert isinstance(edge_endpoint, Endpoint)
            if edge_endpoint.attached is False or edge_endpoint.attached is None:
                edge_endpoint.attached = True
                #logging.debug("NF-FG - findEdgeEndpoint - edge endpoint : "+str(edge_endpoint))            
                return edge_endpoint
        
    def getEdgeEndpoint(self, endpoint_switch, new = False):
        if new is False:
            edge_endpoint_list = []
            listEndpoint = self.getEndpointsSendingTrafficToVNF(endpoint_switch.id)
            #logging.debug("NF-FG - getEdgeEndpoint - listEndpoint: "+str(len(listEndpoint)))
            for endpoint in listEndpoint:
                if endpoint.name == "EDGE_ENDPOINT":
                    edge_endpoint_list.append(endpoint)
            return edge_endpoint_list   
        else:
            return self.getEdgeEndpointsByName(endpoint_switch+"_EDGE_ENDPOINT")
    
    def getEndpointByID(self, endpoint_id):
        for endpoint in self.listEndpoint:
            if endpoint.id == endpoint_id:
                return endpoint
        
    def addEdgeEndpoint(self, endpoint_switch): 
        ''' 
        Create an endpoint named "EDGE ENDPOINT" and connect it to passed endpoint switch
        '''
        edge_endpoint = self.createEndpoint("EDGE_ENDPOINT")
        port = self.addPortToSwitch(endpoint_switch)
        port.setFlowRuleToEndpoint(edge_endpoint.id)
        port.setFlowRuleFromEndpoint(endpoint_switch.id, edge_endpoint.id)
        edge_endpoint.endpoint_switch = endpoint_switch
        return edge_endpoint
    
    def getIngoingFlowruleJson(self, list_outgoing_flowrule):
        j_flowrules = []
        j_flowrule = {}
        for ingoing in list_outgoing_flowrule:
            j_flowrule['action'] = {}
            j_flowrule['action']['type'] = ingoing.action.type
            if ingoing.action.vnf is not None:
                j_vnf_action = {}
                j_vnf_action['id'] = ingoing.action.vnf['id']
                j_vnf_action['port'] = ingoing.action.vnf['port']
                j_flowrule['action']['VNF'] = j_vnf_action
            if ingoing.action.endpoint is not None:
                j_endpoint_action = {}
                j_endpoint_action['id'] = getEndpointID(ingoing.action.endpoint)
                j_flowrule['action']['endpoint'] = j_endpoint_action
            j_matches = []
            j_flowspec = {}
            for match in ingoing.matches:   
                j_match = match.of_field
                if match.id is not None:
                    j_match['id'] = match.id
                if match.priority is not None:
                    j_match['priority'] = match.priority
                j_matches.append(j_match)
            j_flowspec['matches'] = j_matches
            j_flowspec['ingress_endpoint'] = ingoing.flowspec['ingress_endpoint']
            j_flowrule['flowspec'] = j_flowspec
            if j_flowrule:
            
                j_flowrules.append(copy.deepcopy(j_flowrule))
        return json.dumps(j_flowrules)

    def getJSON(self):
        j_nf_fg = {}
        j_nf_fg['profile'] = {}
        j_list_vnf = []
        j_list_endpoint = []
        for vnf in self.listVNF:
            j_vnf = {}
            j_vnf['id'] = vnf.id
            j_vnf['name'] = vnf.name
            if vnf.availability_zone is not None:
                j_vnf['availability_zone'] = vnf.availability_zone

            if vnf.manifest is not None:
                j_vnf['manifest'] = vnf.manifest
                j_vnf['vnf_descriptor'] = vnf.template
            else:  
                j_vnf['vnf_descriptor'] = vnf.template
            if vnf.status is not None:
                j_vnf['status'] = vnf.status
            
            j_ports = []
            for port in vnf.listPort:
                j_port = {}
                j_port['id'] = port.id
                if port.internal_id is not None:
                    j_port['internal_id'] = port.internal_id
                
                j_flowrule = {}

                j_port['outgoing_label'] = {}
                j_port['outgoing_label']['flowrules'] = []
                
                j_port['ingoing_label'] = {}
                j_port['ingoing_label']['flowrules'] = []
                
                if port.status is not None:
                    j_port['status'] = port.status
                
                for outgoing in port.list_outgoing_label:
                    
                    if outgoing.id is not None:
                        j_flowrule['id'] = outgoing.id
                    
                    if outgoing.status is not None:
                        j_flowrule['status'] = outgoing.status
                        
                    if outgoing.internal_id is not None:
                            j_flowrule['internal_id'] = outgoing.internal_id
                     
                    j_flowrule['action'] = {}
                    j_flowrule['action']['type'] = outgoing.action.type
                    if outgoing.action.vnf is not None:
                        j_vnf_action = {}
                        j_vnf_action['id'] = outgoing.action.vnf['id']
                        j_vnf_action['port'] = outgoing.action.vnf['port']
                        j_flowrule['action']['VNF'] = j_vnf_action
                    if outgoing.action.endpoint is not None:
                        j_endpoint_action = {}
                        j_endpoint_action['id'] = getEndpointID(outgoing.action.endpoint)
                        j_flowrule['action']['endpoint'] = j_endpoint_action
                        
                    j_matches = []
                    j_flowspec = {}
                    for match in outgoing.matches:  
                        if match.of_field is not None:
                            j_match = match.of_field
                        else:
                            j_match = {}
                        if match.id is not None:
                            j_match['id'] = match.id
                        if match.priority is not None:
                            j_match['priority'] = match.priority
                        
                        j_matches.append(j_match)
                    j_flowspec['matches'] = j_matches
                    j_flowrule['flowspec'] = j_flowspec
                    if j_flowrule:
                        j_port['outgoing_label']['flowrules'].append(copy.deepcopy(j_flowrule))

                j_flowrule = {}
                if port.list_ingoing_label is not None:
                    for ingoing in port.list_ingoing_label:
                        
                        if ingoing.id is not None:
                            j_flowrule['id'] = ingoing.id
                        
                        if ingoing.status is not None:
                            j_flowrule['status'] = ingoing.status
                        
                        if ingoing.internal_id is not None:
                            j_flowrule['internal_id'] = ingoing.internal_id
                        
                        j_flowrule['action'] = {}
                        j_flowrule['action']['type'] = ingoing.action.type
                        if ingoing.action.vnf is not None:
                            j_vnf_action = {}
                            j_vnf_action['id'] = ingoing.action.vnf['id']
                            j_vnf_action['port'] = ingoing.action.vnf['port']
                            j_flowrule['action']['VNF'] = j_vnf_action
                        if ingoing.action.endpoint is not None:
                            j_endpoint_action = {}
                            j_endpoint_action['port'] = getEndpointID(ingoing.action.endpoint)
                            j_flowrule['action']['endpoint'] = j_endpoint_action
                        j_matches = []
                        j_flowspec = {}
                        for match in ingoing.matches:   
                            j_match = match.of_field
                            if match.id is not None:
                                j_match['id'] = match.id
                            if match.priority is not None:
                                j_match['priority'] = match.priority
                            j_matches.append(j_match)
                        j_flowspec['matches'] = j_matches
                        j_flowspec['ingress_endpoint'] = ingoing.flowspec['ingress_endpoint']
                        j_flowrule['flowspec'] = j_flowspec
                        if j_flowrule:
                            j_port['ingoing_label']['flowrules'].append(copy.deepcopy(j_flowrule))
                if len(j_port['ingoing_label']['flowrules']) == 0 and len(j_port['outgoing_label']['flowrules']) == 0:
                    continue
                if len(j_port['ingoing_label']['flowrules']) == 0:
                    del j_port['ingoing_label']
                if len(j_port['outgoing_label']['flowrules']) == 0:
                    del j_port['outgoing_label']
                
                j_ports.append(j_port)
            # TODO: if no flowrules, delete port
            j_vnf['ports'] = j_ports  
            j_list_vnf.append(j_vnf)
        
        for endpoint in self.listEndpoint:
            j_endpoint = {}
            j_endpoint['id'] = endpoint.id
            j_endpoint['name'] = endpoint.name
            
            if endpoint.edge is not False:
                j_endpoint['edge'] = endpoint.edge
            if endpoint.remote_graph_name is not None:
                j_endpoint['remote_graph_name'] = endpoint.remote_graph_name
            if endpoint.remote_id is not None:
                j_endpoint['remote_id'] = endpoint.remote_id
            if endpoint.remote_graph is not None:
                j_endpoint['remote_graph'] = endpoint.remote_graph
            if endpoint.remote_interface is not None:
                j_endpoint['remote_interface'] = endpoint.remote_interface
            if endpoint.endpoint_switch is not None:
                j_endpoint['endpoint_switch'] = endpoint.endpoint_switch._id
            if endpoint.attached is not None:
                j_endpoint['attached'] = endpoint.attached
            if endpoint.connection is not False:
                j_endpoint['connection'] = endpoint.connection
            if endpoint.type is not None:
                j_endpoint['type'] = endpoint.type
            if endpoint.port is not None:
                j_endpoint['port'] = endpoint.port
            if endpoint.interface is not None:
                j_endpoint['interface'] = endpoint.interface
            if endpoint.node is not None:
                j_endpoint['node'] = endpoint.node
            if endpoint.user_mac is not None:
                j_endpoint['user_mac_address'] = endpoint.user_mac
            if len(endpoint.connections) > 0:
                j_endpoint['connections'] = []
                for connection in endpoint.connections:  
                    j_connection = {}
                    j_connection['ext_nf_fg'] = connection.ext_nf_fg
                    j_connection['ext_edge_endpoint'] = connection.ext_edge_endpoint
                    j_endpoint['connections'].append(j_connection)
            j_list_endpoint.append(j_endpoint)
                    
        j_nf_fg['profile']['id']  = self._id
        j_nf_fg['profile']['name']  = self.name
        if hasattr(self, 'zone') and self.zone is not None:
            j_nf_fg['profile']['availability_zone'] = self.zone
        j_nf_fg['profile']['VNFs'] = j_list_vnf
        j_nf_fg['profile']['endpoints'] = j_list_endpoint
        return json.dumps(j_nf_fg)
        
    def adjustPortsOrder(self, switch):
        # Supposing that all switch ports have same label
        num_ports = len(switch.listPort)
        i = 0
        while i <= num_ports:
            found = False
            for port in switch.listPort:
                if int(port.id.split(":")[1]) ==  i:
                    found = True
                    break
            if found == False:
                for port in switch.listPort:
                    if int(port.id.split(":")[1]) >=  num_ports:
                        new_id = port.id.split(":")[0] +":" +str(i)
                        self.changePortID(switch, port._id, new_id)
                        port._id = new_id
            i = i + 1
                        
    def changePortID(self, switch, old_id, new_id):
        for vnf in self.listVNF:
            for port in vnf.listPort:
                for flowrule in port.list_outgoing_label:
                    if flowrule.action.vnf is not None and flowrule.action.vnf['id'] == switch.id and flowrule.action.vnf['port'] == old_id:
                        flowrule.action.vnf['port'] = new_id
                if port.list_ingoing_label is not None:
                    for flowrule in port.list_ingoing_label:
                        if flowrule.action.vnf is not None and flowrule.action.vnf['id'] == switch.id and flowrule.action.vnf['port'] == old_id:
                            flowrule.action.vnf['port'] = new_id
                        
    def getLinks(self):
        links = []
        j_links = {}
        j_links['links'] = []
        visited_link = False
        for vnf in self.listVNF:
            if vnf.name == "Endpoint_Switch":
                
                for port in vnf.listPort:
                    
                    flowrules = port.getDropFlows()
                    if len(flowrules) == 0:
                        continue
                    node1 = Node(vnf.id, port.id)
                    for flowrule in flowrules:
                        flowrule.addIngressPort(node1)
                    link = Link(node1, None, flowrules)
                    links.append(link)  
                    j_links['links'].append(link.getJSON())  
                
            for port in vnf.listPort:
                node1 = Node(vnf.id, port.id)
                #flowrules = port.getVNFPortsFlowruleSendingTrafficToVNFPort() 
                for flowrule in port.list_outgoing_label:
                    if flowrule.action.vnf is not None:
                        node2 = Node(flowrule.action.vnf['id'], flowrule.action.vnf['port'])
                        
                        # insert ingress port in the match of the flowrules
                        flowrules = port.getVNFPortsFlowruleSendingTrafficToVNFPort(flowrule.action.vnf['id'], flowrule.action.vnf['port'])                    
                        for flowrule in flowrules:
                            flowrule.addIngressPort(node1)
                            
                        flowrules1 = self.getVNFByID(flowrule.action.vnf['id']).getPortFromID(flowrule.action.vnf['port']).getVNFPortsFlowruleSendingTrafficToVNFPort(vnf.id, port.id)
                        for flowrule in flowrules1:
                            flowrule.addIngressPort(node2)
                        
                        flowrules = flowrules + flowrules1
                        
                        
                        visited  = False
                        for link in links:
                            """
                            if link.node2.isEqual(node2):
                                visited = True
                            """
                            if link.node2 is not None:
                                if link.node2.isEqual(node1) and link.node1.isEqual(node2):
                                    visited_link = True
                        if visited is not True and visited_link is not True: 
                            link = Link(node1, node2, flowrules)
                            links.append(link)  
                            j_links['links'].append(link.getJSON())  
                            J_f = []
                            for flowrule in flowrules:
                                J_f.append(flowrule.getJSON())
                            #logging.debug(json.dumps(J_f)) 
                        visited_link = False
                    if flowrule.action.endpoint is not None:
                        if self.getEndpointMap()[flowrule.action.endpoint].type is not None:
                            if self.getEndpointMap()[flowrule.action.endpoint].type == "physical":
                                node2 = Node(endpoint = self.getEndpointMap()[getEndpointID(flowrule.action.endpoint)].interface)
                        else:
                            node2 = Node(endpoint = flowrule.action.endpoint['id'])
                        # TODO: insert ingress port in the match of the flowrules
                        flowrules = port.getVNFPortsFlowruleSendingTrafficToEndpoint(flowrule.action.endpoint['id'])
                        for flowrule in flowrules:
                            flowrule.addIngressPort(node1)
                            
                        flowrules1 = port.getIngoingFlowruleToSpecificEndpoint(flowrule.action.endpoint['id'])
                        for flowrule in flowrules1:
                            flowrule.addIngressPort(node2)
                        
                        flowrules = flowrules + flowrules1
                        
                        
                        visited  = False
                        for link in links:
                            """
                            if link.node2.isEqual(node2):
                                visited = True
                                logging.debug("link.node2.isEqual(node2)")
                            """
                            if link.node2.isEqual(node1) and link.node1.isEqual(node2):
                                visited_link = True
                        if visited is not True and visited_link is not True: 
                            link = Link(node1, node2, flowrules)
                            links.append(link)  
                            j_links['links'].append(link.getJSON())
                            J_f = []
                            for flowrule in flowrules:
                                J_f.append(flowrule.getJSON())
                            #logging.debug(json.dumps(J_f))  
                        visited_link = False
                for flowrule in port.list_ingoing_label:
                    # TODO:
                    pass

                        
                    

                    #if flowrule.action.vnf is not None and flowrule.action.vnf['id'] == vnf_id and flowrule.action.vnf['port'] == port_id:
                        #connected_vnfs.append(vnf) 
        logging.debug(json.dumps(j_links))
        logging.debug("")
        return links
            
    def getStatusExitInterface(self):
        return self.getStatusInterface(ISP_EGRESS)
        
    def getStatusIngressInterface(self):
        return self.getStatusInterface(USER_INGRESS)
    
    def getStatusInterface(self, endpoint_name):
        for endpoint in self.listEndpoint:
            if endpoint.name == endpoint_name:
                return True
        return False
    
    def getEndpointThatShouldBeConnected(self):
        endpoints = []
        for endpoint in self.listEndpoint:
            if endpoint.connection is True:   
                endpoints.append(endpoint)
        return endpoints 
    
    def getExitEndpoint(self): 
        return self.getEndpoint(ISP_EGRESS)
    
    def getIngressEndpoint(self):
        return self.getEndpoint(USER_INGRESS)

    def getEndpoint(self, endpoint_name):
        exitEndpoints = []
        for endpoint in self.listEndpoint:
            if endpoint.name == endpoint_name:   
                exitEndpoints.append(endpoint)
        return exitEndpoints 
        
    def getEndpointMap(self):
        if self.endpoint_map == None:
            self.endpoint_map = {}
            for endpoint in self.listEndpoint:
                self.endpoint_map[endpoint.id] = endpoint
        return self.endpoint_map

class Connection(object):
    def __init__(self, ext_nf_fg_id, ext_edge_endpoint):
        self.ext_nf_fg = ext_nf_fg_id
        
        # TODO: I should delete this field. It is useless
        self.ext_edge_endpoint = ext_edge_endpoint
        
class Endpoint(object):
    def __init__(self, endpoint_id, name, connections = [], attached = False, endpoint_switch = None, connection = False,
                  remote_id = None, remote_graph = None, remote_graph_name=None, remote_interface = None, edge = False, endpoint_type = None, port = None,
                   interface = None, node = None, user_mac = None, db_id=None):

        self._id = endpoint_id
        self.name = name
        # Indicate that the endpoint should be connected, but not to anther endpoint
        self.attached = attached
        self.endpoint_switch = endpoint_switch
        # It is used for 1 to n endpoint
        self.connections = connections
        # It is used for 1 to 1 endpoint, also indicate that this port should be connected to remote endpoint
        self.connection = connection
        self.remote_id = remote_id
        self.remote_graph = remote_graph
        self.remote_graph_name = remote_graph_name
        self.edge = edge
        
        # End-point characterization
        self.type = endpoint_type
        self.port = port
        self.interface = interface
        
        '''
        Added for jolnet Component adapter
        '''
        self.user_mac = user_mac
        self.remote_interface = remote_interface
        
        self.node = node
        self.db_id = db_id
            

    @property
    def id(self):
        return self._id
    
    def connectToExternalNF_FGWithoutEdgeEndpoint(self, nf_fg, ext_nf_fg, endpoint_name, endpoint_switch = None, endpoint_port = None):
        '''
        Returns the edge endpoint to connect
        '''
        #TODO: should be moved to /ServiceLayerApplication/common
        ports = nf_fg.getVNFPortsSendingTrafficToEndpoint(self.id)

        if endpoint_port is not None:
            external_port = endpoint_switch.getPortFromID(endpoint_port.id)
            for port in ports:
                for flowrule in port.list_outgoing_label:   
                    if flowrule.action.endpoint is not None and getEndpointID(flowrule.action.endpoint) == self.id:
                        nf_fg.getEndpointMap()[getEndpointID(flowrule.action.endpoint)].type = 'physical'
                        nf_fg.getEndpointMap()[getEndpointID(flowrule.action.endpoint)].interface = external_port.internal_id
            for port in ports:
                for flowrule in port.list_ingoing_label:
                    if 'ingress_endpoint' in flowrule.flowspec and flowrule.flowspec['ingress_endpoint'] == self.id:
                        nf_fg.getEndpointMap()[flowrule.flowspec['ingress_endpoint']].interface = external_port.internal_id
                        nf_fg.getEndpointMap()[flowrule.flowspec['ingress_endpoint']].type = 'physical'
        else:              
            external_ports = ext_nf_fg.getVNFPortsReceivingTrafficFromEndpont(ext_nf_fg.getEndpointFromName(endpoint_name).id)
            for external_port in external_ports:
                # TODO: manage traffic splitters
                for port in ports:
                    for flowrule in port.list_outgoing_label:   
                        if flowrule.action.endpoint is not None and getEndpointID(flowrule.action.endpoint) == self.id:
                            nf_fg.getEndpointMap()[getEndpointID(flowrule.action.endpoint)].type = 'physical'
                            nf_fg.getEndpointMap()[getEndpointID(flowrule.action.endpoint)].interface = external_port.internal_id
                for port in ports:
                    for flowrule in port.list_ingoing_label:
                        if 'ingress_endpoint' in flowrule.flowspec and flowrule.flowspec['ingress_endpoint'] == self.id:
                            nf_fg.getEndpointMap()[flowrule.flowspec['ingress_endpoint']].interface = external_port.internal_id
                            nf_fg.getEndpointMap()[flowrule.flowspec['ingress_endpoint']].type = 'physical'
            
        self.remote_graph_name = ext_nf_fg.name
        self.remote_id = ext_nf_fg.getEndpointFromName(endpoint_name).id
        self.remote_graph = ext_nf_fg._id
        self.connection = True 
             
class VNF(object):
    
    def __init__(self, VNFname, template, vnf_id = None, ports = None, manifest = None, availability_zone=None, status = None, db_id = None, internal_id = None):

        if vnf_id is not None:
            self._id = vnf_id
        else:
            self._id = uuid.uuid4().hex
            
        self.listPort = []
        if ports is not None:
            for port in ports:
                ingoing_label = None
                outgoing_label = None
                internal_id = None
                if 'ingoing_label' in port:
                    ingoing_label = port['ingoing_label']
                if 'outgoing_label' in port:
                    outgoing_label = port['outgoing_label']
                if 'internal_id' in port:
                    internal_id = port['internal_id']
                self.port = Port(port['id'], outgoing_label = outgoing_label, ingoing_label = ingoing_label, vnf_id = self.id, internal_id = internal_id)
                
                self.listPort.append(self.port)
                    
        self.name = VNFname
        self.template = template
        self.manifest = manifest
        self.availability_zone = availability_zone

        self.status = status
        self.db_id = db_id
        self.internal_id = internal_id

        
           
    @property
    def id(self):
        return self._id
    
    def addPort(self, vnf=None, label=None, port_id=None, db_id=None, internal_id=None):
        num = 0
        if label is not None:
            for port in self.listPort:
                if port.id.split(":")[0] == label:
                    num = num + 1
            port = Port(label+":"+str(num), vnf_id = vnf.id, db_id=db_id, internal_id=internal_id)
        elif port_id is not None:
            if vnf is not None:
                port = Port(port_id, vnf_id = vnf.id, db_id=db_id, internal_id=internal_id)
            else:
                port = Port(port_id, db_id=db_id, internal_id=internal_id)
        self.listPort.append(port)
        return port
        
    def getControlPort(self):
        for self.port in self.listPort:
            if self.port.split[0] == "control":
                return self.port
            
    def deleteConnectionsToVNF(self, vnf):

        for port in self.listPort[:]:
            

            for flowrule in port.list_outgoing_label:
                if flowrule.action.vnf is not None and flowrule.action.vnf['id'] == vnf.id:
                    self.listPort.remove(port)
            """
            for flowrule in port.list_ingoing_label[:]:
                if 'ingress_endpoint' in flowrule.flowspec and flowrule.flowspec['ingress_endpoint'] == endpoint.id:
                    port.list_ingoing_label.remove(flowrule)
                    logging.info("NFFG - deleteEndpointConnections - remove info ingoing: "+str(len(port.list_ingoing_label)))
                    logging.info("NFFG - deleteEndpointConnections - remove info outgoing: "+str(len(port.list_outgoing_label)))
            """
            
    def deletePortsWithoutFlows(self):
        ports_without_flowrule = []
        for port in self.listPort:
            if port.list_outgoing_label is None or len(port.list_outgoing_label) == 0:
                if port.list_ingoing_label is None or len(port.list_ingoing_label) == 0:
                    ports_without_flowrule.append(port)
                    
        for port in ports_without_flowrule:
            self.listPort.remove(port)
    
    def getPortFromID(self, port_id):
        for port in self.listPort:
                if port.id == port_id:
                    return port

    def getPortConnectedToEndpoints(self):
        ports = []
        for port in self.listPort:
            if port.checkIfConnectedToEndpoint() is True:
                ports.append(port)
        return ports
       
    def getDropFlows(self):
        flows = []
        for port in self.listPort:
            flows = flows + port.getDropFlows()
        return flows
          
class Link(object):
    def __init__(self, node1, node2, flowrules):
        self.node1 = node1
        self.node2 = node2
        self.flowrules = flowrules
    
    def getJSON(self):
        #j_nf_fg['links'] = {}
        #links = []
        j_link = {}
        j_link['node1'] = {}
        j_link['node2'] = {}
        if self.node1.vnf_id is not None:
            j_link['node1']['vnf_id'] = self.node1.vnf_id
            j_link['node1']['port_id'] = self.node1.port_id
        elif self.node1.interface is not None:
            j_link['node1']['interface'] = self.node1.interface
        elif self.node1.endpoint is not None:
            j_link['node1']['endpoint'] = self.node1.endpoint
        if self.node2 is not None:
            if self.node2.vnf_id is not None:
                j_link['node2']['vnf_id'] = self.node2.vnf_id
                j_link['node2']['port_id'] = self.node2.port_id
            elif self.node2.interface is not None:
                j_link['node2']['interface'] = self.node2.interface
            elif self.node2.endpoint is not None:
                j_link['node2']['endpoint'] = self.node2.endpoint
        return j_link
        
class Node(object):
    def __init__(self, vnf_id = None, port_id = None, interface = None, endpoint = None):   
        if vnf_id is not None:
            self.vnf_id = vnf_id 
            self.port_id = port_id
        else: 
            self.port_id = None
            self.vnf_id = None
            
        if interface is not None:
            self.interface = interface
        else:
            self.interface = None
            
        if endpoint is not None:
            self.endpoint = endpoint
        else:
            self.endpoint = None
            
    def isEqual(self, node):
        if node.vnf_id is not None and node.vnf_id == self.vnf_id:
            if node.port_id is not None and node.port_id == self.port_id:
                return True
        if node.interface is not None and  node.interface == self.interface:
            return True
        if node.endpoint is not None and  node.endpoint == self.endpoint:
            return True
        return False
      
class Port(object):
    
    def __init__(self, port_id, outgoing_label = None, ingoing_label= None, vnf_id = None,  internal_id = None, status = None, db_id=None):
        self._id = port_id
        self.vnf_id = vnf_id
        self.internal_id = internal_id
        self.outgoing_label = {}
        self.list_outgoing_label = []
        self.list_ingoing_label = []
        self.flowrules = []
        self.status = status
        self.db_id=db_id
        if outgoing_label is not None:
            flowrules = []
            for flowrule in outgoing_label['flowrules']:
                flowrules.append(Flowrule(flowrule['id'], flowrule['action'], flowrule['flowspec']))
            self.flowrules = copy.deepcopy(flowrules)
            self.list_outgoing_label = copy.deepcopy(flowrules)
        if ingoing_label is not None:
            flowrules = []
            for flowrule in ingoing_label['flowrules']:      
                flowrules.append(Flowrule(flowrule['id'], flowrule['action'], flowrule['flowspec']))
            self.flowrules = copy.deepcopy(flowrules)
            self.list_ingoing_label = copy.deepcopy(flowrules)
           
    @property            
    def id(self):
        return self._id
    
    def checkIfConnectedToEndpoint(self):
        for flowrule in self.list_ingoing_label:
            if 'ingress_endpoint' in flowrule.flowspec:
                return True
        for flowrule in self.list_outgoing_label:
            if flowrule.action.endpoint is not None:
                return True         
        return False
            
    def deleteIngoingRule(self, endpoint_id):
        for flowrule in self.list_ingoing_label:
            if 'ingress_endpoint' in flowrule.flowspec and flowrule.flowspec['ingress_endpoint'] == endpoint_id:
                self.list_ingoing_label.remove(flowrule)
          
    def deleteIngoingRuleByMac(self, endpoint_id, mac_address):
        for flowrule in self.list_ingoing_label:
            if 'ingress_endpoint' in flowrule.flowspec and flowrule.flowspec['ingress_endpoint'] == endpoint_id:
                for match in flowrule.flowspec['matches']:
                    if "sourceMAC" in match.of_field:         
                        if match.of_field['sourceMAC'] == mac_address:
                            self.list_ingoing_label.remove(flowrule)
    
    def deleteConnectionToEndpoint(self, endpoint_id):
        for flowrule in self.list_outgoing_label:
            if flowrule.action.endpoint is not None and getEndpointID(flowrule.action.endpoint) == endpoint_id:
                self.list_outgoing_label.remove(flowrule)
            
        for flowrule in self.list_ingoing_label:
            if 'ingress_endpoint' in flowrule.flowspec and flowrule.flowspec['ingress_endpoint'] == endpoint_id:
                self.list_ingoing_label.remove(flowrule)
             
    def getVNFPortsFlowruleSendingTrafficToEndpoint(self, endpoint_id):
        flowrules = []
        for flowrule in self.list_outgoing_label:  
            if flowrule.action.endpoint is not None and getEndpointID(flowrule.action.endpoint) == endpoint_id:
                flowrules.append(flowrule) 
        return flowrules
    
    def getVNFPortsFlowruleSendingTrafficToVNFPort(self, vnf_id, port_id):
        flowrules  = []
        for flowrule in self.list_outgoing_label:
            if flowrule.action.vnf is not None and flowrule.action.vnf['id'] == vnf_id and flowrule.action.vnf['port'] == port_id:
                flowrules.append(flowrule) 
        return flowrules
     
    def getIngoingFlowruleToSpecificEndpoint(self, endpoint_id):
        flowrules = []
        for flowrule in self.list_ingoing_label:
            if 'ingress_endpoint' in flowrule.flowspec and flowrule.flowspec['ingress_endpoint'] == endpoint_id:
                flowrules.append(flowrule)
        return flowrules
    
    def setFlowRuleToEndpoint(self, endpoint_id, db_id=None, internal_id=None, flowrule_id=None):
        if flowrule_id is None:
            flowrule_id = uuid.uuid4().hex
        matches = []
        matches.append(Match(priority = DEFAULT_PRIORITY, match_id = uuid.uuid4().hex))
        endpoint_pointer  = {}
        endpoint_pointer['port'] = endpoint_id
        action = Action("output", endpoint = endpoint_pointer)
        flowrule = Flowrule(flowrule_id, action, matches = matches, db_id=db_id, internal_id=internal_id)
        self.list_outgoing_label.append(flowrule)
        self.flowrules.append(flowrule)
        return flowrule
        
    def setFlowRuleFromEndpoint(self, vnf_id, endpoint_id, db_id=None, internal_id=None, flowrule_id=None):
        if flowrule_id is None:
            flowrule_id = uuid.uuid4().hex
        matches = []
        matches.append(Match(priority = DEFAULT_PRIORITY, match_id = uuid.uuid4().hex))
        vnf_pointer  = {}
        vnf_pointer['id'] = vnf_id
        vnf_pointer['port'] = self.id
        action = Action("output", vnf = vnf_pointer)
        flowrule = Flowrule(flowrule_id, action, matches = matches, ingress_endpoint = endpoint_id, db_id=db_id, internal_id=internal_id)
        self.list_ingoing_label.append(flowrule)
        self.flowrules.append(flowrule)
        return flowrule
        
    def setFlowRuleToVNF(self, vnf_id, port_id, db_id=None, internal_id=None, flowrule_id=None):
        if flowrule_id is None:
            flowrule_id = uuid.uuid4().hex
        matches = []
        matches.append(Match(priority = DEFAULT_PRIORITY, match_id = uuid.uuid4().hex))
        vnf_pointer  = {}
        vnf_pointer['id'] = vnf_id
        vnf_pointer['port'] = port_id
        action = Action("output", vnf_pointer)
        flowrule = Flowrule(flowrule_id, action, matches = matches, db_id=db_id, internal_id=internal_id)
        self.list_outgoing_label.append(flowrule)
        self.flowrules.append(flowrule)
        return flowrule
        
    def setDropFlow(self, flowrule_id=None):
        if flowrule_id is None:
            flowrule_id = uuid.uuid4().hex
        matches = []
        matches.append(Match(priority = 1, match_id = uuid.uuid4().hex))
        action = Action("drop")
        flowrule = Flowrule(flowrule_id, action, matches = matches)
        self.list_outgoing_label.append(flowrule)
        self.flowrules.append(flowrule)
    
    def getDropFlows(self):
        flowrules = []
        for flowrule in self.list_outgoing_label:
            if flowrule.action.type  == 'drop':
                flowrules.append(flowrule) 
        return flowrules
               
class Flowrule(object):
    def __init__(self, flowrule_id, action, flowspec = None, matches = None, ingress_endpoint = None, status = None, db_id=None, internal_id=None):
        self._id = flowrule_id
        self.flowspec = {}
        self.matches = []
        self.flowspec['matches'] = self.matches 
        self.status = status
        self.db_id=db_id
        self.internal_id=internal_id
        if flowspec is not None and 'ingress_endpoint' in flowspec:
            self.flowspec['ingress_endpoint'] = flowspec['ingress_endpoint']
        if isinstance(action, Action):
            self.action = action
        elif "VNF" in action:
            self.action = Action(action['type'], vnf = action['VNF'])
        elif "endpoint" in action:
            self.action = Action(action['type'], endpoint = action['endpoint'])
            
        if ingress_endpoint is not None:
            self.flowspec['ingress_endpoint'] = ingress_endpoint
          
        if flowspec is not None:  
            for match in flowspec['matches']:
                priority = match['priority']
                match_id = match['id']
                of_field = match
                del of_field['id']
                del of_field['priority']
                
                if of_field is True:
                    of_field = None
                self.match = Match(priority = priority, 
                                   match_id = match_id,
                                   of_field = of_field)
                self.matches.append(self.match)
        elif matches is not None:
            self.matches = matches
    
    @property
    def id(self):
        return self._id
    
    def changeMatches(self, matches):
        if matches:
            self.matches = matches
        else:
            self.matches = []
    
    def changeAction(self, action):    
        self.action = action
        
    def addIngressPort(self, node):
        if node.vnf_id is not None:
            self.flowspec['source_VNF_id'] = node.vnf_id 
            self.flowspec['ingressPort'] = node.port_id
            
        if node.endpoint is not None:
            self.flowspec['ingressPort'] = node.endpoint
    
    def getJSON(self):
        j_flowrule = {}
        if hasattr(self, 'id'): 
            j_flowrule['id'] = self.id
        j_flowrule['action'] = {}
        j_flowrule['action']['type'] = self.action.type
        if self.action.vnf is not None:
            j_vnf_action = {}
            j_vnf_action['id'] = self.action.vnf['id']
            j_vnf_action['port'] = self.action.vnf['port']
            j_flowrule['action']['VNF'] = j_vnf_action
        if self.action.endpoint is not None:
            j_endpoint_action = {}
            j_endpoint_action['id'] = getEndpointID(self.action.endpoint)
            if 'type' in self.action.endpoint:
                j_endpoint_action['type'] = self.action.endpoint['type']
            if 'interface' in self.action.endpoint:
                j_endpoint_action['interface'] = self.action.endpoint['interface']
            j_flowrule['action']['endpoint'] = j_endpoint_action
            
        j_matches = []
        j_flowspec = {}
        for match in self.matches:  
            if match.of_field is not None:
                j_match = match.of_field
            else:
                j_match = {}
            if match.id is not None:
                j_match['id'] = match.id
            if match.priority is not None:
                j_match['priority'] = match.priority
            
            j_matches.append(j_match)
        j_flowspec['matches'] = j_matches
        j_flowrule['flowspec'] = j_flowspec
        if 'ingressPort'  in self.flowspec:
            j_flowrule['flowspec']['ingressPort'] = self.flowspec['ingressPort']
        if 'source_VNF_id'  in self.flowspec:
            j_flowrule['flowspec']['source_VNF_id'] = self.flowspec['source_VNF_id']
        return j_flowrule
    
class Action(object):
    def __init__(self, action_type, vnf = None, endpoint = None, graph_id = None):
        self.type = action_type
        self.vnf = {}
        self.endpoint = {}
        if vnf is not None:
            self.vnf['id'] = vnf['id']
            self.vnf['port'] = vnf['port']
        else:
            self.vnf = None
        if endpoint is not None:
            self.endpoint['id'] = getEndpointID(endpoint)
            if 'interface' in endpoint:
                self.endpoint['interface'] = endpoint['interface']
            if 'type' in endpoint:
                self.endpoint['type'] = endpoint['type']
        else:
            self.endpoint = None
    
class Match(object):
    def __init__(self, 
                        priority = None,
                        match_id = None,
                        of_field = None,
                        db_id = None):
        
        self.of_field = {}
        if of_field is not None:
            self.of_field = of_field
        
        
        self.priority = priority
        self._id = match_id
        self.db_id = db_id
        
    @property
    def id(self):
        return self._id
        
        
        
def getEndpointID(endpoint):
    if 'id' in endpoint:
        return endpoint['id']
    if 'port' in endpoint:
        return endpoint['port']
