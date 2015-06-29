'''
Created on Oct 1, 2014

@author: fabiomignini
'''

import collections
import logging
import json
import os
import hashlib
import time, copy
from Common.config import Configuration
from Orchestrator.ComponentAdapter.Openstack.rest import Nova, Heat, Glance, ODL
from Orchestrator.ComponentAdapter.interfaces import OrchestratorInterface
from Common.NF_FG.nf_fg import NF_FG, Node, Link, Action
from Common.Manifest.manifest import Manifest
from Common.NF_FG.nf_fg_managment import NF_FG_Management
"""
from Common.SQL.endpoint import set_endpoint, delete_endpoint_connections, get_endpoint_by_graph_id
from Common.SQL.component_adapter import set_extra_info, get_extra_info,update_extra_info
from Common.SQL.session import checkEgressNode, checkIngressNode, get_active_user_session_by_nf_fg_id,get_instantiated_profile, get_profile_by_id, set_error
from Common.SQL.nodes import getAvaibilityZoneByHostname, getEgressInterface, updateIPAddress, getNodeName, getIngressInterface, getNodeID,getAvaibilityZone,getIPAddress, get_node_id
"""
from Common.exception import NoHeatPortTranslationFound, StackError, NodeNotFound, DeletionTimeout

DEBUG_MODE = Configuration().DEBUG_MODE
ISP_INGRESS = Configuration().ISP_INGRESS
CONTROL_INGRESS = Configuration().CONTROL_INGRESS
INTEGRATION_BRIDGE = Configuration().INTEGRATION_BRIDGE
EGRESS_PORT = Configuration().EGRESS_PORT
EXIT_SWITCH = Configuration().EXIT_SWITCH
INGRESS_SWITCH = Configuration().INGRESS_SWITCH
INGRESS_PORT = Configuration().INGRESS_PORT

