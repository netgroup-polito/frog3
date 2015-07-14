import uuid
import json
import logging
import copy

DEFAULT_PRIORITY = '1000'

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
            
            if endpoint.status is not None:
                j_endpoint['status'] = endpoint.status
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
        
    
class Connection(object):
    def __init__(self, ext_nf_fg_id, ext_edge_endpoint):
        self.ext_nf_fg = ext_nf_fg_id
        
        # TODO: I should delete this field. It is useless
        self.ext_edge_endpoint = ext_edge_endpoint
        
class Endpoint(object):
    def __init__(self, endpoint_id, name, connections = [], attached = False, endpoint_switch = None, connection = False,
                  remote_id = None, remote_graph = None, remote_graph_name=None, remote_interface = None, edge = False, endpoint_type = None, port = None,
                   interface = None, node = None, user_mac = None, db_id=None, status=None):

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
        self.status = status
            

    @property
    def id(self):
        return self._id
             
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
    
    def addPort(self, vnf=None, label=None, port_id=None, db_id=None, internal_id=None, type=None):
        num = 0
        if label is not None:
            for port in self.listPort:
                if port.id.split(":")[0] == label:
                    num = num + 1
            port = Port(label+":"+str(num), vnf_id = vnf.id, db_id=db_id, internal_id=internal_id, type=type)
        elif port_id is not None:
            if vnf is not None:
                port = Port(port_id, vnf_id = vnf.id, db_id=db_id, internal_id=internal_id, type=type)
            else:
                port = Port(port_id, db_id=db_id, internal_id=internal_id, type=type)
        self.listPort.append(port)
        return port

class Port(object):
    
    def __init__(self, port_id, outgoing_label = None, ingoing_label= None, vnf_id = None,  internal_id = None, status = None, db_id=None, type=None):
        self._id = port_id
        self.vnf_id = vnf_id
        self.internal_id = internal_id
        self.outgoing_label = {}
        self.list_outgoing_label = []
        self.list_ingoing_label = []
        self.flowrules = []
        self.status = status
        self.db_id = db_id
        self.type = type
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
        matches.append(Match(priority =DEFAULT_PRIORITY, match_id = uuid.uuid4().hex))
        vnf_pointer  = {}
        vnf_pointer['id'] = vnf_id
        vnf_pointer['port'] = port_id
        action = Action("output", vnf_pointer)
        flowrule = Flowrule(flowrule_id, action, matches = matches, db_id=db_id, internal_id=internal_id)
        self.list_outgoing_label.append(flowrule)
        self.flowrules.append(flowrule)
        return flowrule
   
               
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
