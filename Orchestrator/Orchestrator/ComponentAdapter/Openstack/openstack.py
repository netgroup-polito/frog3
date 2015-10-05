'''
Created on Oct 1, 2014

@author: fabiomignini
'''
from __future__ import division
import logging
import json
import os
import hashlib
import time, copy
from Common.config import Configuration
from Orchestrator.ComponentAdapter.Openstack.rest import Nova, Heat, Glance, ODL, Neutron
from Orchestrator.ComponentAdapter.interfaces import OrchestratorInterface
from Common.NF_FG.nf_fg import NF_FG, Node, Link, Action
from Common.Manifest.manifest import Manifest
from Orchestrator.ComponentAdapter.Common.nffg_management import NFFG_Management
from Orchestrator.ComponentAdapter.Openstack.resources import FlowRoute,Net,Port,ProfileGraph,VNF
from Common.SQL.graph import Graph
from Common.exception import NoHeatPortTranslationFound, StackError, NodeNotFound, DeletionTimeout
from threading import Thread
from Orchestrator.ComponentAdapter.Openstack.ovsdb import OVSDB
from Orchestrator.ComponentAdapter.OpenstackCommon.authentication import KeystoneAuthentication


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
    
    def __init__(self, session_id, userdata, node):
        '''
        Initialized the Heat translation object from the user profile
        params:
            heatEndpoint:
                The list of the heatEndpoints of the Open Stack service (it takes the first one)
            novaEndpoint:
                The list of the novaEndpoints of the Open Stack service (it takes the first one)
        '''
        
        self.session_id = session_id
        self.token = KeystoneAuthentication(node.openstack_controller, userdata.tenant, userdata.username, userdata.password)
        self.compute_node_address = node.domain_id
        self._URI = "http://"+self.compute_node_address
        self.novaEndpoint = self.token.get_endpoints('compute')[0]['publicURL']
        self.glanceEndpoint = self.token.get_endpoints('image')[0]['publicURL']
        self.neutronEndpoint = self.token.get_endpoints('network')[0]['publicURL']
        self.ovsdb = OVSDB(self.odlendpoint, self.odlusername, self.odlpassword, self.compute_node_address)
        odl = Node().getOpenflowController(node.openflow_controller)
        self.odlendpoint = odl.endpoint
        self.odlusername = odl.username
        self.odlpassword = odl.password
        
    
    @property
    def URI(self):
        return self._URI
    
    '''
    '''
    ######################################################################################################
    #########################    Orchestrator interface implementation        ############################
    ######################################################################################################
    
    def getStatus(self, session_id, node_endpoint):
        self.node_endpoint = node_endpoint
        return self.openstackResourcesStatus(self.token.get_token())
    
    def deinstantiateProfile(self, nffg, node_endpoint):
        '''
        Override method of the abstract class for deleting the user Stack
        '''
        self.node_endpoint = node_endpoint

        token_id = self.token.get_token()
    
        if DEBUG_MODE is not True:
            self.openstackResourcesDeletion(token_id, copy.deepcopy(nffg))
                        
        # Disconnect exit switch from graph
        self.deleteEndpoints(nffg) 
    
    def instantiateProfile(self, nffg, node_endpoint):
        '''
        Override method of the abstract class for instantiating the user Stack
        '''
        self.node_endpoint = node_endpoint   
        try:            
            # Create a drop flow that match all packets, to avoid loop
            # when ODL doesn't set properly the tag vlan
            self.createIntegrationBridgeDropFlow()
            
            self.instantiateEndpoints(nffg)
            
            logging.debug("Heat :"+nffg.getJSON())
            
            token = self.token.get_token()
            if DEBUG_MODE is not True:
                # Fill HEAT model objects
                graph = ProfileGraph()
                for vnf in nffg.listVNF:
                    manifest = Manifest(vnf.manifest)
                    cpuRequirements = manifest.CPUrequirements.socket
                    logging.debug(manifest.uri)                    
                    graph.addEdge(VNF(vnf.id, vnf, Glance().get_image(manifest.uri, token)['id'],
                                       self.findFlavor(int(manifest.memorySize), int(manifest.rootFileSystemSize),
                                        int(manifest.ephemeralFileSystemSize), int(cpuRequirements[0]['coreNumbers']), token),
                                         vnf.availability_zone))
                
                for link in self.getLinks(nffg):
                    graph.addArch(FlowRoute(link))
                graph.vistGraph()
                #self.addPortsToEndpointSwitches(nf_fg, graph)
                
                self.openstackResourcesInstantiation(nffg, graph)

        except Exception as err:
            logging.error(err.message)
            logging.exception(err)
            #self.deleteGraphResorces(nffg._id, self.token)
            #set_error(self.token.get_userID())  
            raise
  
    def updateProfile(self, new_nf_fg, old_nf_fg, node_endpoint):
        updated_nffg = NFFG_Management().diff(old_nf_fg, new_nf_fg)
        token = self.token.get_token()
        logging.debug("diff: "+updated_nffg.getJSON())
        
        self.node_endpoint = node_endpoint   
        token_id = self.token.get_token()
        
        # Delete VNFs
        for vnf in updated_nffg.listVNF[:]:
            if vnf.status == 'to_be_deleted':
                self.deleteVNF(token_id, vnf)
            else:
                # Delete ports
                for port in vnf.listPort[:]:
                    if port.status == 'to_be_deleted':
                        self.deletePort(token_id, port)
                    else:
                        # Delete flow-rules
                        for flowrule in port.list_outgoing_label[:]:
                            if flowrule.status == 'to_be_deleted':
                                self.deleteFlowrule(token_id, port, flowrule)
                                port.list_outgoing_label.remove(flowrule)
                        for flowrule in port.list_ingoing_label[:]:
                            if flowrule.status == 'to_be_deleted':
                                self.deleteFlowrule(token_id, port, flowrule)
                                port.list_ingoing_label.remove(flowrule)
        
        # Delete end-point resources
        for endpoint in updated_nffg.listEndpoint[:]:
            if endpoint.status == 'to_be_deleted':
                self.deleteEndpoint(endpoint, updated_nffg)
                Graph().deleteEndpoint(endpoint.id, self.session_id)
                Graph().deleteEndpointResource(endpoint.id, self.session_id)
            
        # Wait for resource deletion
        for vnf in updated_nffg.listVNF[:]:
            if vnf.status == 'to_be_deleted':
                self.waitForVNFInstantiation(token_id, updated_nffg, vnf)
            else:
                for port in vnf.listPort[:]:
                    if port.status == 'to_be_deleted':
                        self.waitForPortInstantiation(token_id, vnf, port)
                    
        # Delete unused networks and subnets
        self.deleteUnusedNetworksAndSubnets(token_id)
        
        logging.debug("diff after: "+updated_nffg.getJSON())
        
        # Store, in initialize status, the new resources
        Graph().updateNFFG(updated_nffg, self.session_id)
        
        # Create a drop flow that match all packets, to avoid loop
        # when ODL doesn't set properly the tag vlan
        self.createIntegrationBridgeDropFlow()
        
        # Instantiate end-points
        self.instantiateEndpoints(updated_nffg)
        
        graph = ProfileGraph(Graph().getHigherNumberOfNet(self.session_id))
        for vnf in updated_nffg.listVNF:
            manifest = Manifest(vnf.manifest)
            cpuRequirements = manifest.CPUrequirements.socket
            logging.debug(manifest.uri)                    
            graph.addEdge(VNF(vnf.id, vnf, Glance().get_image(manifest.uri, token)['id'],
                               self.findFlavor(int(manifest.memorySize), int(manifest.rootFileSystemSize),
                                int(manifest.ephemeralFileSystemSize), int(cpuRequirements[0]['coreNumbers']), token),
                                 vnf.availability_zone, status = vnf.status))
        
        for link in self.getLinks(updated_nffg):
            graph.addArch(FlowRoute(link))
        graph.vistGraph()
        #self.addPortsToEndpointSwitches(nf_fg, graph)
        
        # Instantiate Resources
        self.openstackResourcesInstantiation(updated_nffg, graph)
    
    def instantiateEndpoints(self, nffg):
        for endpoint in nffg.listEndpoint[:]:
            if endpoint.status == 'new' or endpoint.status == None or endpoint.status == 'already_deployed':
                self.instantiateEndpoint(nffg, endpoint)
    
    def instantiateEndpoint(self, nffg, endpoint):
        if endpoint.type == 'ingress_interface':
            self.manageIngressEndpoint(endpoint)
        elif endpoint.type == 'egress_interface':
            self.manageExitEndpoint(nffg, endpoint)
        elif endpoint.type == 'ingress_gre_interface':
            raise NotImplementedError()
        elif endpoint.type == 'egress_gre_interface':
            raise NotImplementedError()
        elif endpoint.type is None and endpoint.connection is not True:
            self.deleteEndpointConnection(nffg, endpoint)
        if endpoint.connection is True:
            self.connectEndpoints(nffg, endpoint)
    
    def deleteEndpoints(self, nffg):
        logging.debug("Deleting endpoints")
        for endpoint in nffg.listEndpoint[:]:
            logging.debug("Deleting endpoint named "+str(endpoint.name))
            self.deleteEndpoint(endpoint, nffg)
        
    
    def deleteEndpoint(self, endpoint, nffg):
        logging.debug("Deleting endpoint type: "+str(endpoint.type))
        if endpoint.type == 'egress_interface':
            logging.debug("Deleting endpoint egress_interface "+str(endpoint.name))
            self.deleteExitEndpoint(nffg, endpoint)
        if endpoint.connection is True:
            self.disconnectEndpoint(endpoint, nffg)
        nffg.listEndpoint.remove(endpoint)
    
    def deleteFlowrule(self, token_id, port, flowrule):
        Neutron().deleteFlowrule(self.neutronEndpoint, token_id, flowrule.internal_id)
        Graph().deleteoOArch(flowrule.db_id, self.session_id)
        Graph().deleteFlowspec(flowrule.db_id, self.session_id)
        
    def deletePort(self, token_id, port):
        Neutron().deletePort(self.neutronEndpoint, token_id, port.internal_id)
        Graph().deleteFlowspecFromPort(self.session_id, port.db_id)
        Graph().deletePort(port.db_id, self.session_id)
    
    def deleteVNF(self, token_id, vnf):
        Nova().deleteServer(self.novaEndpoint, token_id, vnf.internal_id)
        Graph().deleteFlowspecFromVNF(self.session_id, vnf.db_id)
        Graph().deleteVNF(vnf.id, self.session_id)
        Graph().deletePort(None, self.session_id, vnf.db_id)
                
    def waitForPortInstantiation(self, token_id, vnf, port):
        while True:
            status = Neutron().getPortStatus(self.neutronEndpoint, token_id, port.internal_id)
            if status != 'ACTIVE':
                logging.debug("VNF "+vnf.internal_id+" status "+status)
                vnf.listPort.remove(port)
                break
            if status == 'ERROR':
                raise Exception('Port status ERROR - '+vnf.internal_id)
            logging.debug("Port "+vnf.internal_id+" status "+status)
            
    def waitForVNFInstantiation(self, token_id, nffg, vnf):
        while True:
            status = Nova().getServerStatus(self.novaEndpoint, token_id, vnf.internal_id)
            if status != 'ACTIVE':
                logging.debug("VNF "+vnf.internal_id+" status "+status)
                nffg.listVNF.remove(vnf)
                break
            if status == 'ERROR':
                raise Exception('VNF status ERROR - '+vnf.internal_id)
            logging.debug("VNF "+vnf.internal_id+" status "+status)
        
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
    
    def openstackResourcesStatus(self, token_id):
        resources_status = {}
        resources_status['networks'] = {}
        networks = Graph().getNetworks(self.session_id)
        for network in networks:
            resources_status['networks'][network.id] = Neutron().getNetworkStatus(self.neutronEndpoint, token_id, network.id)
        resources_status['subnets'] = {}
        subnets = Graph().getSubnets(self.session_id)
        for subnet in subnets:
            resources_status['subnets'][subnet.id] = Neutron().getSubNetStatus(self.neutronEndpoint, token_id, subnet.id)
        resources_status['ports'] = {}
        ports = Graph().getPorts(self.session_id)
        for port in ports:
            if port.type == 'openstack':
                resources_status['ports'][port.id] = Neutron().getPortStatus(self.neutronEndpoint, token_id, port.internal_id)
        resources_status['vnfs'] = {}
        vnfs = Graph().getVNFs(self.session_id)
        for vnf in vnfs:
            resources_status['vnfs'][vnf.id] = Nova().getServerStatus(self.novaEndpoint, token_id, vnf.internal_id)
        resources_status['flowrules'] = {}
        flowrules = Graph().getOArchs(self.session_id)
        
        # TODO: if the flowrule involve an endpoint that have no type, the status should not be checked in OS
        for flowrule in flowrules:
            if flowrule.internal_id is not None:
                resources_status['flowrules'][flowrule.id] = Neutron().getFlowruleStatus(self.neutronEndpoint, token_id, flowrule.internal_id)
            elif flowrule.status == 'complete':
                resources_status['flowrules'][flowrule.id] = 'ACTIVE'
            else:
                resources_status['flowrules'][flowrule.id] = 'not_found'
        
        num_resources = len(resources_status['networks'])+len(resources_status['subnets'])+len(resources_status['ports'])\
                        +len(resources_status['vnfs'])+len(resources_status['flowrules'])
        num_resources_completed = 0
        for value in resources_status['networks'].itervalues():
            logging.debug("network - "+value)
            if value == 'ACTIVE':
                num_resources_completed = num_resources_completed + 1
        for value in resources_status['subnets'].itervalues():
            logging.debug("subnet - "+value)
            if value == 'ACTIVE':
                num_resources_completed = num_resources_completed + 1
        for value in resources_status['ports'].itervalues():
            logging.debug("port - "+value)
            if value == 'ACTIVE':
                num_resources_completed = num_resources_completed + 1
        for value in resources_status['vnfs'].itervalues():
            logging.debug("vnf - "+value)
            if value == 'ACTIVE':
                num_resources_completed = num_resources_completed + 1
        for key, value in resources_status['flowrules'].iteritems():
            logging.debug("flowrule - "+value)
            logging.debug("flowrule key: "+str(key))
            if value == 'ACTIVE':
                num_resources_completed = num_resources_completed + 1
        status  = {}
        logging.debug("num_resources_completed "+str(num_resources_completed))
        logging.debug("num_resources "+str(num_resources))
        if num_resources_completed == num_resources:
            status['status'] = 'complete'
            status['percentage_completed'] = num_resources_completed/num_resources*100
        else:
            status['status'] = 'in_progress'
            status['percentage_completed'] = num_resources_completed/num_resources*100
        return status
    
    def deleteUnusedNetworksAndSubnets(self, token_id):
        unused_networks_ref = Graph().getUnusedNetworks()
        for unused_network_ref in unused_networks_ref:
            subnet_id = Graph().getSubnet(unused_network_ref.id).id
            Neutron().deleteSubNet(self.neutronEndpoint, token_id, subnet_id)
            Graph().deleteSubnet(unused_network_ref.id)
            Neutron().deleteNetwork(self.neutronEndpoint, token_id, unused_network_ref.id)
            Graph().deleteNetwok(unused_network_ref.id)
                
    def openstackResourcesDeletion(self, token_id, nffg):
        subnets = Graph().getSubnets(self.session_id)
        networks = Graph().getNetworks(self.session_id)
        flowrules = Graph().getOArchs(self.session_id)
        for flowrule in flowrules:
            Neutron().deleteFlowrule(self.neutronEndpoint, token_id, flowrule.internal_id)
        vnfs = Graph().getVNFs(self.session_id)
        for vnf in vnfs:
            Nova().deleteServer(self.novaEndpoint, token_id, vnf.internal_id)   
        for vnf in nffg.listVNF:
            self.waitForVNFInstantiation(token_id, nffg, vnf)
        ports = Graph().getPorts(self.session_id)
        for port in ports:
            Neutron().deletePort(self.neutronEndpoint, token_id, port.internal_id)
        for vnf in nffg.listVNF:
            for port in vnf.listPort:
                self.waitForPortInstantiation(token_id, vnf, port)     
        for subnet in subnets:
            Neutron().deleteSubNet(self.neutronEndpoint, token_id, subnet.id)
        for network in networks:
            Neutron().deleteNetwork(self.neutronEndpoint, token_id, network.id)
    
    def openstackResourcesInstantiation(self, nffg, graph):
        for network in graph.networks:
            logging.debug("Network: "+json.dumps(network.getNetResourceJSON()))
            network.network_id = Neutron().createNetwork(self.neutronEndpoint, self.token.get_token(), network.getNetResourceJSON())['network']['id']
            # Save the OS network in the db
            Graph().addOSNetwork(network.network_id, network.name)
            logging.debug("SubNet: "+json.dumps(network.getSubNetResourceJSON()))
            network.subnet_id = Neutron().createSubNet(self.neutronEndpoint, self.token.get_token(), network.getSubNetResourceJSON())['subnet']['id']
            Graph().addOSSubNet(network.subnet_id, network.name, network.network_id)
        for vnf in graph.edges.values():
            for port in vnf.listPort:
                logging.debug("Port: "+json.dumps(port.getResourceJSON())+" Status: "+str(port.status))
                if port.status == 'new':
                    if vnf.status == 'new':
                        port.port_id = Neutron().createPort(self.neutronEndpoint, self.token.get_token(), port.getResourceJSON())['port']['id']
                    else:
                        port.port_id = Neutron().createPort(self.neutronEndpoint, self.token.get_token(), port.getResourceJSON())['port']['id']
                        Nova().attachPort(self.novaEndpoint, self.token.get_token(), port.port_id, vnf.vnf_id)
                    Graph().setPortInternalID(port.name, nffg.getVNFByID(vnf.id).db_id, port.port_id, self.session_id, nffg.db_id, port_type='openstack')
                    Graph().setOSNetwork(port.net.network_id, port.name, nffg.getVNFByID(vnf.id).db_id, port.port_id, self.session_id, nffg.db_id)
            logging.debug("VNF: "+json.dumps(vnf.getResourceJSON())+" Status: "+str(vnf.status))
            if vnf.status == 'new':
                vnf.vnf_id = Nova().createServer(self.novaEndpoint, self.token.get_token(), vnf.getResourceJSON())['server']['id']
                Graph().setVNFInternalID(vnf.id, vnf.vnf_id, self.session_id, nffg.db_id)
        
        thread = Thread(target = self.setFlows, args = (graph, nffg ))
        thread.start()
        
    def setFlows(self, graph, nffg):
        while True:
            time.sleep(1)
            complete = True
            resources_status = {}
            resources_status['vnfs'] = {}
            vnfs = Graph().getVNFs(self.session_id)
            for vnf in vnfs:
                resources_status['vnfs'][vnf.internal_id] = Nova().getServerStatus(self.novaEndpoint, self.token.get_token(), vnf.internal_id)
            for value in resources_status['vnfs'].itervalues():
                if value != 'ACTIVE':
                    complete = False
            if complete is True:
                break
        for flow in graph.archs:
            vect = flow.getResourcesJSON(self.token.get_tenantID(), graph.edges)
            index = 0
            for flowroute in vect:
                logging.debug("Flowrule: "+json.dumps(flowroute)+" Status: "+str(flow.flowrules[index].status))
                if flow.flowrules[index].status == 'new' or flow.flowrules[index].status is None:
                    flowrule_id = Neutron().createFlowrule(self.neutronEndpoint, self.token.get_token(), flowroute)['flowrule']['id']
                    Graph().setOArchInternalID(flow.flowrules[index].id, flowrule_id, self.session_id, nffg.db_id)
                index = index + 1
        logging.debug("Instantiation of graph "+nffg.id+" completed")
    
    '''
    '''
    ######################################################################################################
    ###############################       Manage graphs connection        ################################
    ######################################################################################################
                  
    def connectEndpoints(self, nf_fg, endpoint):
        '''
        characterize the endpoints that should be connected to another graph
        '''
        # Getting remote graph's session
        if endpoint.type == 'openstack':
            remote_interface = endpoint.interface
            endpoint.interface = "INGRESS_tap"+str(endpoint.interface)[:11]
            endpoint.type = "remote_interface"
            nf_fg.characterizeEndpoint(endpoint, endpoint_type=endpoint.type, interface=endpoint.interface)
            # Add the connection in the database?
            Graph().updateEndpointType(endpoint.id, self.session_id, endpoint.type)
            # Update endpoint with new information
            remote_interface_id = Graph().getPortFromInternalID(remote_interface).id
            Graph().addEndpointResource(endpoint.db_id, endpoint.type, remote_interface_id, self.session_id)
        
    
    def disconnectEndpoint(self, endpoint, nffg):
        if endpoint.type == 'remote_interface':
            # TODO: delete flows
            pass
    
    def deleteEndpointConnection(self, nf_fg, endpoint):
        '''
        Delete connection to endpoints those are not connected to any interface or other graph
        '''        
        logging.debug("Deleting flow to endoints not characterized: "+str(endpoint.name))   
        
        ports = nf_fg.getVNFPortsConnectedToEndpoint(endpoint.id)
        logging.debug("NF-FG name: "+nf_fg.name)
        logging.debug("Endpoint - endpoint.name: "+endpoint.name)
        
        logging.debug("DELETING flows to not connected endpoint")
        deleted_flowrules = nf_fg.deleteEndpointConnections(endpoint)
        logging.debug("Flows deleted: "+str(deleted_flowrules))
        
        # Set the flowrules that connects end-points to complete status
        for deleted_flowrule in deleted_flowrules:
            Graph().updateOArch(deleted_flowrule)
        
        
        # These flows for now are useless, because we set a base drop flow in br-int.
        # Anyway if we would use them, they must be saved in the db, couse if we install a flow 
        # with the same matches and priority the ODL mechanism driver raise an exception that
        # cause the lost of samo following flow (Known bug).
        # Add drop flows to avoid that that packets match normal flows
        #for connected_port in ports:
        #    connected_port.setDropFlow()
        pass
        
                                       
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
    '''
    ######################################################################################################
    #########################    Manage external connection in the nodes        ##########################
    ######################################################################################################
    
    def createVirtualIngressNetwork(self, ip_address):
        ingress_patch_port = "to-br-int"
        
        self.ovsdb.createBridge(INGRESS_SWITCH)
        
        
        ingress_bridge_uuid = self.ovsdb.getBridgeUUID(INGRESS_SWITCH)
        self.ovsdb.createPort(ingress_patch_port, ingress_bridge_uuid)
        
        integration_bridge_uuid = self.ovsdb.getBridgeUUID(INTEGRATION_BRIDGE)
        self.ovsdb.createPort(INGRESS_PORT, integration_bridge_uuid)
        
        interface_id = self.ovsdb.getInterfaceUUID(self.ovsdb.getPortUUID(ingress_patch_port), ingress_patch_port)
        ODL().setPatchPort(self.odlendpoint, self.odlusername, self.odlpassword, interface_id, INGRESS_PORT, ingress_bridge_uuid, self.ovsdb.node_ip, self.ovsdb.ovsdb_port)
        interface_id = self.ovsdb.getInterfaceUUID(self.ovsdb.getPortUUID(INGRESS_PORT), INGRESS_PORT)
        ODL().setPatchPort(self.odlendpoint, self.odlusername, self.odlpassword, interface_id, ingress_patch_port, integration_bridge_uuid, self.ovsdb.node_ip, self.ovsdb.ovsdb_port)

    def createVirtualExitNetwork(self, nf_fg, exit_endpoint, ip_address):
        br_name = EXIT_SWITCH
        #Heat().createBridge(OVS_ENDPOINT, br_name)
        logging.debug("Creating exit network on node: "+self.ovsdb.node_ip+":"+self.ovsdb.ovsdb_port)
        self.ovsdb.createBridge(br_name)
        bridge_id_1 = self.ovsdb.getBridgeUUID(br_name)
        bridge_id_2 = self.ovsdb.getBridgeUUID(INTEGRATION_BRIDGE)
        # Connect exit interface on egress bridge
        '''
        node_id = get_node_id(ip_address)
        Disabled because the orchestrator dont't know the phisical ports of node 
        self.ovsdb.createPort(getEgressInterface(node_id), bridge_id_1)
        '''
        #self.ovsdb.createPort(EGRESS_PORT, bridge_id_1)
        
        # Create port that will be connected
        port1 = "port_"+exit_endpoint.id+"_"+nf_fg.name+"_"+self.token.get_userID()+"_to_"+INTEGRATION_BRIDGE
        port1 = str(hashlib.md5(port1).hexdigest())[0:14]
        logging.debug("port1: "+port1)
        self.ovsdb.createPort(port1, bridge_id_1)
        port2 = "port_"+exit_endpoint.id+"_"+nf_fg.name+"_"+self.token.get_userID()+"_to_"+br_name
        port2 = str(hashlib.md5(port2).hexdigest())[0:14]
        logging.debug("port2: "+port2)
        self.ovsdb.createPort(port2, bridge_id_2)
        
        # Set the two port as patch port
        interface_id = self.ovsdb.getInterfaceUUID(self.ovsdb.getPortUUID(port1), port1)
        ODL().setPatchPort(self.odlendpoint, self.odlusername, self.odlpassword, interface_id, port2, bridge_id_1, self.ovsdb.node_ip, self.ovsdb.ovsdb_port)
        interface_id = self.ovsdb.getInterfaceUUID(self.ovsdb.getPortUUID(port2), port2)
        ODL().setPatchPort(self.odlendpoint, self.odlusername, self.odlpassword, interface_id, port1, bridge_id_2, self.ovsdb.node_ip, self.ovsdb.ovsdb_port)
        return port2
            
    def deleteVirtualExitNetwork(self, nf_fg, port1, port2, ip_address):
        logging.debug("Deleting exit network on node: "+self.ovsdb.node_ip+":"+self.ovsdb.ovsdb_port)
        self.ovsdb.deletePort(port1)
        self.ovsdb.deletePort(port2)
    
    def manageIngressEndpoint(self, ingress_endpoint):    
        ingress_endpoint.interface = "INGRESS_"+ingress_endpoint.interface
        self.createVirtualIngressNetwork(self.compute_node_address)
        
    def manageExitEndpoint(self, nf_fg, exit_endpoint):
        '''
        Characterize exit endpoint with virtual interface that bring the traffic
        to a switch that is used to forward packets on the right graph
        '''
        logging.debug("Managing single exit endpoint : "+exit_endpoint.id)
        graph_exit_port = self.createVirtualExitNetwork(nf_fg, exit_endpoint, self.compute_node_address)
        exit_endpoint.interface = "INGRESS_"+graph_exit_port

    def deleteIngressEndpoint(self, nf_fg):
        self.deleteVirtualIngressNetwork(nf_fg, self.compute_node_address)

    def deleteExitEndpoint(self, nf_fg, exit_endpoint):
        '''
        Delete the connection between the switch where the VNFs are connected and the switch used to
        connect graphs to Internet
        '''

        logging.debug("Managing single exit endpoint : "+exit_endpoint.id)
        br_name = EXIT_SWITCH
        port1 = "port_"+exit_endpoint.id+"_"+nf_fg.name+"_"+self.token.get_userID()+"_to_"+INTEGRATION_BRIDGE
        port1 = str(hashlib.md5(port1).hexdigest())[0:14]
        port2 = "port_"+exit_endpoint.id+"_"+nf_fg.name+"_"+self.token.get_userID()+"_to_"+br_name
        port2 = str(hashlib.md5(port2).hexdigest())[0:14]
        '''
        deleting connection to the WAN on the node where the user is connected
        '''
        self.deleteVirtualExitNetwork(nf_fg, port1, port2, self.compute_node_address)
            
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
        integration_bridge_dpid = self.ovsdb.getBridgeDPID(INTEGRATION_BRIDGE)
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
        ODL().createFlowmod(self.odlendpoint, self.odlusername, self.odlpassword, flowmod, name, DPID)
      
    def getLinks(self, nffg):
        links = []
        j_links = {}
        j_links['links'] = []
        visited_link = False
        for vnf in nffg.listVNF:
            for port in vnf.listPort:
                node1 = Node(vnf.id, port.id)
                
                ########### Manage drop flows ############
                flowrules = port.getDropFlows()
                if len(flowrules) != 0:
                    for flowrule in flowrules:
                        flowrule.addIngressPort(node1)
                    link = Link(node1, None, flowrules)
                    links.append(link)  
                    j_links['links'].append(link.getJSON())  
                ###########################################
                
                
                #flowrules = port.getVNFPortsFlowruleSendingTrafficToVNFPort() 
                for flowrule in port.list_outgoing_label:
                    if flowrule.action.vnf is not None:
                        node2 = Node(flowrule.action.vnf['id'], flowrule.action.vnf['port'])
                        
                        # insert ingress port in the match of the flowrules
                        flowrules = port.getVNFPortsFlowruleSendingTrafficToVNFPort(flowrule.action.vnf['id'], flowrule.action.vnf['port'])                    
                        for flowrule in flowrules:
                            flowrule.addIngressPort(node1)
                            
                        flowrules1 = nffg.getVNFByID(flowrule.action.vnf['id']).getPortFromID(flowrule.action.vnf['port']).getVNFPortsFlowruleSendingTrafficToVNFPort(vnf.id, port.id)
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
                        if nffg.getEndpointMap()[flowrule.action.endpoint['id']].type is not None:
                            if "interface" in nffg.getEndpointMap()[flowrule.action.endpoint['id']].type:
                                interface = nffg.getEndpointMap()[flowrule.action.endpoint['id']].interface
                                
                        else:
                            interface = flowrule.action.endpoint['id']

                        if("INGRESS_" in interface):
                            bridge_datapath_id = self.ovsdb.getBridgeDatapath_id(interface.split("INGRESS_")[1])
                            if bridge_datapath_id is None:
                                raise Exception("Bridge datapath id doesn't found for this interface: "+str(interface.split("INGRESS_")[1]))
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
                                endpoint['type'] = nffg.getEndpointMap()[flowrule.action.endpoint['id']].type
                                flowrule.changeAction(Action("output", endpoint = endpoint))

                            
                        flowrules1 = port.getIngoingFlowruleToSpecificEndpoint(flowrule.action.endpoint['id'])
                        for flowrule in flowrules1:
                            flowrule.addIngressPort(node2)
                        
                        flowrules = flowrules + flowrules1
                        
                        
                        visited  = False
                        for link in links:
                            if link.node2 is not None and link.node2.isEqual(node1) and link.node1.isEqual(node2):
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
    
    '''
    '''
    ######################################################################################################
    ##########################    Find right flavor for virtual machine        ###########################
    ######################################################################################################
                        
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
                    findFlavor = flavor['id']
                    minData = flavor['vcpus'] - CPUrequirements + (flavor['ram'] - memorySize)/1024 + flavor['disk'] - rootFileSystemSize - int(ephemeralFileSystemSize or 0)
                elif (flavor['vcpus'] - CPUrequirements + (flavor['ram'] - memorySize)/1024 + flavor['disk'] - rootFileSystemSize - int(ephemeralFileSystemSize or 0)) < minData:
                    findFlavor = flavor['id']
                    minData = flavor['vcpus'] - CPUrequirements + (flavor['ram'] - memorySize)/1024 + flavor['disk'] - rootFileSystemSize - int(ephemeralFileSystemSize or 0)
        assert (findFlavor != None), "No flavor found.  memorySize: "+str(memorySize)+" rootFileSystemSize: "+str(rootFileSystemSize)+" ephemeralFileSystemSize: "+str(ephemeralFileSystemSize)+" CPUrequirements: "+str(CPUrequirements) 
        return findFlavor