class HeatOrchestrator(OrchestratorInterface):
    '''
    Override class of the abstract class OrchestratorInterface
    '''
    STATUS = ['CREATE_IN_PROGRESS', 'CREATE_COMPLETE', 'CREATE_FAILED',  'DELETE_IN_PROGRESS', 'DELETE_COMPLETE', 'DELETE_FAILED', 'UPDATE_IN_PROGRESS', 'UPDATE_COMPLETE', 'UPDATE_FAILED']
    WRONG_STATUS = ['CREATE_FAILED','DELETE_FAILED', 'UPDATE_FAILED']
    
    def __init__(self, session_id):
        '''
        Initialized the Heat translation object from the user profile
        params:
            heatEndpoint:
                The list of the heatEndpoints of the Open Stack service (it takes the first one)
            novaEndpoint:
                The list of the novaEndpoints of the Open Stack service (it takes the first one)
        '''
        self._URI = None
        self.novaEndpoint = None
        self.session_id = session_id
        self.token = None
    
    @property
    def URI(self):
        return self._URI
    
    
    '''
    ######################################################################################################
    #########################    Orchestrator interface implementation        ############################
    ######################################################################################################
    '''
    
    def getStatus(self, session_id, node_endpoint):
        pass
    
    def deinstantiateProfile(self, token, profile_id, profile=None):
        '''
        Override method of the abstract class for deleting the user Stack
        '''
        '''
        self.token = token
        token = token.get_token()
        logging.debug(profile)
        nf_fg = NF_FG(json.loads(profile))  
        
        # Delete endpoint from db
        delete_endpoint_connections(nf_fg._id) 
        # Send request to Heat to delete the stack
        if DEBUG_MODE is not True:
            # TODO: if 404 set stack in error
            Heat().deleteStack(self.URI, token, nf_fg.name , Heat().getStackID(self.URI, token, nf_fg.name))                   
        # Disconnect exit switch from graph
        self.deleteExitEndpoint(nf_fg) 
        
        self.deleteIngressEndpoint(nf_fg)
        '''
        pass
    
    def instantiateProfile(self, nf_fg, token):
        '''
        Override method of the abstract class for instantiating the user Stack
        '''
        '''
        self.token = token
        #logging.debug("Heat :"+json.dumps(nf_fg))
        nf_fg = NF_FG(nf_fg)
        
        
        # TODO: This call should be moved in the SLApp
        # also save available endpoints
        self.deleteEndpointConnection(nf_fg)
        try:
            # Create a drop flow that match all packets, to avoid loop
            # when ODL doesn't set properly the tag vlan
            self.createIntegrationBridgeDropFlow()
            
            # Manage ingress endpoint
            self.manageIngressEndpoint()
            
            # Manage exit endpoint
            self.manageExitEndpoint(nf_fg)
            
            # Add flows to remote endpoints
            self.connectEndpoints(nf_fg, token)
            
            logging.debug("Heat :"+nf_fg.getJSON())
            
            token = token.get_token()
            if DEBUG_MODE is not True:
                # Fill HEAT model objects
                graph = ProfileGraph()
                for vnf in nf_fg.listVNF:
                    manifest = Manifest(vnf.manifest)
                    cpuRequirements = manifest.CPUrequirements.socket
                    logging.debug(manifest.uri)                    
                    graph.addEdge(VNF(vnf.id, vnf, Glance().get_image_name(manifest.uri, token),
                                       self.findFlavor(int(manifest.memorySize), int(manifest.rootFileSystemSize),
                                        int(manifest.ephemeralFileSystemSize), int(cpuRequirements[0]['coreNumbers']), token),
                                         getAvaibilityZone(getNodeID(self.token.get_userID()))))
                
                for link in NFFG(nf_fg).getLinks(self):
                    graph.addArch(FlowRoute(link))
                graph.vistGraph()
                #self.addPortsToEndpointSwitches(nf_fg, graph)
                
                
                
                
                stackTemplate = graph.getStackTemplate()
                logging.debug(json.dumps(stackTemplate))
                res = Heat().instantiateStack(self.URI, token, nf_fg.name, stackTemplate)
                logging.debug("Heat response: "+str(res))        
                
                # TODO: take response from getStackResourcesStatus
                
                complete = False
                endpoints = get_endpoint_by_graph_id(nf_fg._id)
                if endpoints is not None:
                    while complete is not True:
                        time.sleep(1)
                        logging.debug("-------------")
                        complete = True
                        resources = self.getStackResourcesStatus(token, nf_fg.name)
                        for resource in resources['resources']:
                            for endpoint in endpoints:
                                if resource['resource_name'] == endpoint.Endpoint_ID:
                                    logging.debug(resource['resource_status'])
                                    logging.debug(resource['physical_resource_id'])
                                    if resource['resource_status'] != "CREATE_COMPLETE" and resource['resource_status'] != "CREATE_IN_PROGRESS":
                                        complete = False
                        if self.checkErrorStatus(self.token, nf_fg.name) is True:
                            logging.debug("Stack error, checks HEAT logs.")
                            raise StackError("Stack error, checks HEAT logs.")   
                        
                resources = json.dumps(self.getStackResourcesStatus(token, nf_fg.name))
        except Exception as err:
            logging.error(err.message)
            logging.exception(err)
            self.deleteGraphResorces(nf_fg._id, self.token)
            set_error(self.token.get_userID())  
            raise
        # TODO if the entry exists, update it
        #set_extra_info(self.session_id, resources)
        '''
        pass
  
    def updateProfile(self, new_nf_fg, old_nf_fg, token, node_endpoint):
        '''
        self.token = token
        token = token.get_token()
        new_nf_fg = NF_FG(new_nf_fg)
        
        logging.debug("updating profile...")
        # Manage exit endpoint
        self.manageExitEndpoint(new_nf_fg)
        # Add flows to remote endpoints
        self.connectEndpoints(new_nf_fg, token)
        
        logging.debug("Heat :"+new_nf_fg.getJSON())
        
        if DEBUG_MODE is not True:
            # Fill HEAT model objects
            graph = ProfileGraph()
            for vnf in new_nf_fg.listVNF:
                manifest = Manifest(vnf.manifest)
                cpuRequirements = manifest.CPUrequirements.socket
                logging.debug(manifest.uri)
                graph.addEdge(VNF(vnf.id, vnf, Glance().get_image_name(manifest.uri, token),
                                   self.findFlavor(int(manifest.memorySize), int(manifest.rootFileSystemSize),
                                    int(manifest.ephemeralFileSystemSize), int(cpuRequirements[0]['coreNumbers']), token),
                                     getAvaibilityZone(getNodeID(self.token.get_userID()))))
            for link in NFFG(new_nf_fg).getLinks(self):
                graph.addArch(FlowRoute(link))
            graph.vistGraph()
            self.addPortsToEndpointSwitches(new_nf_fg, graph)
            
            
            
            
            stackTemplate = graph.getStackTemplate()
            logging.debug(json.dumps(stackTemplate))
            
            
            res = Heat().updateStack(self.URI, token, new_nf_fg.name , Heat().getStackID(self.URI, token, new_nf_fg.name),stackTemplate)
            logging.debug("Heat response: "+str(res))        
            
            # Update resources in db            
            complete = False
            endpoints = get_endpoint_by_graph_id(new_nf_fg._id)
            while complete is not True:
                time.sleep(4)
                logging.debug("-------------")
                complete = True
                resources = self.getStackResourcesStatus(token, new_nf_fg.name)
                for resource in resources['resources']:
                    for endpoint in endpoints:
                        if resource['resource_name'] == endpoint.Endpoint_ID:
                            logging.debug(resource['resource_status'])
                            logging.debug(resource['physical_resource_id'])
                            if resource['resource_status'] != "CREATE_COMPLETE" and resource['resource_status'] != "CREATE_IN_PROGRESS":
                                complete = False
            resources = json.dumps(self.getStackResourcesStatus(token, new_nf_fg.name))
            update_extra_info(self.session_id, resources)
        '''
        pass
