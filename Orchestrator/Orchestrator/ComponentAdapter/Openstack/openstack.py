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
    
    def __init__(self, session_id, compute_node_address, token):
        '''
        Initialized the Heat translation object from the user profile
        params:
            heatEndpoint:
                The list of the heatEndpoints of the Open Stack service (it takes the first one)
            novaEndpoint:
                The list of the novaEndpoints of the Open Stack service (it takes the first one)
        '''
        
        self.session_id = session_id
        self.token = token
        self.compute_node_address = compute_node_address
        self._URI = "http://"+compute_node_address
        self.novaEndpoint = token.get_endpoints('compute')[0]['publicURL']
        self.glanceEndpoint = token.get_endpoints('image')[0]['publicURL']
        self.neutronEndpoint = token.get_endpoints('network')[0]['publicURL']
    
    @property
    def URI(self):
        return self._URI
    
    
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
            self.openstackResourcesDeletion(token_id)               
        # Disconnect exit switch from graph
        self.deleteExitEndpoint(nffg) 
    
    def instantiateProfile(self, nffg, node_endpoint):
        '''
        Override method of the abstract class for instantiating the user Stack
        '''
        self.node_endpoint = node_endpoint   
        
        # TODO: This call should be moved in the SLApp
        # also save available endpoints
        #self.deleteEndpointConnection(nf_fg)
        try:
            # Create a drop flow that match all packets, to avoid loop
            # when ODL doesn't set properly the tag vlan
            self.createIntegrationBridgeDropFlow()
            
            # Manage ingress endpoint
            self.manageIngressEndpoint(nffg)
            
            # Manage exit endpoint
            self.manageExitEndpoint(nffg)
            
            # Add flows to remote endpoints
            self.connectEndpoints(nffg, self.token)
            
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
                
                for link in NFFG(nffg).getLinks(self):
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
                Nova().deleteServer(self.novaEndpoint, token_id, vnf.internal_id)
                Graph().deleteFlowspecFromVNF(self.session_id, vnf.db_id)
                Graph().deleteVNF(vnf.id, self.session_id)
                Graph().deletePort(None, self.session_id, vnf.db_id)
                
            else:
                # Delete ports
                for port in vnf.listPort[:]:
                    if port.status == 'to_be_deleted':
                        Neutron().deletePort(self.neutronEndpoint, token_id, port.internal_id)
                        Graph().deleteFlowspecFromPort(self.session_id, port.id)
                        Graph().deletePort(port.id, self.session_id)
                    else:
                        # Delete flow-rules
                        for flowrule in port.list_outgoing_label[:]:
                            if flowrule.status == 'to_be_deleted':
                                Neutron().deleteFlowrule(self.neutronEndpoint, token_id, flowrule.internal_id)
                                Graph().deleteoOArch(flowrule.db_id, self.session_id)
                                Graph().deleteFlowspec(flowrule.db_id, self.session_id)
                                port.list_outgoing_label.remove(flowrule)
                        for flowrule in port.list_ingoing_label[:]:
                            if flowrule.status == 'to_be_deleted':
                                Neutron().deleteFlowrule(self.neutronEndpoint, token_id, flowrule.internal_id)
                                Graph().deleteoOArch(flowrule.db_id, self.session_id)
                                Graph().deleteFlowspec(flowrule.db_id, self.session_id)
                                port.list_ingoing_label.remove(flowrule)
        
        # TODO: delete endpoint resources
        
        # Wait for resource deletion
        for vnf in updated_nffg.listVNF[:]:
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
                            logging.debug("Port "+vnf.internal_id+" status "+status)
                    
        # Delete unused networks and subnets
        self.deleteUnusedNetworksAndSubnets(token_id)
        
        logging.debug("diff after: "+updated_nffg.getJSON())
        
        # Store, in initialize status, the new resources
        Graph().updateNFFG(updated_nffg, self.session_id)
        
        # Create a drop flow that match all packets, to avoid loop
        # when ODL doesn't set properly the tag vlan
        self.createIntegrationBridgeDropFlow()
        
        # Manage ingress endpoint
        self.manageIngressEndpoint(updated_nffg)
        
        # Manage exit endpoint
        self.manageExitEndpoint(updated_nffg)
        
        graph = ProfileGraph(Graph().getHigherNumberOfNet(self.session_id))
        for vnf in updated_nffg.listVNF:
            manifest = Manifest(vnf.manifest)
            cpuRequirements = manifest.CPUrequirements.socket
            logging.debug(manifest.uri)                    
            graph.addEdge(VNF(vnf.id, vnf, Glance().get_image(manifest.uri, token)['id'],
                               self.findFlavor(int(manifest.memorySize), int(manifest.rootFileSystemSize),
                                int(manifest.ephemeralFileSystemSize), int(cpuRequirements[0]['coreNumbers']), token),
                                 vnf.availability_zone, status = vnf.status))
        
        for link in NFFG(updated_nffg).getLinks(self):
            graph.addArch(FlowRoute(link))
        graph.vistGraph()
        #self.addPortsToEndpointSwitches(nf_fg, graph)
        
        self.openstackResourcesInstantiation(updated_nffg, graph)
        
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
        for flowrule in flowrules:
            if flowrule.internal_id is not None:
                resources_status['flowrules'][flowrule.id] = Neutron().getFlowruleStatus(self.neutronEndpoint, token_id, flowrule.internal_id)
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
                
    def openstackResourcesDeletion(self, token_id):
        subnets = Graph().getSubnets(self.session_id)
        networks = Graph().getNetworks(self.session_id)
        flowrules = Graph().getOArchs(self.session_id)
        for flowrule in flowrules:
            Neutron().deleteFlowrule(self.neutronEndpoint, token_id, flowrule.internal_id)
        vnfs = Graph().getVNFs(self.session_id)
        for vnf in vnfs:
            Nova().deleteServer(self.novaEndpoint, token_id, vnf.internal_id)
        ports = Graph().getPorts(self.session_id)
        for port in ports:
            Neutron().deletePort(self.neutronEndpoint, token_id, port.internal_id)
        # TODO: if there are some network and subnet daesn't used, I have to delete them.
        for subnet in subnets:
            Neutron().deleteSubNet(self.neutronEndpoint, token_id, subnet.id)
        for network in networks:
            Neutron().deleteNetwork(self.neutronEndpoint, token_id, network.id)
    
    def openstackResourcesUpdate(self, nffg):
        pass
        
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
                
    def checkProfile(self, session_id, token):
        '''
        Override method of the abstract class for check the user Stack
        '''
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
        '''
        pass
    
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
        '''
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
        pass

    ######################################################################################################
    ###############################       Manage graphs connection        ################################
    ######################################################################################################
                  
    def connectEndpoints(self, nf_fg, token):
        '''
        characterize the endpoints that should be connected to another graph
        '''
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
           '''      
    def deleteEndpointConnection(self, nf_fg):
        '''
        Delete connection to endpoints those are not connected to any interface or other graph
        '''        
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

    ######################################################################################################
    #########################    Manage external connection in the nodes        ##########################
    ######################################################################################################
    
    def createVirtualIngressNetwork(self, ip_address):
        ingress_patch_port = "to-br-int"
        
        node_ip, ovsdb_port = self.getOvsdbNodeEndpoint(ip_address)
        self.createBridge(INGRESS_SWITCH, node_ip, ovsdb_port)
        
        
        ingress_bridge_uuid = self.getBridgeUUID(INGRESS_SWITCH, node_ip, ovsdb_port)
        self.createPort(ingress_patch_port, ingress_bridge_uuid, node_ip, ovsdb_port)
        
        integration_bridge_uuid = self.getBridgeUUID(INTEGRATION_BRIDGE, node_ip, ovsdb_port)
        self.createPort(INGRESS_PORT, integration_bridge_uuid, node_ip, ovsdb_port)
        
        interface_id = self.getInterfaceUUID(self.getPortUUID(ingress_patch_port, node_ip, ovsdb_port), ingress_patch_port, node_ip, ovsdb_port)
        ODL().setPatchPort(interface_id, INGRESS_PORT, ingress_bridge_uuid, node_ip, ovsdb_port)
        interface_id = self.getInterfaceUUID(self.getPortUUID(INGRESS_PORT, node_ip, ovsdb_port), INGRESS_PORT, node_ip, ovsdb_port)
        ODL().setPatchPort(interface_id, ingress_patch_port, integration_bridge_uuid, node_ip, ovsdb_port)

    def createVirtualExitNetwork(self, nf_fg, exit_endpoint, ip_address):
        br_name = EXIT_SWITCH
        #Heat().createBridge(OVS_ENDPOINT, br_name)
        node_ip, ovsdb_port = self.getOvsdbNodeEndpoint(ip_address)
        logging.debug("Creating exit network on node: "+node_ip+":"+ovsdb_port)
        self.createBridge(br_name, node_ip, ovsdb_port)
        bridge_id_1 = self.getBridgeUUID(br_name, node_ip, ovsdb_port)
        bridge_id_2 = self.getBridgeUUID(INTEGRATION_BRIDGE, node_ip, ovsdb_port)
        # Connect exit interface on egress bridge
        '''
        node_id = get_node_id(ip_address)
        Disabled because the orchestrator dont't know the phisical ports of node 
        self.createPort(getEgressInterface(node_id), bridge_id_1)
        '''
        #self.createPort(EGRESS_PORT, bridge_id_1)
        
        # Create port that will be connected
        port1 = "port_"+exit_endpoint.id+"_"+nf_fg.name+"_"+self.token.get_userID()+"_to_"+INTEGRATION_BRIDGE
        port1 = str(hashlib.md5(port1).hexdigest())[0:14]
        logging.debug("port1: "+port1)
        self.createPort(port1, bridge_id_1, node_ip, ovsdb_port)
        port2 = "port_"+exit_endpoint.id+"_"+nf_fg.name+"_"+self.token.get_userID()+"_to_"+br_name
        port2 = str(hashlib.md5(port2).hexdigest())[0:14]
        logging.debug("port2: "+port2)
        self.createPort(port2, bridge_id_2, node_ip, ovsdb_port)
        
        # Set the two port as patch port
        interface_id = self.getInterfaceUUID(self.getPortUUID(port1, node_ip, ovsdb_port), port1, node_ip, ovsdb_port)
        ODL().setPatchPort(interface_id, port2, bridge_id_1, node_ip, ovsdb_port)
        interface_id = self.getInterfaceUUID(self.getPortUUID(port2, node_ip, ovsdb_port), port2, node_ip, ovsdb_port)
        ODL().setPatchPort(interface_id, port1, bridge_id_2, node_ip, ovsdb_port)
        return port2
            
    def deleteVirtualExitNetwork(self, nf_fg, port1, port2, ip_address):
        node_ip, ovsdb_port = self.getOvsdbNodeEndpoint(ip_address)
        logging.debug("Deleting exit network on node: "+node_ip+":"+ovsdb_port)
        self.deletePort(port1, node_ip, ovsdb_port)
        self.deletePort(port2, node_ip, ovsdb_port)
    
    def manageIngressEndpoint(self, nf_fg):
        if nf_fg.getStatusIngressInterface() is True:
            ingress_endpoints = nf_fg.getIngressEndpoint()
        
            for ingress_endpoint in ingress_endpoints:
                ingress_endpoint.type = "physical"
                ingress_endpoint.interface = "INGRESS_"+ingress_endpoint.interface
                nf_fg.characterizeEndpoint(ingress_endpoint, endpoint_type = ingress_endpoint.type, interface = ingress_endpoint.interface)


        self.createVirtualIngressNetwork(self.compute_node_address)
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
                graph_exit_port = self.createVirtualExitNetwork(nf_fg, exit_endpoint, self.compute_node_address)
                
                exit_endpoint.type = "physical"
                exit_endpoint.interface = "INGRESS_"+graph_exit_port
                nf_fg.characterizeEndpoint(exit_endpoint, endpoint_type = exit_endpoint.type, interface = exit_endpoint.interface)

    def deleteIngressEndpoint(self, nf_fg):
        self.deleteVirtualIngressNetwork(nf_fg, self.compute_node_address)

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
                self.deleteVirtualExitNetwork(nf_fg, port1, port2, self.compute_node_address)
    
    ######################################################################################################
    ####################################        OVSDB CALL        ########################################
    ######################################################################################################
    
    def getOvsdbNodeEndpoint(self, ip_address = None): 
        nodes = json.loads(ODL().getNodes())['node']
        node_id = None
        for node in nodes:
            if node['type'] == "OVS":
                if ip_address is not None and ip_address == node['id'].split(':')[0]:
                    node_id = node['id']
        if node_id is None:
            raise NodeNotFound("Node "+str(ip_address)+" not found.")
        node_ip = node_id.split(":")[0]
        ovsdb_port = node_id.split(":")[1]
        return node_ip,  ovsdb_port
    
    def getBridgeDatapath_id(self, port_name, node_ip, ovsdb_port):
        logging.debug("datapath id - portname - "+str(port_name))
        portUUID = self.getPortUUID(port_name, node_ip, ovsdb_port)
        logging.debug("datapath id - portUUID - "+str(portUUID))
        datapath_id = self._getBridgeDatapath_id(portUUID, node_ip, ovsdb_port)
        logging.debug("datapath id - datapath_id - "+str(datapath_id))
        return datapath_id
        
    def _getBridgeDatapath_id(self, portUUID, node_ip, ovsdb_port):
        bridges = ODL().getBridges(node_ip, ovsdb_port)
        json_object = json.loads(bridges)['rows']
        for attribute, value in json_object.iteritems():
            for ports in value['ports'][1]:
                if ports[1] == portUUID:               
                    return value['datapath_id'][1][0]
            
    def getBridgeUUID(self, bridge_name, node_ip, ovsdb_port):
        bridges = ODL().getBridges(node_ip, ovsdb_port)
        json_object = json.loads(bridges)['rows']
        for attribute, value in json_object.iteritems():
            if value['name'] == bridge_name:
                return attribute     
            
    def getBridgeDPID(self, bridge_name, node_ip, ovsdb_port):
        bridges = ODL().getBridges(node_ip, ovsdb_port)
        json_object = json.loads(bridges)['rows']
        for attribute, value in json_object.iteritems():
            if value['name'] == bridge_name:
                return value['datapath_id'][1][0]  
        
    def getPortUUID(self, port_name, node_ip, ovsdb_port): 
        ports = ODL().getPorts(node_ip, ovsdb_port)
        ports = json.loads(ports)['rows']
        for attribute, value in ports.iteritems():    
            if value['name'] == port_name:
                return attribute

    def getInterfaceUUID(self, port_id, port_name, node_ip, ovsdb_port):
        interfaces = ODL().getInterfaces(port_id,node_ip, ovsdb_port)
        interfaces = json.loads(interfaces)['rows']
        for attribute, value in interfaces.iteritems():  
            if value['name'] == port_name:
                return attribute
            
    def createPort(self, port_name, bridge_id, node_ip, ovsdb_port):
        if self.getPortUUID(port_name, node_ip, ovsdb_port) is None:
            ODL().createPort(port_name, bridge_id, node_ip, ovsdb_port)
    
    def createBridge(self, bridge_name, node_ip, ovsdb_port):
        if self.getBridgeUUID(bridge_name, node_ip, ovsdb_port) is None:
            ODL().createBridge(bridge_name, node_ip, ovsdb_port)
        
    def deletePort(self, port_name, node_ip, ovsdb_port):
        port_id = self.getPortUUID(port_name, node_ip, ovsdb_port)
        if port_id is not None:
            ODL().deletePort(port_id, node_ip, ovsdb_port)
            
    def deleteBridge(self, bridge_name, node_ip, ovsdb_port):
        bridge_id = self.getBridgeUUID(bridge_name)
        if bridge_id is not None:
            ODL().deleteBridge(bridge_id, node_ip, ovsdb_port)
            
    '''
    
    '''
    def deleteIntegrationBridgeDropFlow(self):
        
        pass
    

            
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
        node_ip, ovsdb_port = self.getOvsdbNodeEndpoint(self.compute_node_address)
        self.node_ip = node_ip
        self.ovsdb_port = ovsdb_port
        integration_bridge_dpid = self.getBridgeDPID(INTEGRATION_BRIDGE, node_ip, ovsdb_port)
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
                            bridge_datapath_id = heat_orchestrator.getBridgeDatapath_id(interface.split("INGRESS_")[1], heat_orchestrator.node_ip, heat_orchestrator.ovsdb_port)
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

    






