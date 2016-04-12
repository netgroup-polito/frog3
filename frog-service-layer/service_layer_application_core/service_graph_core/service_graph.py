'''
Created on Oct 25, 2014

@author: fabiomignini
'''

from Common.NF_FG.nf_fg import NF_FG
from Common.exception import EndpointConnectionError
import json

lan_label = "L2"
switch_template = "switch.json"
default_priority = 32770

class ServiceGraph(object):
    """
    Represent the service Graph
    """
    def __init__(self, graph = None):
        self.graph = graph
        self.user_id = None
        self.traffic_splitter_list = []
        self.lan_list = []
        self.endpoint_list = []
        self.vnf_list = []
        self.link_list = []
    
    def getNF_FG(self):
        return NF_FG(self.graph)
    
    def loads(self, graph):

        for vnf_id, vnf in graph['vnf_list'].iteritems():
            port_list = []
            for port in vnf['ports']:
                for idx in str(port['cnt']):
                    port_list.append(Port(str(int(idx)-1), port['label']))
            self.vnf_list.append(VirtualNetworkFunction(vnf_id, vnf['vnfDesc']['name'], port_list))
            
        for traffic_splitter_id, traffic_splitter in graph['splitter_list'].iteritems():
            link_list = []
            for rule in traffic_splitter['rules']:
                link_id = traffic_splitter['rules'].index(rule)
                link_list.append(Link(link_id, Node('splitter', traffic_splitter_id, port_id = str(int(rule['in'])-1)), 
                                 Node('splitter', traffic_splitter_id, port_id = str(int(rule['out'])-1)), 
                                 flowspec = FlowSpec(rule['priority'], rule['settings']['macsrc'],
                                                      rule['settings']['macdst'], rule['settings']['ipsrc'],
                                                      rule['settings']['ipdst'], rule['settings']['vlanid'],
                                                      rule['settings']['portsrc'], rule['settings']['portdst'],
                                                      rule['settings']['protocol']),
                                 directed = True))
            self.traffic_splitter_list.append(TrafficSplitter(traffic_splitter_id, 
                                            traffic_splitter['num_inout'],
                                             link_list))
            
        for endpoint_id, endpoint in graph['endpoint_list'].iteritems():
            self.endpoint_list.append(Endpoint(endpoint_id,endpoint['type']))
            
        for lan_id, lan in graph['lan_list'].iteritems():
            self.lan_list.append(LocalAreaNetwork(lan['id']))
            
        for link_id, link in graph['link_list'].iteritems():
            elem1_port_id = None
            elem2_port_id = None
            elem1_label = None
            elem2_label = None
            if link['elem1']['type'] == 'vnf':
                elem1_port_id = link['elem1']['port'].rpartition('_')[2]
                elem1_label = link['elem1']['port'].rpartition('-')[2].rpartition('_')[0]
            if link['elem1']['type'] == 'splittermerger':
                elem1_port_id = link['elem1']['port'].rpartition('_')[2]
            if link['elem2']['type'] == 'vnf':
                elem2_port_id = link['elem2']['port'].rpartition('_')[2]
                elem2_label = link['elem2']['port'].rpartition('-')[2].rpartition('_')[0]
            if link['elem2']['type'] == 'splittermerger':
                elem1_port_id = link['elem2']['port'].rpartition('_')[2]
            self.link_list.append(Link(link_id, Node(link['elem1']['type'], link['elem1']['id'], port_id=elem1_port_id, label=elem1_label), 
                                 Node(link['elem2']['type'], link['elem2']['id'], port_id=elem2_port_id, label=elem2_label)))
            
    def dumps(self):
        sg = None
        return sg
        
    
        
    def transformLANs(self):
        for lan in self.lan_list:
            port_list = []
            for link in self.link_list:
                if link.node1.isLAN() is True:
                    if link.node1.node_id == lan.lan_id:
                        port_id = link.link_id.split('_')[1]
                        port_list.append(Port(port_id, lan_label))
                        link.node1.port_id = port_id
                        link.node1.label = lan_label
                        link.node1.setAsVNF()
                if link.node2.isLAN() is True:
                    if link.node2.node_id == lan.lan_id:
                        port_id = link.link_id.split('_')[1]
                        port_list.append(Port(port_id, lan_label))
                        link.node2.port_id = port_id
                        link.node2.label = lan_label
                        link.node2.setAsVNF()
            self.vnf_list.append(VirtualNetworkFunction(lan.lan_id, 'switch', port_list))
    
    def getNetworkFunctionForwardingGraph(self, encode=True):
        self.transformLANs()
        splitter_dict = {}
        for splitter in self.traffic_splitter_list:
            print "    - "+splitter.traffic_splitter_id
            splitter_dict[splitter.traffic_splitter_id] = splitter
        
        nffg = {}
        nffg['profile'] = {}
        nffg['profile']['id'] = self.user_id
        nffg['profile']['name'] = self.user_id
        vnfs = []
        for vnf in self.vnf_list:
            vnf_obj = {}
            vnf_obj['vnf_descriptor'] = vnf.name+'.json'
            vnf_obj['id'] = vnf.id
            vnf_obj['name'] = vnf.name
            vnf_obj['ports'] = []
            for port in vnf.port_list:
                port_obj = {}
                port_obj['id'] = port.label+":"+str(port.port_id)
                outgoing_flowrules_obj = []
                ingoing_flowrules_obj = []
                for link in self.link_list:
                    self.createFlowrule(link.node1, link.node2, vnf, port, splitter_dict, outgoing_flowrules_obj, ingoing_flowrules_obj)
                    self.createFlowrule(link.node2, link.node1, vnf, port, splitter_dict, outgoing_flowrules_obj, ingoing_flowrules_obj)
                    
                if len(outgoing_flowrules_obj) != 0:
                    port_obj['outgoing_label'] = {}
                    port_obj['outgoing_label']['flowrules'] = outgoing_flowrules_obj
                if len(ingoing_flowrules_obj) != 0:
                    port_obj['ingoing_label'] = {}
                    port_obj['ingoing_label']['flowrules'] = ingoing_flowrules_obj
                vnf_obj['ports'].append(port_obj)
            vnfs.append(vnf_obj)
        nffg['profile']['VNFs'] = vnfs
        endpoints = []
        for endpoint in self.endpoint_list:
            endpoint_obj = {}
            endpoint_obj['id'] = endpoint.endpoint_id
            endpoint_obj['name'] = endpoint.endpoint_type
            endpoints.append(endpoint_obj)
        nffg['profile']['endpoints'] = endpoints
        if encode:
            return json.dumps(nffg, sort_keys=True).encode()
        else:
            return nffg
    
    def createFlowrule(self, node_a, node_b, vnf, port, splitter_dict, outgoing_flowrules_obj, ingoing_flowrules_obj):
        # Warning: in the NFFG in use, can't be directly connected two end-points
        if node_a.isVNF() and node_a.node_id == vnf.id and node_a.port_id == port.port_id and node_a.label == port.label:
            if node_b.isVNF():
                # TODO: match id
                match_id = ""
                outgoing_flowrules_obj.append(self.setFlowruleToVNF(node_b.node_id, str(node_b.label)+':'+str(node_b.port_id), match_id))
            if node_b.isEndpoint():
                # TODO: match id
                match_id = ""
                outgoing_flowrules_obj.append(self.setFlowruleToEndpoint(node_b.node_id, match_id))
                ingoing_flowrules_obj.append(self.setFlowruleFromEndpoint(node_b.node_id, match_id, node_a.node_id,  str(node_a.label)+':'+ str(node_a.port_id)))
            if node_b.isTrafficSplitter():
                self.getConnectionFromTrafficSplitter(node_b.node_id, splitter_dict, vnf, port, outgoing_flowrules_obj, ingoing_flowrules_obj)

                '''
                outgoing_links = splitter_dict[node_b.node_id].getOutgoingConnection(node_b.port_id) 
                #ingoing_links = splitter_dict[link.node2.node_id].getIngoingConnection(link.node2.port_id)
                for outgoing_link in outgoing_links:
                    connected_objects = self.getConnectedObjects(outgoing_link.node2)
                    assert len(connected_objects) != 0
                    for connected_object in connected_objects:
                        if connected_object.isVNF():
                            # TODO: match id
                            match_id = ""
                            outgoing_flowrules_obj.append(self.setFlowruleToVNF(connected_object.node_id,  str(connected_object.label)+':'+str(connected_object.port_id), match_id, flowspec = outgoing_link.flowspec))
                        if connected_object.isEndpoint():
                            # TODO: match id
                            match_id = ""
                            outgoing_flowrules_obj.append(self.setFlowruleToEndpoint(connected_object.node_id, match_id))
                            object_connected_to_endpoints = self.getConnectedObjects(connected_object)
                            for object_connected_to_endpoint in object_connected_to_endpoints:
                                if object_connected_to_endpoint.isVNF():
                                    ingoing_flowrules_obj.append(self.setFlowruleFromEndpoint(connected_object.node_id, match_id, vnf.id,  port.label+":"+str(port.port_id)))
                                else:
                                    raise EndpointConnectionError("End-point connected directly to another end end-point")
                '''
        '''
        if node_a.isTrafficSplitter():
            connected_objects = self.getConnectedObjects(node_a)
            assert len(connected_objects) != 0
            for connected_object in connected_objects:          
                if connected_object.isVNF() and connected_object.node_id == vnf.id and connected_object.port_id == port.port_id and connected_object.label == port.label:
                    # At this point i should follow the flows from the port of the TS, connected to the port 'connected_object.port_id', to find out the VNFs connected to that port.
                    outgoing_links = splitter_dict[node_b.node_id].getOutgoingConnection(node_b.port_id) 
                    for outgoing_link in outgoing_links:
                        if connected_object.isTrafficSplitter():
                            self.getConnectionFromTrafficSplitter(node_b.node_id, splitter_dict, vnf, port, outgoing_flowrules_obj, ingoing_flowrules_obj)

        '''

    def getConnectionFromTrafficSplitter(self, traffic_splitter_id, splitter_dict, vnf, port, outgoing_flowrules_obj, ingoing_flowrules_obj):
        outgoing_links = splitter_dict[traffic_splitter_id].getOutgoingConnection(traffic_splitter_id) 
        #ingoing_links = splitter_dict[link.node2.node_id].getIngoingConnection(link.node2.port_id)
        for outgoing_link in outgoing_links:
            connected_objects = self.getConnectedObjects(outgoing_link.node2)
            assert len(connected_objects) != 0
            for connected_object in connected_objects:
                if connected_object.isVNF():
                    # TODO: match id
                    match_id = ""
                    outgoing_flowrules_obj.append(self.setFlowruleToVNF(connected_object.node_id,  str(connected_object.label)+':'+str(connected_object.port_id), match_id, flowspec = outgoing_link.flowspec))
                if connected_object.isEndpoint():
                    # TODO: match id
                    match_id = ""
                    outgoing_flowrules_obj.append(self.setFlowruleToEndpoint(connected_object.node_id, match_id))
                    object_connected_to_endpoints = self.getConnectedObjects(connected_object)
                    for object_connected_to_endpoint in object_connected_to_endpoints:
                        if object_connected_to_endpoint.isVNF():
                            ingoing_flowrules_obj.append(self.setFlowruleFromEndpoint(connected_object.node_id, match_id, vnf.id,  port.label+":"+str(port.port_id)))
                        else:
                            raise EndpointConnectionError("End-point connected directly to another end end-point")
                if connected_object.isTrafficSplitter():
                    print "Traffic Splitters connected to each other"
                    self.getConnectionFromTrafficSplitter(connected_object.port_id, splitter_dict, vnf, port, outgoing_flowrules_obj, ingoing_flowrules_obj)
                        
                                            
    def getConnectedObjects(self, node):
        connectedObjects = []
        # TODO: manage the case in which a traffic splitter is connected to another traffic splitter
        for link in self.link_list:
            if link.node1.isTrafficSplitter() and str(link.node1.node_id) == str(node.node_id) and str(link.node1.port_id) == str(node.port_id):
                connectedObjects.append(link.node2)
            if link.node2.isTrafficSplitter() and str(link.node2.node_id) == str(node.node_id) and str(link.node2.port_id) == str(node.port_id):
                connectedObjects(link.node1)
        return connectedObjects
     
    def setFlowruleFromEndpoint(self, endpoint_id, match_id, vnf, port, priority=None):
        flowrule = {}
        flowrule['action'] = {}
        flowrule['action']['VNF'] = {}
        flowrule['action']['VNF']['id'] = vnf
        flowrule['action']['VNF']['port'] = port
        flowrule['action']['type'] =  "output"
        flowrule['flowspec'] = {}
        flowrule['flowspec']['matches'] = []
        match = {}
        if priority is None:
            match['priority'] = default_priority
        else:
            match['priority'] = priority
        match['id'] = match_id
        flowrule['flowspec']['matches'].append(match)
        flowrule['ingress_endpoint'] = endpoint_id
        return flowrule
    
    def setFlowruleToEndpoint(self, endpoint_id, match_id, priority=None):
        flowrule = {}
        flowrule['action'] = {}
        flowrule['action']['endpoint'] = {}
        flowrule['action']['endpoint']['id'] = endpoint_id
        flowrule['action']['type'] =  "output"
        flowrule['flowspec'] = {}
        flowrule['flowspec']['matches'] = []
        match = {}
        if priority is None:
            match['priority'] = default_priority
        else:
            match['priority'] = priority
        match['id'] = match_id
        flowrule['flowspec']['matches'].append(match)
        return flowrule
    
    def setFlowruleToVNF(self, output_vnf, output_port, match_id, flowspec=None):
        flowrule = {}
        flowrule['action'] = {}
        flowrule['action']['VNF'] = {}
        flowrule['action']['VNF']['id'] = output_vnf
        flowrule['action']['VNF']['port'] = output_port
        flowrule['action']['type'] =  "output"
        flowrule['flowspec'] = {}
        flowrule['flowspec']['matches'] = []
        match = {}
  
        match['priority'] = default_priority
        
        match['id'] = match_id
        flowrule['flowspec']['matches'].append(match)
        return flowrule
    