"""
              
    def getStackResourcesStatus(self, token, name):
        '''
        Return the status of the Stack
        '''
        # TODO: Manage cache
        if DEBUG_MODE is not True:
            stack_id = Heat().getStackID(self.URI, token, name)
            return Heat().getStackResourcesStatus(self.URI, token, name, stack_id)
    
    def getStackStatus(self, token, name):
        '''
        Return the status of the Stack
        '''
        stack_id = Heat().getStackID(self.URI, token, name)
        return Heat().getStackStatus(self.URI, token, stack_id)
     
    def checkProfile(self, session_id, token):
        '''
        Override method of the abstract class for check the user Stack
        '''
        profile = get_instantiated_profile(token.get_userID())
        nf_fg = NF_FG(json.loads(profile))
        try:
            stack_info = self.getStackStatus(token.get_token(), nf_fg.name)
            logging.debug("stack info: "+stack_info)
        except Exception as ex:
            logging.debug("checkProfile: "+str(ex))
            return False

        return True    
    
    def checkErrorStatus(self, token, graph_name):
        try:
            stack_info = self.getStackStatus(token.get_token(), graph_name)
            logging.debug("stack info: "+stack_info)
        except Exception as ex:
            logging.debug("checkErrorStatus: "+str(ex))
            return True
    
        if stack_info in self.WRONG_STATUS:
            return True

        return False
      
    def deleteGraphResorces(self, profile_id, token):
        self.token = token
        token = token.get_token()
        profile = get_profile_by_id(profile_id)
        nf_fg = NF_FG(json.loads(profile))
        
        # Delete endpoint from db
        delete_endpoint_connections(nf_fg._id) 
                
        # Disconnect exit switch from graph
        self.deleteExitEndpoint(nf_fg) 
        logging.debug("resource of graph "+nf_fg.name+" of user "+self.token.get_username()+" deleted.")
        
    '''
    ######################################################################################################
    ###############################       Manage graphs connection        ################################
    ######################################################################################################
    '''
                  
    def connectEndpoints(self, nf_fg, token):
        '''
        characterize the endpoints that should be connected to another graph
        '''
        endpoints = nf_fg.getEndpointThatShouldBeConnected()

        for endpoint in endpoints:
            if endpoint.connection is True:
                # Getting remote graph's session
                session = get_active_user_session_by_nf_fg_id(endpoint.remote_graph)
                logging.debug("session: "+str(session.id))
                extra = get_extra_info(session.id)
                logging.debug("extra: "+str(extra))
                resources = json.loads(extra)['resources']
                
                # For every endpoints that should be connected we convert the heat port id to the right port id
                match = False
                for resource in resources:
                    if resource['resource_name'] == endpoint.remote_id:
                        endpoint.type = "physical"
                        logging.debug("id porta fisica: "+str(resource['physical_resource_id']))
                        endpoint.interface = "INGRESS_tap"+str(resource['physical_resource_id'])[:11]
                        nf_fg.characterizeEndpoint(endpoint, endpoint_type=endpoint.type, interface=endpoint.interface)
                        match = True
                        break
                if match is False:
                    raise NoHeatPortTranslationFound("No traslation found for remote graph's port "+str(endpoint.remote_id))
                 
    def deleteEndpointConnection(self, nf_fg):
        '''
        Delete connection to endpoints those are not connected to any interface or other graph
        Insert those endpoints in db as available endpoints          
        '''        
        logging.debug("Here: "+nf_fg.getJSON())
        for endpoint in nf_fg.listEndpoint:
            if endpoint.connection is False and endpoint.attached is False and endpoint.edge is False:
                logging.debug("Deleting flow to endoints not characterized: "+str(endpoint.name))   
                
                edge_endpoints = nf_fg.getEdgeEndpoint(endpoint.name, True)  
                if len(edge_endpoints) == 0:
                    ports = nf_fg.getVNFPortsConnectedToEndpoint(endpoint.id)
                    logging.debug("NF-FG name: "+nf_fg.name)
                    logging.debug("Endpoint - endpoint.name: "+endpoint.name)
                    
                    logging.debug("DELETING flows to not connected endpoint")
                    nf_fg.deleteEndpointConnections(endpoint)
                    # Add drop flows to avoid that that packets match normal flows
                    for connected_port in ports:
                        connected_port.setDropFlow()
                else:    
                    endpoint_switch = nf_fg.getEndpointSwitchByEdgeEndpoints(edge_endpoints[0])
                    ports = endpoint_switch.getPortConnectedToEndpoints()
                    logging.debug("NF-FG name: "+nf_fg.name)
                    logging.debug("Endpoint - endpoint.name: "+endpoint.name)
                    
                    # Delete flows from endpoint switch to endpoints
                    
                    for edge_endpoint in edge_endpoints:  
                        logging.debug("DELETING flows to not connected endpoint")
                        connected_ports = nf_fg.getVNFPortsConnectedToEndpoint(edge_endpoint.id)
                        nf_fg.deleteEndpointConnections(edge_endpoint)
                        # Add drop flows to avoid that that packets match normal flows
                        for connected_port in connected_ports:
                            connected_port.setDropFlow()
                    
                    
                # Write in DB endpoint 1 to n
                for port in ports:
                    set_endpoint(nf_fg._id, endpoint_switch._id+port.id, True, endpoint.name, endpoint._id, endpoint_type="interface")   
                    
    def addPortsToEndpointSwitches(self, nf_fg, graph):    
        ''' 
        Prepare ports that acts like endpoint, in practice insert neutron networks 
        to all vnf connected to not specialized endpoint.
        Other graphs will be able to connect to these ports.
        '''
        
        # TODO: get rid of CONTROL_INGRESS and ISP_INGRESS, but do this comparison based on 
        # characteristic of endpoint not based on their name (connection)
        net_counter = 0
        for endpoint in nf_fg.listEndpoint:
            if endpoint.name == CONTROL_INGRESS or endpoint.name == ISP_INGRESS:
                
                edge_endpoints = nf_fg.getEdgeEndpoint(endpoint.name, True)
                endpoint_switch = nf_fg.getEndpointSwitchByEdgeEndpoints(edge_endpoints[0])
                for edge_endpoint in edge_endpoints:
                    ports = nf_fg.getVNFPortsSendingTrafficToEndpoint(edge_endpoint._id)
                    for port in ports:
                        # create net
                        newNet = Net("Endpoint_net"+str(net_counter))
                        graph.networks.append(newNet)
                        net_counter = net_counter + 1
                        graph.edges[endpoint_switch.id].setNetwork(newNet,port.id)
                        '''
                        graph.edges[endpoint_switch.id].network[port.id] = newNet.name
                        '''

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
                    findFlavor = flavor['name']
                    minData = flavor['vcpus'] - CPUrequirements + (flavor['ram'] - memorySize)/1024 + flavor['disk'] - rootFileSystemSize - int(ephemeralFileSystemSize or 0)
                elif (flavor['vcpus'] - CPUrequirements + (flavor['ram'] - memorySize)/1024 + flavor['disk'] - rootFileSystemSize - int(ephemeralFileSystemSize or 0)) < minData:
                    findFlavor = flavor['name']
                    minData = flavor['vcpus'] - CPUrequirements + (flavor['ram'] - memorySize)/1024 + flavor['disk'] - rootFileSystemSize - int(ephemeralFileSystemSize or 0)
        return findFlavor

    '''
    ######################################################################################################
    #########################    Manage external connection in the nodes        ##########################
    ######################################################################################################
    '''
    
    def createVirtualIngressNetwork(self, ip_address):
        ingress_patch_port = "to-br-int"
        
        self.getNode(ip_address)
        self.createBridge(INGRESS_SWITCH)
        
        
        ingress_bridge_uuid = self.getBridgeUUID(INGRESS_SWITCH)
        self.createPort(ingress_patch_port, ingress_bridge_uuid)
        node_id = get_node_id(ip_address)
        '''
        Disabled because the orchestrator dont't know the phisical ports of node 
        if node_id is not None:
            self.createPort(getIngressInterface(node_id), ingress_bridge_uuid)
        '''
        
        integration_bridge_uuid = self.getBridgeUUID(INTEGRATION_BRIDGE)
        self.createPort(INGRESS_PORT, integration_bridge_uuid)
        
        interface_id = self.getInterfaceUUID(self.getPortUUID(ingress_patch_port), ingress_patch_port)
        ODL().setPatchPort(interface_id, INGRESS_PORT, ingress_bridge_uuid, self.node_ip, self.node_port)
        interface_id = self.getInterfaceUUID(self.getPortUUID(INGRESS_PORT), INGRESS_PORT)
        ODL().setPatchPort(interface_id, ingress_patch_port, integration_bridge_uuid, self.node_ip, self.node_port)

    def createVirtualExitNetwork(self, nf_fg, exit_endpoint, ip_address):
        br_name = EXIT_SWITCH
        #Heat().createBridge(OVS_ENDPOINT, br_name)
        self.getNode(ip_address)
        logging.debug("Creating exit network on node: "+self.node_ip+":"+self.node_port)
        self.createBridge(br_name)
        bridge_id_1 = self.getBridgeUUID(br_name)
        bridge_id_2 = self.getBridgeUUID(INTEGRATION_BRIDGE)
        # Connect exit interface on egress bridge
        node_id = get_node_id(ip_address)
        '''
        Disabled because the orchestrator dont't know the phisical ports of node 
        self.createPort(getEgressInterface(node_id), bridge_id_1)
        '''
        #self.createPort(EGRESS_PORT, bridge_id_1)
        
        # Create port that will be connected
        port1 = "port_"+exit_endpoint.id+"_"+nf_fg.name+"_"+self.token.get_userID()+"_to_"+INTEGRATION_BRIDGE
        port1 = str(hashlib.md5(port1).hexdigest())[0:14]
        logging.debug("port1: "+port1)
        self.createPort(port1, bridge_id_1)
        port2 = "port_"+exit_endpoint.id+"_"+nf_fg.name+"_"+self.token.get_userID()+"_to_"+br_name
        port2 = str(hashlib.md5(port2).hexdigest())[0:14]
        logging.debug("port2: "+port2)
        self.createPort(port2, bridge_id_2)
        
        # Set the two port as patch port
        interface_id = self.getInterfaceUUID(self.getPortUUID(port1), port1)
        ODL().setPatchPort(interface_id, port2, bridge_id_1, self.node_ip, self.node_port)
        interface_id = self.getInterfaceUUID(self.getPortUUID(port2), port2)
        ODL().setPatchPort(interface_id, port1, bridge_id_2, self.node_ip, self.node_port)
        return port2
    
    def deleteVirtualIngressNetwork(self, nf_fg, ip_address):
        ingress_patch_port = "to-br-int"
        
        node = get_node_id(ip_address)
        if checkIngressNode(node, nf_fg._id) == False:
            self.getNode(ip_address)
            logging.debug("Deleting ingress network on node: "+self.node_ip+":"+self.node_port)
            self.deletePort(ingress_patch_port)
            self.deletePort(INGRESS_PORT)
            '''
            Disabled because the orchestrator dont't know the phisical ports of node 
            self.deleteBridge(INGRESS_SWITCH)
            ''''
            
    def deleteVirtualExitNetwork(self, nf_fg, port1, port2, ip_address):
        self.getNode(ip_address)
        logging.debug("Deleting exit network on node: "+self.node_ip+":"+self.node_port)
        self.deletePort(port1)
        self.deletePort(port2)
    
    def manageIngressEndpoint(self):
        self.createVirtualIngressNetwork(self.getNodeIPAddress())

    def manageExitEndpoint(self, nf_fg):
        '''
        Characterize exit endpoint with virtual interface that bring the traffic
        to a switch that is used to forward packets on the right graph
        '''
        logging.debug("Check if Managing exit endpoints")
        if nf_fg.getStatusExitInterface() is True:
            logging.debug("Managing exit endpoints")
            exit_endpoints = nf_fg.getExitEndpoint()
            for exit_endpoint in exit_endpoints:
                logging.debug("Managing single exit endpoint : "+exit_endpoint.id)
                
                
                '''
                create connection to the WAN on the node where the user is connected
                '''
                graph_exit_port = self.createVirtualExitNetwork(nf_fg, exit_endpoint, self.getNodeIPAddress())
                
                exit_endpoint.type = "physical"
                exit_endpoint.interface = "INGRESS_"+graph_exit_port
                nf_fg.characterizeEndpoint(exit_endpoint, endpoint_type = exit_endpoint.type, interface = exit_endpoint.interface)

    def deleteIngressEndpoint(self, nf_fg):
        self.deleteVirtualIngressNetwork(nf_fg, self.getNodeIPAddress())

    def deleteExitEndpoint(self, nf_fg):
        '''
        Delete the connection between the switch where the VNFs are connected and the switch used to
        connect graphs to Internet
        '''
        
        if nf_fg.getStatusExitInterface() is True:
            logging.debug("Deleting exit endpoints reconciliation")
            exit_endpoints = nf_fg.getExitEndpoint()
            for exit_endpoint in exit_endpoints:
                logging.debug("Managing single exit endpoint : "+exit_endpoint.id)
                br_name = EXIT_SWITCH
                port1 = "port_"+exit_endpoint.id+"_"+nf_fg.name+"_"+self.token.get_userID()+"_to_"+INTEGRATION_BRIDGE
                port1 = str(hashlib.md5(port1).hexdigest())[0:14]
                port2 = "port_"+exit_endpoint.id+"_"+nf_fg.name+"_"+self.token.get_userID()+"_to_"+br_name
                port2 = str(hashlib.md5(port2).hexdigest())[0:14]
                
                '''
                deleting connection to the WAN on the node where the user is connected
                '''
                self.deleteVirtualExitNetwork(nf_fg, port1, port2, self.getNodeIPAddress())
    
    '''
    ######################################################################################################
    ####################################        OVSDB CALL        ########################################
    ######################################################################################################
    '''
    def getNode(self, ip_address = None): 
        nodes = json.loads(ODL().getNodes())['node']
        node_id = None
        for node in nodes:
            if node['type'] == "OVS":
                if ip_address is not None and ip_address == node['id'].split(':')[0]:
                    node_id = node['id']
        if node_id is None:
            raise NodeNotFound("Node "+str(ip_address)+" not found.")
        self.node_ip = node_id.split(":")[0]
        self.node_port = node_id.split(":")[1]
    
    def getBridgeDatapath_id(self, port_name):
        logging.debug("datapath id - portname - "+str(port_name))
        portUUID = self.getPortUUID(port_name)
        logging.debug("datapath id - portUUID - "+str(portUUID))
        datapath_id = self._getBridgeDatapath_id(portUUID)
        logging.debug("datapath id - datapath_id - "+str(datapath_id))
        return datapath_id
        
    def _getBridgeDatapath_id(self, portUUID):
        bridges = ODL().getBridges(self.node_ip, self.node_port)
        json_object = json.loads(bridges)['rows']
        for attribute, value in json_object.iteritems():
            for ports in value['ports'][1]:
                if ports[1] == portUUID:               
                    return value['datapath_id'][1][0]
            
    def getBridgeUUID(self, bridge_name):
        bridges = ODL().getBridges(self.node_ip, self.node_port)
        json_object = json.loads(bridges)['rows']
        for attribute, value in json_object.iteritems():
            if value['name'] == bridge_name:
                return attribute     
            
    def getBridgeDPID(self, bridge_name):
        bridges = ODL().getBridges(self.node_ip, self.node_port)
        json_object = json.loads(bridges)['rows']
        for attribute, value in json_object.iteritems():
            if value['name'] == bridge_name:
                return value['datapath_id'][1][0]  
        
    def getPortUUID(self, port_name): 
        ports = ODL().getPorts(self.node_ip, self.node_port)
        ports = json.loads(ports)['rows']
        for attribute, value in ports.iteritems():    
            if value['name'] == port_name:
                return attribute

    def getInterfaceUUID(self, port_id, port_name):
        interfaces = ODL().getInterfaces(port_id, self.node_ip, self.node_port)
        interfaces = json.loads(interfaces)['rows']
        for attribute, value in interfaces.iteritems():  
            if value['name'] == port_name:
                return attribute
            
    def createPort(self, port_name, bridge_id):
        if self.getPortUUID(port_name) is None:
            ODL().createPort(port_name, bridge_id, self.node_ip, self.node_port)
    
    def createBridge(self, bridge_name):
        if self.getBridgeUUID(bridge_name) is None:
            ODL().createBridge(bridge_name, self.node_ip, self.node_port)
        
    def deletePort(self, port_name):
        port_id = self.getPortUUID(port_name)
        if port_id is not None:
            ODL().deletePort(port_id, self.node_ip, self.node_port)
            
    def deleteBridge(self, bridge_name):
        bridge_id = self.getBridgeUUID(bridge_name)
        if bridge_id is not None:
            ODL().deleteBridge(bridge_id, self.node_ip, self.node_port)
            
    '''
    
    '''
    def deleteIntegrationBridgeDropFlow(self):
        
        pass
    
    def getNodeIPAddress(self):
        '''
        Retrie the IP address of the node from orchestrator DB, 
        if the IP address of the node is unknown it call getNodeIPAddressFromNova
        '''
        node_id = getNodeID(self.token.get_userID())
        ip_address = getIPAddress(node_id)
        if ip_address is None:
            node_name = getNodeName(node_id)
            ip_address = str(self.getNodeIPAddressFromNova(node_name))
            updateIPAddress(node_id, ip_address)
        return ip_address
            
    def getNodeIPAddressFromNova(self, node_name):
        '''
        Retrieve the IP address of the node from nova
        '''
        admin_token = copy.deepcopy(self.token)
        admin_token.get_info_by_Token(self.token.get_admin_token(), self.token.get_admin_token())
        hypervisors = json.loads(Nova().getHypervisorsInfo(admin_token.get_endpoints("compute").pop()['publicURL'], self.token.get_admin_token()))
        self.check_availability_zone(node_name)
        for hypervisor in hypervisors['hypervisors']:
            if hypervisor['hypervisor_hostname'] == node_name:
                logging.debug("Got ip address of the node from nova: "+str(hypervisor['host_ip']))
                return hypervisor['host_ip']      
    
    def check_availability_zone(self, node_name):
        '''
        Control if the node passed is in the right availability zone
        if not move the node in the correct availability zone
        '''
        admin_token = copy.deepcopy(self.token)
        admin_token.get_info_by_Token(self.token.get_admin_token(), self.token.get_admin_token())
        right_availability_zone = getAvaibilityZoneByHostname(node_name)
        availability_zones = json.loads(Nova().getAvailabilityZones(admin_token.get_endpoints("compute").pop()['publicURL'], self.token.get_admin_token()))
        for availability_zone in availability_zones['availabilityZoneInfo']:
            for attribute, value in availability_zone['hosts'].iteritems():
                if attribute != node_name:
                    continue
                if availability_zone['zoneName'] != right_availability_zone:
                    self.change_availability_zone(node_name, right_availability_zone)
                    
    def get_host_aggregate_id_from_availability_zone(self, availability_zone):
        admin_token = copy.deepcopy(self.token)
        admin_token.get_info_by_Token(self.token.get_admin_token(), self.token.get_admin_token())
        host_aggregate_list = json.loads(Nova().getHostAggregateList(admin_token.get_endpoints("compute").pop()['publicURL'], self.token.get_admin_token()))
        for host_aggregate in host_aggregate_list['aggregates']:
            if host_aggregate['availability_zone'] == availability_zone:
                return host_aggregate['id']
            
    def change_availability_zone(self, node_name, availability_zone):
        '''
        Change the availability zone of a node
        '''
        admin_token = copy.deepcopy(self.token)
        admin_token.get_info_by_Token(self.token.get_admin_token(), self.token.get_admin_token())
        
        host_aggregate_id = self.get_host_aggregate_id_from_availability_zone(availability_zone)
        Nova().addComputeNodeToHostAggregate(admin_token.get_endpoints("compute").pop()['publicURL'], self.token.get_admin_token(), host_aggregate_id, node_name)
        
    
    def createIntegrationBridgeDropFlow(self):
        self.getNode(self.getNodeIPAddress())
        integration_bridge_dpid = self.getBridgeDPID(INTEGRATION_BRIDGE)
        self.createDropFlow("STATIC_drop_"+str(integration_bridge_dpid),
                            integration_bridge_dpid,
                            "1")
    
    def createDropFlow(self, name, DPID, priority):
        '''
        flowmod = {
            "installInHw":"true",
            "name":"flow1",
            "node":{
                "id":"00:00:00:00:00:00:00:01",
                "type":"OF"
            },
            "ingressPort":"1",
            "priority":"500",
            "etherType":"0x800",
            "nwSrc":"10.0.0.1",
            "actions":["DROP"]
        }
        '''
        DPID = ':'.join([DPID[i:i+2] for i in range(0,len(DPID[0:16]),2)])
        flowmod = {
                    "installInHw":"true",
                    "name": name,
                    "node":{
                        "id": DPID,
                        "type":"OF"
                    },
                    "priority":priority,
                    "actions":["DROP"]
                  }
        ODL().createFlowmod(flowmod, name, DPID)
        
class HeatResource():
    def __init__(self, resources):
        self.resources = resources
      
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


    def __init__(self):
        '''
        Constructor of the Graph
        '''
        self.edges = {}
        self.archs = []
        self.networks = []
        #self.router = Router()
        self.switch = None
        self.num_net = 0
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
                
class VNF(object):
    '''
    Class that contains the VNF data that will be used on the profile generation
    '''


    def __init__(self, VNFId, vnf, imageName, flavor, availability_zone = None):
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
        
        template_info = VNFTemplate(vnf)
        for port in vnf.listPort:
            self.ports[port.id] = Port(port, VNFId)
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
                            
class Port(object):
    '''
    Class that contains the port data for the VNF
    '''        
    
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
        self.trash = None
        self.fip = None
        self.name = portTemplate.id
        self.network = None
        self.type = None
        self.VNFId = VNFId
        self.archs = []
        
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
                        if flowspec['action']['endpoint']['type'] == "physical":
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

class NFFG(object):

    def __init__(self, nffg):
        self.nffg = nffg
    
    def getLinks(self, heat_orchestrator):
        links = []
        j_links = {}
        j_links['links'] = []
        visited_link = False
        for vnf in self.nffg.listVNF:
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
                            
                        flowrules1 = self.nffg.getVNFByID(flowrule.action.vnf['id']).getPortFromID(flowrule.action.vnf['port']).getVNFPortsFlowruleSendingTrafficToVNFPort(vnf.id, port.id)
                        for flowrule in flowrules1:
                            flowrule.addIngressPort(node2)
                        
                        flowrules = flowrules + flowrules1
                        
                        
                        visited  = False
                        for link in links:
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
                        if self.nffg.getEndpointMap()[flowrule.action.endpoint['id']].type is not None:
                            if self.nffg.getEndpointMap()[flowrule.action.endpoint['id']].type == "physical":
                                interface = self.nffg.getEndpointMap()[flowrule.action.endpoint['id']].interface
                                
                        else:
                            interface = flowrule.action.endpoint['id']

                        if("INGRESS_" in interface):
                            bridge_datapath_id = heat_orchestrator.getBridgeDatapath_id(interface.split("INGRESS_")[1])
                            interface = "INGRESS_"+bridge_datapath_id+":"+interface.split("INGRESS_")[1]
                            logging.debug("port with datapath id of his router: "+str(interface))
                            node2 = Node(endpoint = interface)
                        else:
                            node2 = Node(endpoint = interface)
                            
                        # TODO: insert ingress port in the match of the flowrules
                        flowrules = port.getVNFPortsFlowruleSendingTrafficToEndpoint(flowrule.action.endpoint['id'])
                        for flowrule in flowrules:
                            flowrule.addIngressPort(node1)
                            if("INGRESS_" in interface):
                                endpoint = {}
                                endpoint['port'] = flowrule.action.endpoint['id']
                                endpoint['interface'] = interface
                                endpoint['type'] = "physical"
                                flowrule.changeAction(Action("output", endpoint = endpoint))

                            
                        flowrules1 = port.getIngoingFlowruleToSpecificEndpoint(flowrule.action.endpoint['id'])
                        for flowrule in flowrules1:
                            flowrule.addIngressPort(node2)
                        
                        flowrules = flowrules + flowrules1
                        
                        
                        visited  = False
                        for link in links:
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
        logging.debug("links: \n"+json.dumps(j_links))
        logging.debug("")
        return links
"""
    






