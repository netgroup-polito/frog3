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
from Orchestrator.ComponentAdapter.Common.nffg_management import NFFG_Management
from Orchestrator.ComponentAdapter.Jolnet.rest import ODL, Glance, Nova, Neutron
from Orchestrator.ComponentAdapter.Jolnet.resources import Action, Match, Flow, ProfileGraph, VNF, Endpoint

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
        self.node_endpoint = node_endpoint
        return self.openstackResourcesStatus(self.token.get_token())
    
    def instantiateProfile(self, nf_fg, node_endpoint):
        '''
        Override method of the abstract class for instantiating the user graph
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
    
    def updateProfile(self, new_nf_fg, old_nf_fg, node_endpoint):
        '''
        Override method of the abstract class for updating the user graph
        '''        
        self.node_endpoint = node_endpoint
        
        try:
            updated_nffg = NFFG_Management().diff(old_nf_fg, new_nf_fg)
            
            if DEBUG_MODE is True:
                logging.debug("diff: " + updated_nffg.getJSON()) 
                
            self.openstackResourcesControlledDeletion(updated_nffg, self.token.get_token())
            Graph().updateNFFG(updated_nffg, self.session_id)
            profile_graph = self.buildProfileGraph(updated_nffg)
            self.openstackResourcesInstantiation(profile_graph, updated_nffg)
            logging.debug("Graph " + old_nf_fg.id + "correctly updated!")
            
        except Exception as err:
            logging.error(err.message)
            logging.exception(err) 
            raise
        
    def deinstantiateProfile(self, nf_fg, node_endpoint):
        '''
        Override method of the abstract class for deleting the user graph
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
 
    '''
    ######################################################################################################
    #############################    Resources preparation phase        ##################################
    ######################################################################################################
    '''      
    def buildProfileGraph(self, nf_fg):
        profile_graph = ProfileGraph()
        profile_graph.setId(nf_fg.id)
        
        #TODO: merge this two cycles together
        for vnf in nf_fg.listVNF[:]:
            nf = self.buildVNF(vnf)
            profile_graph.addVNF(nf)
        
        for vnf in nf_fg.listVNF[:]:
            nf = profile_graph.functions[vnf.id]
            self.setVNFNetwork(vnf, nf)
        
        for endpoint in nf_fg.listEndpoint:
            if endpoint.type == "vlan-egress" or endpoint.type == "vlan-ingress":
                ep = self.buildEndpoint(endpoint)
                profile_graph.addEndpoint(ep)
                
        for vnf in nf_fg.listVNF[:]:
            nf = profile_graph.functions[vnf.id]
            self.characterizeIngressEndpoints(profile_graph, nf_fg, vnf)
                             
        return profile_graph                        
    
    def buildVNF(self, vnf):
        #Get the necessary info (glance URI and Nova flavor) and create a VNF object
        manifest = Manifest(vnf.manifest)
        cpuRequirements = manifest.CPUrequirements.socket
        if DEBUG_MODE is True:
            logging.debug(manifest.uri)
        image = Glance().getImage(manifest.uri, self.token.get_token())
        flavor = self.findFlavor(int(manifest.memorySize), int(manifest.rootFileSystemSize),
            int(manifest.ephemeralFileSystemSize), int(cpuRequirements[0]['coreNumbers']), self.token.get_token())
        if vnf.status is None:
            status = "new"
        else:
            status = vnf.status
        return VNF(vnf.id, vnf, image, flavor, vnf.availability_zone, status)
    
    def setVNFNetwork(self, vnf, nf):
        #Complete all ports with the right Neutron network id and add them to the VNF
        #This is necessary because the network are already present (create them on the fly would be better)
        #This should be changed with a creation call in case networks would be created on the fly
        for port in vnf.listPort[:]:
            p = nf.ports[port.id]
            
            if len(port.list_outgoing_label) > 1:
                raise StackError("Traffic splitting and merging not supported!")
            
            for flowrule in port.list_outgoing_label:
                if flowrule.action.type == "output":
                    if flowrule.matches is not None:
                        #Check if the network required already exists in Neutron
                        net_vlan = flowrule.match.of_field['vlanId']
                        name = "exp" + str(net_vlan)
                        net_id = self.getNetworkIdfromName(name)
                        p.setNetwork(net_id, net_vlan)                        
                        networks = Graph().getAllNetworks()
                        found = False
                        for net in networks:
                            if net.vlan_id == net_vlan:
                                found = True
                        if found is False:
                            Graph().addOSNetwork(net_id, name, 'complete', net_vlan)
                    
                if flowrule.action.type == "control":
                    if flowrule.matches is not None:
                        #TODO: attach the port to the right management network
                        pass                                          
            
    def buildEndpoint(self, endpoint):
        if endpoint.status is None:
            status = "new"
        else:
            status = endpoint.status
        if endpoint.connection is True:
            return Endpoint(endpoint.id, endpoint.name, endpoint.connection, endpoint.type, endpoint.node, endpoint.interface, status, endpoint.remote_graph, endpoint.remote_id)
        else:
            return Endpoint(endpoint.id, endpoint.name, endpoint.connection, endpoint.type, endpoint.node, endpoint.interface, status)
    
    def characterizeIngressEndpoints(self, profile_graph, nf_fg, vnf):
        for port in vnf.listPort[:]:
            for flowrule in port.list_ingoing_label:
                if flowrule.status == 'new':
                    if flowrule.action.type == "output":
                        if flowrule.matches is not None:
                            endpoint = profile_graph.getIngressEndpoint(flowrule.flowspec['ingress_endpoint'])
                            
                            user_vlan = flowrule.match.of_field['vlanId']
                            user_mac = flowrule.match.of_field['sourceMAC']
                            user_port = flowrule.match.of_field['sourcePort']
                            tmp = user_port.split(":")                                     
                            cpe = tmp[0] + ":" + tmp[1]
                            cpe_port = tmp[2]
                            
                            endpoint.setUserParams(user_mac, user_vlan, cpe, cpe_port)
    
    '''
    ######################################################################################################
    ##########################    Resources instantiation and deletion        ############################
    ######################################################################################################
    ''' 
    def openstackResourcesInstantiation(self, profile_graph, nf_fg):
        #Instantiate ports and servers directly interacting with Neutron and Nova
        for vnf in profile_graph.functions.values():
            if vnf.status == "new":           
                self.createServer(vnf, nf_fg)
            else:
                for port in vnf.listPort[:]:
                    if port.status == "new":
                        self.addPorttoVNF(port, vnf, nf_fg)
                    
        #Create flow on the SDN network for graphs interconnection
        for endpoint in profile_graph.getVlanEgressEndpoints():
            if endpoint.status == "new":
                if endpoint.connection is True:
                    #Check if the remote graph exists and the requested endpoint is available                
                    session = Session().get_active_user_session_by_nf_fg_id(endpoint.remote_graph).id
                    existing_endpoints = Graph().getEndpoints(session)
                    remote_endpoint = None
                    for e in existing_endpoints:
                        if (e.graph_endpoint_id == endpoint.remote_id):
                            remote_endpoint = e
                    
                    if remote_endpoint is not None:
                        vlan = endpoint.id
                        switch1 = endpoint.node
                        port1 = endpoint.interface                                       
                                           
                        node1_id = Node().getNodeFromDomainID(switch1).id
                        node2_id = Graph().getNodeID(session)
                        switch2 = Node().getNodeDomainID(node2_id)     
                        port2 = remote_endpoint.location         
                        
                        #TODO: add the port on the endpoint switch
                        self.linkZones(nf_fg.db_id, switch1, port1, node1_id, switch2, port2, node2_id, vlan)
                    else:
                        logging.error("Remote graph " + endpoint.remote_graph + " has not a " + endpoint.id + " endpoint available!")
                
                #Insert location info into the database
                Graph().setEndpointLocation(self.session_id, nf_fg.db_id, endpoint.id, endpoint.interface)
            
        #Create flow on the SDN network for users connection (auth graph has the same endpoint but without user_mac)
        for endpoint in profile_graph.getVlanIngressEndpoints():
            if endpoint.status == "new":
                if endpoint.connection is True:
                    cpe_id = Node().getNodeFromDomainID(endpoint.user_node).id
                    switch_id = Node().getNodeFromDomainID(endpoint.node).id
                    self.linkUser(nf_fg.db_id, endpoint.user_node, endpoint.user_interface, cpe_id, endpoint.node, endpoint.interface, switch_id, endpoint.id, endpoint.user_vlan, endpoint.user_mac)
                
                #Insert location info into the database
                Graph().setEndpointLocation(self.session_id, nf_fg.db_id, endpoint.id, endpoint.interface)                      
    
    def openstackResourcesDeletion(self):       
        #Delete every resource one by one
        flows = Graph().getOArchs(self.session_id)
        for flow in flows:
            if flow.type == "external" and flow.status == "complete":
                switch_id = Node().getNodeDomainID(flow.start_node_id)
                ODL().deleteFlow(switch_id, flow.internal_id)
        
        vnfs = Graph().getVNFs(self.session_id)
        for vnf in vnfs:
            Nova().deleteServer(self.novaEndpoint, self.token.get_token(), vnf.internal_id)
            
        #TODO: Delete also networks and subnets if previously created
    
    def openstackResourcesControlledDeletion(self, updated_nffg, token_id):
        # Delete VNFs
        for vnf in updated_nffg.listVNF[:]:
            if vnf.status == 'to_be_deleted':
                self.deleteServer(vnf, updated_nffg)              
            else:
                # Delete ports
                for port in vnf.listPort[:]:
                    self.deletePort(port)
        
        for endpoint in updated_nffg.listEndpoint[:]:
            if endpoint.status == 'to_be_deleted':
                flows = Graph().getOArchs(self.session_id)
                for flow in flows:
                    if flow.type == "external" and flow.status == "complete" and flow.internal_id.contains(endpoint.id):
                        switch_id = Node().getNodeDomainID(flow.start_node_id)
                        ODL().deleteFlow(switch_id, flow.internal_id)
        
        # Wait for resource deletion
        '''for vnf in updated_nffg.listVNF[:]:
            if vnf.status == 'to_be_deleted':
                while True:
                    status = Nova().getServerStatus(self.novaEndpoint, token_id, vnf.internal_id)
                    if status != 'ACTIVE':
                        logging.debug("VNF "+vnf.internal_id+" status "+status)
                        updated_nffg.listVNF.remove(vnf)
                        break
                    if status == 'ERROR':
                        raise Exception('VNF status ERROR - '+vnf.internal_id)
                    logging.debug("VNF "+vnf.internal_id+" status "+status)
            else:
                for port in vnf.listPort[:]:
                    if port.status == 'to_be_deleted':
                        while True:
                            status = Neutron().getPortStatus(self.neutronEndpoint, token_id, port.internal_id)
                            if status != 'ACTIVE':
                                logging.debug("VNF "+vnf.internal_id+" status "+status)
                                vnf.listPort.remove(port)
                                break
                            if status == 'ERROR':
                                raise Exception('Port status ERROR - '+vnf.internal_id)
                            logging.debug("Port "+vnf.internal_id+" status "+status)'''
    
    def openstackResourcesStatus(self, token_id):
        resources_status = {}
        resources_status['ports'] = {}
        ports = Graph().getPorts(self.session_id)
        for port in ports:
            if port.type == 'openstack':
                resources_status['ports'][port.id] = Neutron().getPortStatus(self.neutronEndpoint, token_id, port.internal_id)
        resources_status['vnfs'] = {}
        vnfs = Graph().getVNFs(self.session_id)
        for vnf in vnfs:
            resources_status['vnfs'][vnf.id] = Nova().getServerStatus(self.novaEndpoint, token_id, vnf.internal_id)
        
        num_resources = len(resources_status['ports']) + len(resources_status['vnfs'])                
        num_resources_completed = 0
        
        for value in resources_status['ports'].itervalues():
            logging.debug("port - "+value)
            if value == 'ACTIVE':
                num_resources_completed = num_resources_completed + 1
        for value in resources_status['vnfs'].itervalues():
            logging.debug("vnf - "+value)
            if value == 'ACTIVE':
                num_resources_completed = num_resources_completed + 1
        
        status  = {}
        if DEBUG_MODE is True:
            logging.debug("num_resources_completed "+str(num_resources_completed))
            logging.debug("num_resources "+str(num_resources))
            
        if num_resources_completed == num_resources:
            status['status'] = 'complete'
            status['percentage_completed'] = num_resources_completed/num_resources*100
        else:
            status['status'] = 'in_progress'
            status['percentage_completed'] = num_resources_completed/num_resources*100
        
        return status
    
    '''
    ######################################################################################################
    ###############################    Interactions with OpenStack       #################################
    ######################################################################################################
    '''
    def createServer(self, vnf, nf_fg):
        for port in vnf.listPort[:]:
            self.createPort(port, vnf, nf_fg) 
        json_data = vnf.getResourceJSON()
        resp = Nova().createServer(self.novaEndpoint, self.token.get_token(), json_data)
        vnf.OSid = resp['server']['id']
        
        #TODO: image location, location, type and availability_zone missing
        Graph().setVNFInternalID(vnf.id, vnf.OSid, self.session_id, nf_fg.db_id)
    
    def deleteServer(self, vnf, nf_fg):
        Nova().deleteServer(self.novaEndpoint, self.token.get_token(), vnf.internal_id)
        Graph().deleteFlowspecFromVNF(self.session_id, vnf.db_id)
        Graph().deleteVNFNetworks(self.session_id, vnf.db_id)     
        Graph().deletePort(None, self.session_id, vnf.db_id)
        Graph().deleteVNF(vnf.id, self.session_id)
        nf_fg.listVNF.remove(vnf)    
    
    def createPort(self, port, vnf, nf_fg):
        if port.net is None:
            #TODO: create an Openstack network and subnet and set the id into port.net instead of exception
            #You need to set its vlan-id as the one passed in the flowrule (you cannot do it from OpenStack)
            raise StackError("No network found for this port")
        
        json_data = port.getResourceJSON()      
        resp = Neutron().createPort(self.neutronEndpoint, self.token.get_token(), json_data)
        if resp['port']['status'] == "DOWN":
            port_id = resp['port']['id']
            port.setId(port_id)
            Graph().setPortInternalID(port.name, nf_fg.getVNFByID(vnf.id).db_id, port_id, self.session_id, nf_fg.db_id, port_type='openstack')
            Graph().setOSNetwork(port.net, port.name, nf_fg.getVNFByID(vnf.id).db_id, port_id, self.session_id, nf_fg.db_id,  vlan_id = port.vlan)
    
    def deletePort(self, port): 
        if port.status == 'to_be_deleted':
            Neutron().deletePort(self.neutronEndpoint, self.token.get_token(), port.internal_id)
            Graph().deleteFlowspecFromPort(self.session_id, port.id)
            p = Graph().getPortFromInternalID(port.internal_id)
            Graph().deleteNetwok(p.os_network_id)
            Graph().deletePort(port.id, self.session_id)
        else:
            # Delete flow-rules
            for flowrule in port.list_outgoing_label[:]:
                if flowrule.status == 'to_be_deleted':
                    Neutron().deletePort(self.neutronEndpoint, self.token.get_token(), port.internal_id)                                
                    Graph().deleteoOArch(flowrule.db_id, self.session_id)
                    Graph().deleteFlowspec(flowrule.db_id, self.session_id)
                    p = Graph().getPortFromInternalID(port.internal_id)
                    Graph().deleteNetwok(p.os_network_id)
                    Graph().deletePort(port.id, self.session_id)                   
                    port.list_outgoing_label.remove(flowrule)
                    port.status = 'new'
            for flowrule in port.list_ingoing_label[:]:
                if flowrule.status == 'to_be_deleted':
                    flows = Graph().getOArchs(self.session_id)
                    for flow in flows:
                        if flow.type == "external" and flow.status == "complete" and flow.internal_id.contains(flowrule.action.endpoint.id):
                            switch_id = Node().getNodeDomainID(flow.start_node_id)
                            ODL().deleteFlow(switch_id, flow.internal_id)
                            Graph().deleteoOArch(flowrule.db_id, self.session_id)
                            Graph().deleteFlowspec(flowrule.db_id, self.session_id)
                            port.list_ingoing_label.remove(flowrule)
            
    def addPorttoVNF(self, port, vnf, nf_fg):
        vms = Graph().getVNFs(self.session_id)
        for vm in vms:
            if vm.graph_vnf_id == vnf.id:
                port.setDeviceId(vm.internal_id)
                self.createPort(port, vnf, nf_fg)
                break;
        
    def getNetworkIdfromName(self, network_name):
        #Since we need to control explicitly the vlan id of OpenStack networks, we need to use this trick
        #No way to find vlan id from OpenStack REST APIs
        json_data = Neutron().getNetworks(self.neutronEndpoint, self.token.get_token())
        networks = json.loads(json_data)['networks']
        for net in networks:
            if net['name'] == network_name:
                return net['id']
        return None
    
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
    #########################    Interactions with OpenDaylight Helium       #############################
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
    