class VirtualNetworkFunction(object):
    def __init__(self, vnf_id, name, port_list):
        self.id = vnf_id
        self.name = name
        self.port_list = port_list
        self.template = None

class Port():
    def __init__(self, port_id, label):
        self.port_id = port_id
        self.label = label

class TrafficSplitter(object):
    '''
    Traffic splitter or big switch??
    '''
    def __init__(self, traffic_splitter_id, number_of_ports, links):
        self.traffic_splitter_id = traffic_splitter_id
        self.number_of_ports = number_of_ports
        self.links = links
        
    def getIngoingConnection(self, port):
        ingoing_link = []
        for link in self.links:
            if str(link.node2.port_id) == str(port):
                ingoing_link.append(link)
        return ingoing_link
    
    def getOutgoingConnection(self, port):
        outgoing_link = []
        for link in self.links:
            if str(link.node1.port_id) == str(port):
                outgoing_link.append(link)
        return outgoing_link

class Endpoint(object):
    def __init__(self, endpoint_id, endpoint_type):
        self.endpoint_id = endpoint_id
        self.endpoint_type = endpoint_type

class LocalAreaNetwork(object):
    def __init__(self, lan_id):
        self.lan_id = lan_id

class Link(object):
    '''
    directed or undirected edge
    '''
    def __init__(self, link_id, node1, node2, flowspec = None, directed = False):
        self.link_id = link_id
        self.node1 = node1
        self.node2 = node2
        self.flowspec = flowspec
        self.directed = directed

class Node(object):
    def __init__(self, node_type, node_id, port_id = None, label = None):
        self.node_type = node_type
        self.node_id = node_id
        self.port_id = port_id
        self.label = label
        
    def isVNF(self):
        if self.node_type == 'vnf':
            return True
        return False
    
    def isLAN(self):
        if self.node_type == 'lan':
            return True
        return False
    
    def isTrafficSplitter(self):
        if self.node_type == 'splittermerger':
            return True
        return False
        
    def isEndpoint(self):
        if self.node_type == 'endpoint':
            return True
        return False
        
    def setAsVNF(self):
        self.node_type = 'vnf'
        
class FlowSpec(object):
    def __init__(self, priority, macsrc=None, macdst=None, ipsrc=None, ipdst=None,
                  vlanid=None, portsrc=None, portdst=None, protocol=None):
        self.priority = priority
        self.macsrc = macsrc
        self.macdst = macdst
        self.ipsrc = ipsrc
        self.ipdst = ipdst
        self.vlanid = vlanid
        self.portsrc = portsrc
        self.portdst = portdst
        self.protocol = protocol


