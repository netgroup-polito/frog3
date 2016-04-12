'''
Created on 08 ott 2015

@author: stefanopetrangeli
'''

import json
import logging

class ProfileGraph(object):
    def __init__(self):
        self._id = None
        self.VNFs = {}
        self.endpoints = {}

    def addVNF(self, vnf):
        self.VNFs[vnf.id] = vnf

    def addEndpoint(self, endpoint):
        self.endpoints[endpoint.id] = endpoint
        
    @property
    def id(self):
        return self._id
    
    def setId(self, profile_id):
        self._id = profile_id
        
        
class FlowGraph(object):
    
    def __init__(self):
        """
        graph = {}
        graph["flow-graph"] = {}
        graph["flow-graph"]["VNFs"] = []
        graph["flow-graph"]["flow-rules"] = []
        """
        
        self.VNFs = []
        self.flowrules = []
        
    def addVNF(self, vnf):
        nf = {}
        nf['id'] = vnf
        self.VNFs.append(nf)

    def addFlowrule(self, flowrule):
        self.flowrules.append(flowrule)
        
    def getJSON(self):
        graph = {}
        graph["flow-graph"] = {}
        graph["flow-graph"]["VNFs"] = self.VNFs
        graph["flow-graph"]["flow-rules"] = self.flowrules
        
        return graph
    
"""   
class Endpointtt(object):

    def __init__(self, unify, profile):
        
        logging.debug("Unify - Endpoint - self.profile\n\n"+json.dumps(self.profile))
        
        
        for endpoint in nf_fg.listEndpoint:
            if endpoint.connection is False and endpoint.attached is False and endpoint.edge is False:
                edge_endpoints = nf_fg.getEdgeEndpoint(endpoint.name, True)
                logging.debug("NF-FG name: "+nf_fg.name)
                logging.debug("Endpoint - endpoint.name: "+endpoint.name)
                    
                # Write in DB endpoint 1 to n
                '''
                for edge_endpoint in edge_endpoints:
                    set_endpoint(nf_fg._id, edge_endpoint.id, True, endpoint.name, endpoint._id, endpoint_type="endpoint")   
                '''
                
            if endpoint.connection is True:
                nf_fg.characterizeEndpoint(endpoint, endpoint_id=endpoint.remote_graph+":"+endpoint.remote_id)
    
        self.nf_fg = json.loads(nf_fg.getJSON())
        #logging.debug("Unify - Endpoint - self.nf_fg\n\n"+json.dumps(self.nf_fg))
        
    def defineIngress(self):
        pass
"""  
        
class VNF(object):
    '''
    Class that contains the VNF data that will be used on the profile generation
    '''
    def __init__(self, VNFId, vnf, status='new'):
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
        self._id = VNFId
        self.name = vnf.name
        self.ports = {}
        self.listPort = vnf.listPort
        self.status = status
        self.ports_label = VNFTemplate(vnf).ports_label

    
    @property
    def id(self):
        return self._id

class VNFTemplate(object):

    def __init__(self, vnf):
        self.ports_label = {}
        self.id = vnf.id
        template = vnf.manifest
        for port in template['ports']:
            tmp = int(port['position'].split("-")[0])
            self.ports_label[port['label']] = tmp