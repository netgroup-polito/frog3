'''
Created on 13/apr/2015
@author: vida
'''

import logging
import json

from Common.config import Configuration
from Common.NF_FG.nf_fg import NF_FG
from Common.Manifest.manifest import Manifest
from Common.exception import StackError
from Common.SQL.graph.Graph import getNetworks

from Orchestrator.ComponentAdapter.interfaces import OrchestratorInterface
from Orchestrator.ComponentAdapter.Jolnet.rest import ODL, Glance, Nova, Neutron, Heat
from Orchestrator.ComponentAdapter.Jolnet.resources import Action, Match, Flow, ProfileGraph, VNF


DEBUG_MODE = Configuration().DEBUG_MODE
USE_HEAT = Configuration().USE_HEAT

class JolnetAdapter(OrchestratorInterface):
    '''
    Override class of the abstract class OrchestratorInterface
    '''
    
    STATUS = ['CREATE_IN_PROGRESS', 'CREATE_COMPLETE', 'CREATE_FAILED',  'DELETE_IN_PROGRESS', 'DELETE_COMPLETE', 'DELETE_FAILED', 'UPDATE_IN_PROGRESS', 'UPDATE_COMPLETE', 'UPDATE_FAILED']
    WRONG_STATUS = ['CREATE_FAILED','DELETE_FAILED', 'UPDATE_FAILED']
    
    def __init__(self, compute_node_address, session_id, token):
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
        
        if USE_HEAT is True:
            self.heatEndpoint = token.get_endpoints('orchestration')[0]['publicURL']
        
        logging.debug(self._URI)    
        if DEBUG_MODE is True:
            if USE_HEAT is True:            
                logging.debug(self.heatEndpoint)
            else:
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
        if USE_HEAT is True:
            pass
        else:
            pass
    
    def instantiateProfile(self, nf_fg, node_endpoint):
        '''
        Override method of the abstract class for instantiating the user Stack
        '''
        self.node_endpoint = node_endpoint
        
        nf_fg = NF_FG(nf_fg)
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
            #set_error(self.token.get_userID())  
            raise
    
    def updateProfile(self, new_nf_fg, old_nf_fg, token, node_endpoint):
        pass
        
    def deinstantiateProfile(self, nffg, node_endpoint):
        '''
        Override method of the abstract class for deleting the user Stack
        '''
        self.node_endpoint = node_endpoint 
        
        try:
            nf_fg = NF_FG(json.loads(nffg))  
            
            if DEBUG_MODE is True:
                logging.debug(nffg)
                       
            self.openstackResourcesDeletion(nf_fg)
            logging.debug("Graph " + nffg.id + "correctly deleted!")
            
        except Exception as err:
            logging.error(err.message)
            logging.exception(err)
            #set_error(self.token.get_userID())  
            raise
    
    def buildProfileGraph(self, nf_fg, token):
        profile_graph = ProfileGraph()
        profile_graph.setId(nf_fg.id)
                
        #Get the necessary info (glance URI and Nova flavor) and create a VNF object
        for vnf in nf_fg.listVNF:
            manifest = Manifest(vnf.manifest)
            cpuRequirements = manifest.CPUrequirements.socket
            if DEBUG_MODE is True:
                logging.debug(manifest.uri)
            image = Glance().getImage(manifest.uri, token)
            flavor = self.findFlavor(int(manifest.memorySize), int(manifest.rootFileSystemSize),
                    int(manifest.ephemeralFileSystemSize), int(cpuRequirements[0]['coreNumbers']), token)
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
                            #TODO: cambiare come vengono lette queste info e la flowspec
                            net_vlan = flowrule.matches[0].id
                            net_id = self.getNetworkIdfromVlan(net_vlan)
                            p.setNetwork(net_id)
                            
                            #if flowrule.action.type == "endpoint":
                            #    #Record the available endpoints into database
                            #    set_endpoint(nf_fg.id, flowrule.action.endpoint['id'], True, vnf.id, port.id, "vlan")
                    
                    if flowrule.action.type == "control":
                        #TODO: attach the port to the right management network
                        pass
                    
                for flowrule in port.list_ingoing_label:
                    pass
        
        #Insert unattached endpoints into DB (apart for ISP ones)
        #TODO: spostare questo negli endpoint
        for endpoint in nf_fg.listEndpoint:
            if endpoint.connection is False and endpoint.attached is False and endpoint.edge is False:
                #existing_endpoints = get_available_endpoints_by_id(nf_fg.id, endpoint.id)
                #if existing_endpoints is None:
                #    set_endpoint(nf_fg.id, endpoint.id, True, endpoint.name, endpoint.interface, endpoint.type)
                pass
        return profile_graph
    
    def openstackResourcesInstantiation(self, profile_graph, nf_fg):
        if USE_HEAT is True:
            #Instantiate the Heat stack through Heat templates (HOT)
            stackTemplate = profile_graph.getStackTemplate()
            if DEBUG_MODE is True:
                logging.debug(json.dumps(stackTemplate))
            res = Heat().instantiateStack(self.URI, self.token, nf_fg.name, stackTemplate)
            if DEBUG_MODE is True:
                logging.debug("Heat response: " + str(res))
                
        elif USE_HEAT is False:
            #Instantiate ports and servers directly interacting with Neutron and Nova
            for vnf in profile_graph.functions.values():
                for port in vnf.listPort:
                    if port.net is not None:
                        #TODO: creare la rete openstack se non esiste
                        
                        resp = Neutron().createPort(self.neutronEndpoint, self.token, port.getResourceJSON())
                        if resp['port']['status'] == "DOWN":
                            port_id = resp['port']['id']
                            port.setId(port_id)
                        
                resp = Nova().createServer(self.novaEndpoint, self.token, vnf.getResourceJSON())
                vnf.OSid = resp['server']['id']
                    
        # Add flows on the SDN network to connect endpoints
        self.connectEndpoints(nf_fg)
    
    def openstackResourcesDeletion(self, nf_fg):
        #TODO:
        if USE_HEAT is True:
            # Send request to Heat to delete the stack
            stack_id = Heat().getStackID(self.heatEndpoint, self.token, nf_fg.name)
            Heat().deleteStack(self.heatEndpoint, self.token, nf_fg.name , stack_id)
                
        elif USE_HEAT is False:
            #Delete every resource one by one
            #profile_resources = get_profile_resources(profile_id)
            #for res in profile_resources:
            #    if res.resource_type == "OS::Nova::Server":
            #        Nova().deleteServer(self.novaEndpoint, token, res.id)
            #        remove_resource(res.id)
            pass
            #Delete also networks if previously created
            
        #Delete flows on SDN network
        self.disconnectEndpoints(nf_fg)
    
    '''
    ######################################################################################################
    ###########################    Interaction with Heat for stacks        ###############################
    ######################################################################################################
    '''
    def getStackStatus(self, name):
        '''
        Get the status of a Stack
        Args:
            name:
                stack name
        '''
        stack_id = Heat().getStackID(self.heatEndpoint, self.token, name)
        return Heat().getStackStatus(self.heatEndpoint, self.token, stack_id)
    
    def getStackResourcesStatus(self, name):
        '''
        Get the status of a Stack resources
        Args:
            name:
                stack name
        '''
        stack_id = Heat().getStackID(self.heatEndpoint, self.token, name)
        return Heat().getStackResourcesStatus(self.heatEndpoint, self.token, name, stack_id)
    
    def checkStackErrorStatus(self, graph_name):
        '''
        Check if a stack is in an error state
        Args:
            token:
                The authentication token to use for the REST call
            graph_name:
                stack name
        '''
        try:
            stack_info = self.getStackStatus(self.token.get_token(), graph_name)
        except Exception as ex:
            logging.debug("Stack status exception: " + str(ex))
            return True    
        if stack_info in self.WRONG_STATUS:
            return True
        return False
    
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
        #return "m1.small"
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
        networks = getNetworks(self.session_id)
        for net in networks:
            if net.vlan_id.equals(vlan_id):
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
    
    def pushVlanFlow(self, source_node, flow_id, vlan, in_port, out_port, flow_type, user):
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
            flow_type:
                distinguish between internal flows (graphs interconnection) and user flows (users connection)
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
        
        #if (flow_already_exists(flow_id, source_node) == False):
        #    ODL().createFlow(json_req, source_node, flow_id)
        #    add_flow(flow_id, source_node, flow_type, user)
        #else:
        #    flows = get_internal_link_flows(vlan)
        #    for flow in flows:
        #        count = flow.users_count + 1
        #        update_flow(flow.id, flow.switch_id, flow.flowtype, flow.user, count)
    
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
        
        #if (flow_already_exists(flow_id, source_node) == False):
        #    ODL().createFlow(json_req, source_node, flow_id)
        #    add_flow(flow_id, source_node, "edge", source_mac)
        #else:
        #    flows = get_edge_link_flows(source_mac)
        #    for flow in flows:
        #        count = flow.users_count + 1
        #        update_flow(flow.id, flow.switch_id, flow.flowtype, flow.user, count)
    
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
        
        #if (flow_already_exists(flow_id, source_node) == False):
        #    ODL().createFlow(json_req, source_node, flow_id)
        #    add_flow(flow_id, source_node, "edge", dest_mac)
        #else:
        #    flows = get_edge_link_flows(dest_mac)
        #    for flow in flows:
        #        count = flow.users_count + 1
        #        update_flow(flow.id, flow.switch_id, flow.flowtype, flow.user, count)
    
    def linkZones(self, switch_user, port_vms_user, switch_isp, port_vms_isp, vlan_id):
        '''
        Link two graphs (or two parts of a single graph) through the SDN network
        Args:
            switch_user:
                OpenDaylight identifier of the first switch (example: openflow:123456789)
            port_vms_user:
                port on the OpenFlow switch where virtual machines are linked
            switch_isp:
                OpenDaylight identifier of the second switch (example: openflow:987654321)
            port_vms_isp:
                port on the OpenFlow switch where virtual machines are linked
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
            self.pushVlanFlow(switch_user, fid, vlan_id, port_vms_user, port12, "internal", vlan_id)
            fid = int(str(vlan_id) + str(2))
            self.pushVlanFlow(switch_isp, fid, vlan_id, port21, port_vms_isp, "internal", vlan_id)
            fid = int(str(vlan_id) + str(3))               
            self.pushVlanFlow(switch_isp, fid, vlan_id, port_vms_isp, port21, "internal", vlan_id)
            fid = int(str(vlan_id) + str(4))               
            self.pushVlanFlow(switch_user, fid, vlan_id, port12, port_vms_user, "internal", vlan_id)
        else:
            logging.debug("Cannot find a link between " + switch_user + " and " + switch_isp)
        
    def unlinkZones(self, vlan_id):
        '''
        Unlink two graphs which where linked through the SDN network
        Args:
            vlan_id:
                VLAN id of the OpenStack network which links the graphs
        '''
        #flows = get_internal_link_flows(vlan_id)
        #for flow in flows:
        #    count = flow.users_count
        #    if (count == 1):
        #        ODL().deleteFlow(flow.switch_id, flow.id)
        #        remove_flow(flow.id, flow.switch_id)
        #    else:
        #        count = count - 1
        #        update_flow(flow.id, flow.switch_id, flow.flowtype, flow.user, count)
        pass
    
    def linkUser(self, cpe, user_port, switch, switch_port, graph_vlan, user_vlan, user_mac = None):
        '''
        Link a user with his graph through the SDN network
        Args:
            cpe:
                OpenDaylight identifier of the cpe where user is connecting (example: openflow:123456789)
            user_port:
                port on the OpenFlow switch (cpe) where the user is connecting
            switch:
                OpenDaylight identifier of the graph switch (example: openflow:987654321)
            switch_port:
                port on the OpenFlow switch where the user's graph is istantiated (compute node)
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
            fid = int(str(graph_vlan) + str(2))
            self.pushVlanFlow(switch, fid, graph_vlan, port21, switch_port, "edge", user_mac)
            fid = int(str(graph_vlan) + str(3))
            self.pushVlanFlow(switch, fid, graph_vlan, switch_port, port21, "edge", user_mac)
            fid = int(str(graph_vlan) + str(4))
            self.pushMACDestFlow(cpe, fid, user_vlan , port12, user_mac, user_port, graph_vlan)
        else:
            logging.debug("Cannot find a link between " + cpe + " and " + switch)
    
    def unlinkUser(self, user_mac):
        '''
        Unlink a user after his logout and graph deletion
        Args:
            user_mac:
                MAC address of the user's device
        '''
        #flows = get_user_flows(user_mac)
        #for flow in flows:
        #    ODL().deleteFlow(flow.switch_id, flow.id)
        #    remove_flow(flow.id, flow.switch_id)
        pass
            
    def removeInternalFlows(self):
        '''
        Deletes all internal links between graphs (useful while shutting down)
        '''
        #flows = get_internal_flows()
        #for flow in flows:
        #    ODL().deleteFlow(flow.switch_id, flow.id)
        #    remove_flow(flow.id, flow.switch_id)
        pass
    
    def removeEdgeFlows(self):
        '''
        Deletes all users links with their graphs (useful while shutting down)
        '''
        #flows = get_edge_flows()
        #for flow in flows:
        #    ODL().deleteFlow(flow.switch_id, flow.id)
        #    remove_flow(flow.id, flow.switch_id)
        pass  
    '''
    ######################################################################################################
    ###############################       Manage graphs connection        ################################
    ######################################################################################################
    ''' 
    
    #TODO: interface e node da inserire al posto delle sole interface
    
    def connectEndpoints(self, nf_fg):
        '''
        Read nf_fg endpoints and create corrisponding flows on the SDN network
        Expecting some precise endpoint descriptions which reflect Orchestration layer scheduling choices
        '''
        #Get egress endpoints of the graph        
        endpoints = nf_fg.getVlanEgressEndpoints()
        for endpoint in endpoints:
            if endpoint.connection is True:
                # Check if the remote graph exists and the requested endpoint is available
                #session = get_active_user_session_by_nf_fg_id(endpoint.remote_graph)
                #if DEBUG_MODE is True:
                #    logging.debug("session: "+str(session.id))
                #existing_endpoints = get_available_endpoints_by_id(endpoint.remote_graph, endpoint.id)
                existing_endpoints = None
                if existing_endpoints is not None:
                    tmp = endpoint.interface
                    tmpList = tmp.split(":")
                    switch1 = tmpList[0] + ":" + tmpList[1]
                    port1 = tmpList[2]
                    
                    tmp = endpoint.remote_interface
                    tmpList = tmp.split(":")
                    switch2 = tmpList[0] + ":" + tmpList[1]
                    port2 = tmpList[2]
                    
                    vlan = endpoint.id
                    self.linkZones(switch1, port1, switch2, port2, vlan)
                    #updateEndpointConnection(endpoint.remote_graph, endpoint.remote_id, nf_fg.id, endpoint.id)
                else:
                    logging.error("Remote graph " + endpoint.remote_graph + " has not a " + endpoint.id + " endpoint available!")
        
        #Get ingress endpoints of the graph (auth graph has the same endpoint but without user_mac)
        endpoints = nf_fg.getVlanIngressEndpoints()
        for endpoint in endpoints:
            if endpoint.attached is True:    
                graph_vlan = endpoint.remote_id
                user_vlan = endpoint.id
                user_mac = endpoint.user_mac
                    
                tmp = endpoint.interface
                tmpList = tmp.split(":")
                cpe = tmpList[0] + ":" + tmpList[1]
                cpe_port = tmpList[2]
                    
                tmp = endpoint.remote_interface
                tmpList = tmp.split(":")
                switch = tmpList[0] + ":" + tmpList[1]
                switch_port = tmpList[2]
                    
                self.linkUser(cpe, cpe_port, switch, switch_port, graph_vlan, user_vlan, user_mac)
    
    def updateEndpoints(self, new_nf_fg, old_nf_fg):     
        #Check ingress endpoint of the graph
        new_endpoints = new_nf_fg.getVlanEgressEndpoints()
        old_endpoints = old_nf_fg.getVlanEgressEndpoints()
        
        if self.checkEquality(new_endpoints, old_endpoints) == False:
            self.disconnectEndpoints(old_nf_fg)
            self.connectEndpoints(new_nf_fg)
            return
        
        #Check egress endpoints of the graph
        new_endpoints = new_nf_fg.getVlanIngressEndpoints()
        old_endpoints = old_nf_fg.getVlanIngressEndpoints()
        
        if self.checkEquality(new_endpoints, old_endpoints) == False:
            self.disconnectEndpoints(old_nf_fg)
            self.connectEndpoints(new_nf_fg)
            return
        
    def disconnectEndpoints(self, nf_fg):
        '''
        Deletes flows after a profile deletion
        Args:
            nf_fg:
                JSON Object for the user profile graph (forwarding graph)
        '''
        endpoints = nf_fg.getVlanEgressEndpoints()
        for endpoint in endpoints:           
            vlan = endpoint.id            
            self.unlinkZones(vlan)
        
        endpoints = nf_fg.getVlanIngressEndpoints()
        for endpoint in endpoints:
            user_mac = endpoint.user_mac
            self.unlinkUser(user_mac)
        
        #delete_endpoint_connections(nf_fg.id)
        
    def checkEquality(self, new_endpoints, old_endpoints):
        '''
        Check if two endpoints are equivalent or not
        '''
        #Actually supports only one endpoint for every vector
        if len(new_endpoints) != len(old_endpoints):
            return False
        
        if len(new_endpoints) == 0:
            return True
        
        new_end = new_endpoints[0]
        old_end = old_endpoints[0]
        
        new_id = new_end.id
        new_interface = new_end.interface
        new_remote_id = new_end.remote_id
        new_remote_int = new_end.remote_interface
        new_remote_graph = new_end.remote_graph
        
        old_id = old_end.id                                
        old_interface = old_end.interface
        old_remote_id = old_end.remote_id
        old_remote_int = old_end.remote_interface
        old_remote_graph = old_end.remote_graph
                                        
        if new_id != old_id or new_interface != old_interface or new_remote_id != old_remote_id or new_remote_int != old_remote_int or new_remote_graph != old_remote_graph:
            return False
        
        if new_end.user_mac is not None:
            if new_end.user_mac != old_end.user_mac:
                return False
        
        return True