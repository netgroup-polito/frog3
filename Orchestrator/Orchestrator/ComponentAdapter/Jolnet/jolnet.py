'''
Created on 13/apr/2015
@author: vida
'''

import logging
import json

from Common.config import Configuration
from Common.Manifest.manifest import Manifest
from Common.exception import StackError
from Common.SQL.graph import Graph
from Common.SQL.session import Session
from Common.SQL.node import Node

from Orchestrator.ComponentAdapter.interfaces import OrchestratorInterface
from Orchestrator.ComponentAdapter.Jolnet.rest import ODL, Glance, Nova, Neutron
from Orchestrator.ComponentAdapter.Jolnet.resources import Action, Match, Flow, ProfileGraph, VNF


DEBUG_MODE = Configuration().DEBUG_MODE

class JolnetAdapter(OrchestratorInterface):
    '''
    Override class of the abstract class OrchestratorInterface
    '''
    
    def __init__(self, session_id, compute_node_address, token):
        '''
        Initialize the Jolnet component adapter
        Args:
            session_id:
                identifier for the current user session
            compute_node_address:
                address of the compute node where to deploy the graph (can change at every graph)
            token:
                OpenStack access token of the orchestration user
        '''
        self.session_id = session_id
        self.token = token
        self.compute_node_address = compute_node_address
        self._URI = "http://" + compute_node_address
        self.novaEndpoint = token.get_endpoints('compute')[0]['publicURL']
        self.glanceEndpoint = token.get_endpoints('image')[0]['publicURL']
        self.neutronEndpoint = token.get_endpoints('network')[0]['publicURL']
        
        logging.debug(self._URI)    
        if DEBUG_MODE is True:
            logging.debug(self.novaEndpoint)
            logging.debug(self.glanceEndpoint)
            logging.debug(self.neutronEndpoint)
    
    @property
    def URI(self):
        return self._URI
    
    '''
    ######################################################################################################
    #########################    Orchestrator interface implementation        ############################
    ######################################################################################################
    '''
    def getStatus(self, session_id, node_endpoint):
        #TODO:
        pass
    
    def instantiateProfile(self, nf_fg, node_endpoint):
        '''
        Override method of the abstract class for instantiating the user Stack
        '''
        self.node_endpoint = node_endpoint
        
        if DEBUG_MODE is True:
            logging.debug("Forwarding graph: " + nf_fg.getJSON())
        try:            
            #Read the nf_fg JSON structure and map it into the proper objects and db entries
            profile_graph = self.buildProfileGraph(nf_fg)
            self.openstackResourcesInstantiation(profile_graph, nf_fg)
            logging.debug("Graph " + profile_graph.id + "correctly instantiated!")
            
        except Exception as err:
            logging.error(err.message)
            logging.exception(err) 
            raise
    
    def updateProfile(self, new_nf_fg, old_nf_fg, token, node_endpoint):
        pass
        
    def deinstantiateProfile(self, nf_fg, node_endpoint):
        '''
        Override method of the abstract class for deleting the user Stack
        '''
        self.node_endpoint = node_endpoint
        
        if DEBUG_MODE is True:
            logging.debug("Forwarding graph: " + nf_fg.getJSON())
        
        try:
            self.openstackResourcesDeletion()
            logging.debug("Graph " + nf_fg.id + "correctly deleted!") 
        except Exception as err:
            logging.error(err.message)
            logging.exception(err) 
            raise
    
    def buildProfileGraph(self, nf_fg):
        profile_graph = ProfileGraph()
        profile_graph.setId(nf_fg.id)
                
        #Get the necessary info (glance URI and Nova flavor) and create a VNF object
        for vnf in nf_fg.listVNF:
            manifest = Manifest(vnf.manifest)
            cpuRequirements = manifest.CPUrequirements.socket
            if DEBUG_MODE is True:
                logging.debug(manifest.uri)
            image = Glance().getImage(manifest.uri, self.token.get_token())
            flavor = self.findFlavor(int(manifest.memorySize), int(manifest.rootFileSystemSize),
                    int(manifest.ephemeralFileSystemSize), int(cpuRequirements[0]['coreNumbers']), self.token.get_token())
            nf = VNF(vnf.id, vnf, image, flavor, vnf.availability_zone)
            profile_graph.addVNF(nf)
                
        #Complete all ports with the right Neutron network id and add them to the VNF
        #This is necessary because the network are already present (create them on the fly would be better)
        #This should be changed with a creation call in case networks would be created on the fly   
        for vnf in nf_fg.listVNF:
            nf = profile_graph.functions[vnf.id]
            for port in vnf.listPort:
                p = nf.ports[port.id]
                for flowrule in port.list_outgoing_label:
                    #TODO: errore se i grafi contengono primitive non valide (es: splitter)
                    if flowrule.action.type == "output" or flowrule.action.type == "endpoint":
                        if flowrule.matches is not None:
                            #TODO: flowspecs with vlan_id and ip_addresses (mgmt network)
                            net_vlan = flowrule.matches[0].id
                            net_id = self.getNetworkIdfromVlan(net_vlan)
                            p.setNetwork(net_id, net_vlan)
                    
                    if flowrule.action.type == "control":
                        if flowrule.matches is not None:
                            #TODO: attach the port to the right management network
                            pass
                                   
        return profile_graph
    
    def openstackResourcesInstantiation(self, profile_graph, nf_fg):
        #Instantiate ports and servers directly interacting with Neutron and Nova
        for vnf in profile_graph.functions.values():
            for port in vnf.listPort:
                if port.net is None:
                    #TODO: create an Openstack network and subnet and set the id into port.net instead of exception
                    raise StackError("No network found for this port")
                        
                resp = Neutron().createPort(self.neutronEndpoint, self.token.get_token(), port.getResourceJSON())
                if resp['port']['status'] == "DOWN":
                    port_id = resp['port']['id']
                    port.setId(port_id)
                    #TODO: mac address and other port info missing in the db
                    Graph().setPortInternalID(port.name, nf_fg.getVNFByID(vnf.id).db_id, port_id, self.session_id, nf_fg.db_id, port_type='openstack')
                    Graph().setOSNetwork(port.net, port.name, nf_fg.getVNFByID(vnf.id).db_id, port_id, self.session_id, nf_fg.db_id,  vlan_id = port.vlan)
                           
            resp = Nova().createServer(self.novaEndpoint, self.token.get_token(), vnf.getResourceJSON())
            vnf.OSid = resp['server']['id']
            #TODO: image location, location, type and availability_zone missing
            Graph().setVNFInternalID(vnf.id, vnf.OSid, self.session_id, nf_fg.db_id)
                    
        # Add flows on the SDN network to connect endpoints
        self.connectEndpoints(nf_fg)
    
    def openstackResourcesDeletion(self):       
        #Delete every resource one by one
        self.disconnectEndpoints()
        
        vnfs = Graph().getVNFs(self.session_id)
        for vnf in vnfs:
            Nova().deleteServer(self.novaEndpoint, self.token.get_token(), vnf.internal_id)
            
        #TODO: Delete also networks and subnets if previously created
    
    '''
    ######################################################################################################
    ##########################    Find right flavor for virtual machine        ###########################
    ######################################################################################################
    '''    
                        
    def findFlavor(self, memorySize, rootFileSystemSize, ephemeralFileSystemSize, CPUrequirements, token):
        '''
        Find the best nova flavor from the given requirements of the machine
        params:
            memorySize:
                Minimum RAM memory required
            rootFileSystemSize:
                Minimum size of the root file system required
            ephemeralFileSystemSize:
                Minimum size of the ephemeral file system required (not used yet)
            CPUrequirements:
                Minimum number of vCore required
            token:
                Keystone token for the authentication
        '''
        flavors = Nova().get_flavors(self.novaEndpoint, token, memorySize, rootFileSystemSize+ephemeralFileSystemSize)['flavors']
        findFlavor = None
        minData = 0
        for flavor in flavors:
            if flavor['vcpus'] >= CPUrequirements:
                if findFlavor == None:
                    findFlavor = flavor
                    minData = flavor['vcpus'] - CPUrequirements + (flavor['ram'] - memorySize)/1024 + flavor['disk'] - rootFileSystemSize - int(ephemeralFileSystemSize or 0)
                elif (flavor['vcpus'] - CPUrequirements + (flavor['ram'] - memorySize)/1024 + flavor['disk'] - rootFileSystemSize - int(ephemeralFileSystemSize or 0)) < minData:
                    findFlavor = flavor
                    minData = flavor['vcpus'] - CPUrequirements + (flavor['ram'] - memorySize)/1024 + flavor['disk'] - rootFileSystemSize - int(ephemeralFileSystemSize or 0)
        return findFlavor
    
    '''
    ######################################################################################################
    #########################    Manage internal connection in the nodes        ##########################
    ######################################################################################################
    '''
    
    def getNetworkIdfromVlan(self, vlan_id):
        '''
        Get the Neutron network id from the database
        Args:
            vlan_id:
                id of the vlan
        '''
        networks = Graph().getAllNetworks()
        for net in networks:
            if net.vlan_id == vlan_id:
                return net.id
        return None       
     
    '''
    ######################################################################################################
    #########################    Manage external connection among nodes        ###########################
    ######################################################################################################
    ''' 
    '''
    WARNING: all this Opendaylight API calls are based on Helium MD-SAL; not working with AD-SAL
    '''
    def getNodes(self):
        '''
        Retrieve a list of Jolnet nodes (could be hosts or switches)
        '''
        json_data = ODL().getTopology(self)
        topology = json.loads(json_data)
        nList = topology["network-topology"]["topology"][0]["node"]
        return nList
    '''
    def getUserAttachmentPoints(self, user_mac):
        nodeList = self.getNodes()
        for node in nodeList:
            node_id = node["node-id"]
            tmpList = node_id.split(":")
            if (tmpList[0] == "host"):
                if (tmpList[1] == user_mac):
                    return node["host-tracker-service:attachment-points"]'''
    
    def getLinkBetweenSwitches(self, switch1, switch2):             
        '''
        Retrieve the link between two switches, where you can find ports to use
        Args:
            switch1:
                OpenDaylight identifier of the source switch (example: openflow:123456789)
            switch2:
                OpenDaylight identifier of the destination switch (example: openflow:987654321)
        '''
        json_data = ODL().getTopology()
        topology = json.loads(json_data)
        tList = topology["network-topology"]["topology"][0]["link"]
        for link in tList:
            source_node = link["source"]["source-node"]
            dest_node = link["destination"]["dest-node"]
            if (source_node == switch1 and dest_node == switch2):
                return link
    
    def pushVlanFlow(self, source_node, flow_id, vlan, in_port, out_port, user):
        '''
        Push a flow into a Jolnet switch with 
            matching on VLAN id and input port
            output through the specified port
        Args:
            source_node:
                OpenDaylight identifier of the source switch (example: openflow:123456789)
            flow_id:
                unique identifier of the flow on the whole OpenDaylight domain
            vlan:
                VLAN id of the traffic (for matching)
            in_port:
                ingoing port of the traffic (for matching)
            out_port:
                output port where to send out the traffic (action)
            user:
                user profile id to keep track of the owner of the flow
        '''
        action1 = Action()
        action1.setOutputAction(out_port, 65535)
        actions = [action1]
        
        match = Match()
        match.setInputMatch(in_port)
        match.setVlanMatch(vlan)
        
        flowj = Flow("jolnetflow", flow_id, 0, 20, True, 0, 0, actions, match)        
        json_req = flowj.getJSON()
        ODL().createFlow(json_req, source_node, flow_id)
    
    def pushMACSourceFlow(self, source_node, flow_id, user_vlan, in_port, source_mac, out_port, graph_vlan):
        '''
        Push a flow into a Jolnet switch (or cpe) with 
            matching on source MAC address and VLAN id
            VLAN tag swapping and output through the specified port
        Args:
            source_node:
                OpenDaylight identifier of the source switch (example: openflow:123456789)
            flow_id:
                unique identifier of the flow on the whole OpenDaylight domain
            user_vlan:
                VLAN id of the traffic (for matching)
            in_port:
                ingoing port of the traffic (for matching)
            source_mac:
                MAC address of the user device
            out_port:
                output port where to send out the traffic (action)
            graph_vlan:
                new VLAN id to be applied to packets (action)
        '''
        action1 = Action()
        action1.setSwapVlanAction(graph_vlan)
        action2 = Action()
        action2.setOutputAction(out_port, 65535)
        actions = [action1, action2]
        
        priority = 10
        match = Match()
        match.setInputMatch(in_port)
        if source_mac is not None:
            match.setEthernetMatch(None, source_mac, None)
            priority = priority + 15
        match.setVlanMatch(user_vlan)
        
        flowj = Flow("edgeflow", flow_id, 0, priority, True, 0, 0, actions, match)        
        json_req = flowj.getJSON()
        ODL().createFlow(json_req, source_node, flow_id)
    
    def pushMACDestFlow(self, source_node, flow_id, user_vlan, in_port, dest_mac, out_port, graph_vlan):
        '''
        Push a flow into a Jolnet switch (or cpe) with 
            matching on destination MAC address and VLAN id
            VLAN tag swapping and output through the specified port
        Args:
            source_node:
                OpenDaylight identifier of the source switch (example: openflow:123456789)
            flow_id:
                unique identifier of the flow on the whole OpenDaylight domain
            user_vlan:
                new VLAN id for the traffic (action)
            in_port:
                ingoing port of the traffic (action)
            source_mac:
                MAC address of the user device
            out_port:
                output port where to send out the traffic (matching)
            graph_vlan:
                VLAN id of incoming packets (matching)
        '''
        action1 = Action()
        action1.setSwapVlanAction(user_vlan)
        action2 = Action()
        action2.setOutputAction(out_port, 65535)
        actions = [action1, action2]
        
        priority = 10
        match = Match()
        match.setInputMatch(in_port)
        if dest_mac is not None:
            match.setEthernetMatch(None, None, dest_mac)
            priority = priority + 15
        match.setVlanMatch(graph_vlan)
        
        flowj = Flow("edgeflow", flow_id, 0, priority, True, 0, 0, actions, match)        
        json_req = flowj.getJSON()
        ODL().createFlow(json_req, source_node, flow_id)
    
    def linkZones(self, graph_id, switch_user, port_vms_user, switch_user_id, switch_isp, port_vms_isp, switch_isp_id, vlan_id):
        '''
        Link two graphs (or two parts of a single graph) through the SDN network
        Args:
            graph_id:
                id of the user's graph
            switch_user:
                OpenDaylight identifier of the first switch (example: openflow:123456789)
            port_vms_user:
                port on the OpenFlow switch where virtual machines are linked
            switch_user_id:
                id of the node in the database
            switch_isp:
                OpenDaylight identifier of the second switch (example: openflow:987654321)
            port_vms_isp:
                port on the OpenFlow switch where virtual machines are linked
            switch_isp_id:
                id of the node in the database
            vlan_id:
                VLAN id of the OpenStack network which links the graphs
        '''
        link = self.getLinkBetweenSwitches(switch_user, switch_isp)
        
        if link is not None:        
            tmp = link["source"]["source-tp"]
            tmpList = tmp.split(":")
            port12 = tmpList[2]
                    
            tmp = link["destination"]["dest-tp"]
            tmpList = tmp.split(":")
            port21 = tmpList[2]
                 
            fid = int(str(vlan_id) + str(1))              
            self.pushVlanFlow(switch_user, fid, vlan_id, port_vms_user, port12, vlan_id)
            Graph().AddFlowrule(self.session_id, graph_id, fid, "external", "node", switch_user_id, "node", switch_isp_id, "complete")
            fid = int(str(vlan_id) + str(2))
            self.pushVlanFlow(switch_isp, fid, vlan_id, port21, port_vms_isp, vlan_id)
            Graph().AddFlowrule(self.session_id, graph_id, fid, "external", "node", switch_isp_id, "node", switch_user_id, "complete")
            fid = int(str(vlan_id) + str(3))               
            self.pushVlanFlow(switch_isp, fid, vlan_id, port_vms_isp, port21, vlan_id)
            Graph().AddFlowrule(self.session_id, graph_id, fid, "external", "node", switch_isp_id, "node", switch_user_id, "complete")
            fid = int(str(vlan_id) + str(4))               
            self.pushVlanFlow(switch_user, fid, vlan_id, port12, port_vms_user, vlan_id)
            Graph().AddFlowrule(self.session_id, graph_id, fid, "external", "node", switch_user_id, "node", switch_isp_id, "complete")
        else:
            logging.debug("Cannot find a link between " + switch_user + " and " + switch_isp)
    
    def linkUser(self, graph_id, cpe, user_port, cpe_id, switch, switch_port, switch_id, graph_vlan, user_vlan, user_mac = None):
        '''
        Link a user with his graph through the SDN network
        Args:
            graph_id:
                id of the user's graph
            cpe:
                OpenDaylight identifier of the cpe where user is connecting (example: openflow:123456789)
            user_port:
                port on the OpenFlow switch (cpe) where the user is connecting
            cpe_id:
                id of the node in the database
            switch:
                OpenDaylight identifier of the graph switch (example: openflow:987654321)
            switch_port:
                port on the OpenFlow switch where the user's graph is istantiated (compute node)
            switch_id:
                id of the node in the database
            graph_vlan:
                VLAN id of the graph ingress endpoint
            user_vlan:
                VLAN id of user's outgoing traffic (if any)
            user_mac:
                MAC address of the user's device
        '''
        link = self.getLinkBetweenSwitches(cpe, switch)
        
        if link is not None:            
            tmp = link["source"]["source-tp"]
            tmpList = tmp.split(":")
            port12 = tmpList[2]
                        
            tmp = link["destination"]["dest-tp"]
            tmpList = tmp.split(":")
            port21 = tmpList[2]
            
            fid = int(str(graph_vlan) + str(1))
            self.pushMACSourceFlow(cpe, fid, user_vlan , user_port, user_mac, port12, graph_vlan)
            Graph().AddFlowrule(self.session_id, graph_id, fid, "external", "node", cpe_id, "node", switch_id, "complete")
            fid = int(str(graph_vlan) + str(2))
            self.pushVlanFlow(switch, fid, graph_vlan, port21, switch_port, user_mac)
            Graph().AddFlowrule(self.session_id, graph_id, fid, "external", "node", switch_id, "node", cpe_id, "complete")
            fid = int(str(graph_vlan) + str(3))
            self.pushVlanFlow(switch, fid, graph_vlan, switch_port, port21, user_mac)
            Graph().AddFlowrule(self.session_id, graph_id, fid, "external", "node", switch_id, "node", cpe_id, "complete")
            fid = int(str(graph_vlan) + str(4))
            self.pushMACDestFlow(cpe, fid, user_vlan , port12, user_mac, user_port, graph_vlan)
            Graph().AddFlowrule(self.session_id, graph_id, fid, "external", "node", cpe_id, "node", switch_id, "complete")
        else:
            logging.debug("Cannot find a link between " + cpe + " and " + switch)
    
    '''
    ######################################################################################################
    ###############################       Manage graphs connection        ################################
    ######################################################################################################
    ''' 
    
    def connectEndpoints(self, nf_fg):
        '''
        Read nf_fg endpoints and create corrisponding flows on the SDN network
        Expecting some precise endpoint descriptions which reflect Orchestration layer scheduling choices
        '''
        #Get egress endpoints of the graph        
        endpoints = nf_fg.getVlanEgressEndpoints()
        for endpoint in endpoints:
            if endpoint.connection is True:
                #Check if the remote graph exists and the requested endpoint is available                
                session = Session().get_active_user_session_by_nf_fg_id(endpoint.remote_graph).id
                existing_endpoints = Graph().getEndpoints(session)
                existing = None
                for e in existing_endpoints:
                    if (e.graph_endpoint_id == endpoint.remote_id):
                        existing = e
                
                if existing is not None:
                    vlan = endpoint.id
                    switch1 = endpoint.node
                    port1 = endpoint.interface                                       
                                       
                    node1_id = Node().getNodeFromDomainID(switch1).id
                    node2_id = Graph().getNodeID(session)
                    switch2 = Node().getNodeDomainID(node2_id)     
                    port2 = existing.location         
                    
                    self.linkZones(nf_fg.db_id, switch1, port1, node1_id, switch2, port2, node2_id, vlan)
                else:
                    logging.error("Remote graph " + endpoint.remote_graph + " has not a " + endpoint.id + " endpoint available!")
            
            #Insert location info into the database
            Graph().setEndpointLocation(self.session_id, nf_fg.db_id, endpoint.id, endpoint.interface)
            
        #Get ingress endpoints of the graph (auth graph has the same endpoint but without user_mac)
        endpoints = nf_fg.getVlanIngressEndpoints()
        for endpoint in endpoints:
            if endpoint.attached is True:
                session = Session().get_active_user_session_by_nf_fg_id(endpoint.remote_graph).id
                existing_endpoints = Graph().getEndpoints(session)
                existing = None
                for e in existing_endpoints:
                    if (e.graph_endpoint_id == endpoint.remote_id):
                        existing = e
                    
                user_vlan = endpoint.id
                user_mac = endpoint.user_mac
                graph_vlan = endpoint.remote_id               
                cpe = endpoint.node
                cpe_port = endpoint.interface
                                
                cpe_id = Node().getNodeFromDomainID(cpe).id
                node_id = Graph().getNodeID(session)
                switch = Node().getNodeDomainID(node_id)
                switch_port = existing.location 
                    
                self.linkUser(nf_fg.db_id, cpe, cpe_port, cpe_id, switch, switch_port, node_id, graph_vlan, user_vlan, user_mac)
            
            #Insert location info into the database
            Graph().setEndpointLocation(self.session_id, nf_fg.db_id, endpoint.id, endpoint.interface)
        
    def disconnectEndpoints(self):
        '''
        Deletes flows on the SDN network after a profile deletion
        Args:
            nf_fg:
                JSON Object for the user profile graph (forwarding graph)
        '''
        flows = Graph().getOArchs(self.session_id)
        for flow in flows:
            if flow.type == "external" and flow.status == "complete":
                switch_id = Node().getNodeDomainID(flow.start_node_id)
                ODL().deleteFlow(switch_id, flow.internal_id)
    