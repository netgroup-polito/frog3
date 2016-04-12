'''
Created on Oct 1, 2014

@author: fabiomignini
'''
from __future__ import division
import logging
import json
import hashlib
import time, copy, uuid
from orchestrator_core.config import Configuration
from orchestrator_core.component_adapter.openstack_plus.rest import Nova, Heat, Glance, ODL, Neutron
from orchestrator_core.component_adapter.interfaces import OrchestratorInterface
from orchestrator_core.component_adapter.openstack_plus.resources import FlowRoute,ProfileGraph,VNF
from orchestrator_core.sql.graph import Graph
from orchestrator_core.sql.node import Node
from orchestrator_core.component_adapter.common.nffg_manager import NFFGManagerCA
from nffg_library.nffg import NF_FG, EndPoint, Port
from threading import Thread
from orchestrator_core.component_adapter.openstack_plus.ovsdb import OVSDB
from orchestrator_core.component_adapter.openstack_common.authentication import KeystoneAuthentication


DEBUG_MODE = Configuration().DEBUG_MODE
INTEGRATION_BRIDGE = Configuration().INTEGRATION_BRIDGE
EXIT_SWITCH = 'br-ex'
INGRESS_SWITCH = 'br-usr'
INGRESS_PORT = 'to-br-int'

class OpenStackPlusOrchestrator(OrchestratorInterface):
    '''
    Override class of the abstract class OrchestratorInterface
    '''  
    shadow = 'shadow'
    shall_not_be_installed = 'shall_not_be_installed'
    shall_not_be_installed_connection_end_point = 'shall_not_be_installed_connection_end_point'
    connection_end_point = 'connection_end_point'
    
    def __init__(self, graph_id, userdata):
        '''
        Initialized the Heat translation object from the user profile
        params:
            heatEndpoint:
                The list of the heatEndpoints of the Open Stack service (it takes the first one)
            novaEndpoint:
                The list of the novaEndpoints of the Open Stack service (it takes the first one)
        '''
        
        self.graph_id = graph_id
        self.userdata = userdata       
    
    @property
    def URI(self):
        return self._URI

    ######################################################################################################
    #########################    Orchestrator interface implementation        ############################
    ######################################################################################################
    
    def getStatus(self, node):
        self.getAuthTokenAndEndpoints(node)
        return self.openstackResourcesStatus(self.token.get_token())
    
    def deinstantiateProfile(self, nffg, node):
        '''
        Override method of the abstract class for deleting the user Stack
        '''
        nffg = Graph().get_nffg(self.graph_id, complete=True)
        
        self.getAuthTokenAndEndpoints(node)

        token_id = self.token.get_token()
    
        if DEBUG_MODE is not True:
            self.openstackResourcesDeletion(token_id, copy.deepcopy(nffg))
                        
        # Disconnect exit switch from graph
        self.deleteEndpoints(nffg) 
    
    def instantiateProfile(self, nffg, node):
        '''
        Override method of the abstract class for instantiating the user Stack
        '''
        self.getAuthTokenAndEndpoints(node)        
        try:            
            # Create a drop flow that match all packets, to avoid loop
            # when ODL doesn't set properly the tag vlan
            self.createIntegrationBridgeDropFlow()
            
            self.instantiateEndpoints(nffg)
            
            logging.debug("OpenStack CA :"+nffg.getJSON(extended=True))
            token_id = self.token.get_token()
            if DEBUG_MODE is not True:
                # Fill OpenStack model objects
                graph = ProfileGraph()
                for vnf in nffg.vnfs:
                    logging.debug("VNF id: "+vnf.id+" - VNF name: "+vnf.name)                    
                    graph.addEdge(VNF(vnf.id, vnf, Glance().get_image(vnf.template.uri, token_id)['id'],
                                       self.findFlavor(int(vnf.template.memory_size), int(vnf.template.root_file_system_size),
                                        int(vnf.template.ephemeral_file_system_size), int(vnf.template.cpu_requirements.socket[0]['coreNumbers']), token_id),
                                         vnf.availability_zone))
                
                for flow_rule in nffg.flow_rules:
                    graph.addArch(FlowRoute(flow_rule, nffg.end_points))  
                graph.associateNetworks()          
                self.openstackResourcesInstantiation(nffg, graph)

        except Exception as err:
            logging.exception(err)
            #self.deleteGraphResorces(nffg._id, self.token)
            #set_error(self.token.get_userID())  
            raise err
  
    def updateProfile(self, new_nf_fg, old_nf_fg, node):
        updated_nffg = old_nf_fg.diff(new_nf_fg)
        logging.debug("Diff: "+updated_nffg.getJSON(True))
        
        self.getAuthTokenAndEndpoints(node) 
        token_id = self.token.get_token()
        
        
        # Delete FlowRule
        for flow_rule in updated_nffg.flow_rules:
            if flow_rule.status == 'to_be_deleted':
                self.deleteFlowrule(token_id, flow_rule)
        
        # Delete VNFs
        for vnf in updated_nffg.vnfs[:]:
            if vnf.status == 'to_be_deleted':
                self.deleteVNF(token_id, vnf)
            else:
                # Delete ports
                for port in vnf.ports[:]:
                    if port.status == 'to_be_deleted':
                        self.deletePort(token_id, port)
        
        # Delete end-point and end-point resources
        for endpoint in updated_nffg.end_points[:]:
            if endpoint.status == 'to_be_deleted':
                self.deleteEndpoint(endpoint, updated_nffg)
                Graph().deleteEndpoint(graph_endpoint_id=endpoint.id, graph_id=self.graph_id)
                Graph().deleteEndpointResource(endpoint_id=endpoint.db_id)
            
        # Wait for resource deletion
        for vnf in updated_nffg.vnfs[:]:
            if vnf.status == 'to_be_deleted':
                self.waitForVNFInstantiation(token_id, updated_nffg, vnf)
            else:
                for port in vnf.ports[:]:
                    if port.status == 'to_be_deleted':
                        self.waitForPortInstantiation(token_id, vnf, port)
        for flow_rule in updated_nffg.flow_rules[:]:
            if flow_rule.status == 'to_be_deleted':
                updated_nffg.flow_rules.remove(flow_rule)
        
        logging.debug("Old resources completely deleted")
                    
        # Delete unused networks and subnets
        self.deleteUnusedNetworksAndSubnets(token_id)
        
        logging.debug("diff after: "+updated_nffg.getJSON(True))
        
        # Store, in initialize status, the new resources
        Graph().updateNFFG(nffg=updated_nffg, graph_id=self.graph_id)
        
        # Create a drop flow that match all packets, to avoid loop
        # when ODL doesn't set properly the tag vlan
        self.createIntegrationBridgeDropFlow()
        
        # Instantiate end-points
        self.instantiateEndpoints(updated_nffg)
        
        logging.debug("OpenStack CA :"+updated_nffg.getJSON(extended=True))
        if DEBUG_MODE is not True:
            graph = ProfileGraph(Graph().getHigherNumberOfNet(self.graph_id))
            
            for vnf in updated_nffg.vnfs:
                logging.debug("VNF id: "+vnf.id+" - VNF name: "+vnf.name)                    
                graph.addEdge(VNF(vnf.id, vnf, Glance().get_image(vnf.template.uri, token_id)['id'],
                                   self.findFlavor(int(vnf.template.memory_size), int(vnf.template.root_file_system_size),
                                    int(vnf.template.ephemeral_file_system_size), int(vnf.template.cpu_requirements.socket[0]['coreNumbers']), token_id),
                                     vnf.availability_zone, status = vnf.status))
            
            for flow_rule in updated_nffg.flow_rules:
                graph.addArch(FlowRoute(flow_rule, updated_nffg.end_points))  
            graph.associateNetworks()          
            self.openstackResourcesInstantiation(updated_nffg, graph)
    
    def instantiateEndpoints(self, nffg):
        for end_point in nffg.end_points[:]:
            if end_point.status == 'new' or end_point.status == 'to_be_updated' or end_point.status == None:
                self.instantiateEndPoint(nffg, end_point)
    
    def instantiateEndPoint(self, nffg, end_point):
        if end_point.prepare_connection_to_remote_endpoint_ids is not None:
            self.prepareEndPointConnection(nffg, end_point)
        if end_point.remote_endpoint_id is not None:
            self.connectEndPoints(nffg, end_point)
        
        if 'interface-out' in end_point.type:
            self.manageExitEndpoint(nffg, end_point)
        elif 'interface' in end_point.type:
            self.manageIngressEndpoint(end_point)
        elif 'gre' in end_point.type:
            raise NotImplementedError()
        elif  'internal' in end_point.type:
            # TODO: Set the flow-rule of the end-point as 'shall_not_be_installed'
            # TODO: Delete the following line
            self.deleteEndPointConnection(nffg, end_point)
        
    
    def deleteEndpoints(self, nffg):
        for endpoint in nffg.end_points[:]:
            self.deleteEndpoint(endpoint, nffg)
          
    def deleteEndpoint(self, endpoint, nffg):
        logging.debug("Deleting endpoint type: "+str(endpoint.type))
        if endpoint.type == 'interface-out':
            self.deleteExitEndpoint(nffg, endpoint)
        if endpoint.remote_endpoint_id is True:
            self.disconnectEndpoint(endpoint, nffg)
        nffg.end_points.remove(endpoint)
    
    def deleteFlowrule(self, token_id, flowrule):
        Neutron().deleteFlowrule(neutronEndpoint=self.neutronEndpoint, token=token_id,
                                  flowrule_id=flowrule.internal_id)
        Graph().deleteFlowRule(flow_rule_id=flowrule.db_id)
        
    def deletePort(self, token_id, port):
        Neutron().deletePort(neutronEndpoint=self.neutronEndpoint, token=token_id, 
                             port_id=port.internal_id)
        #Graph().deleteFlowspecFromPort(port_id=port.db_id)
        Graph().deletePort(port_id=port.db_id, graph_id=self.graph_id)
    
    def deleteVNF(self, token_id, vnf):
        Nova().deleteServer(self.novaEndpoint, token_id, vnf.internal_id)
        #Graph().deleteFlowRuleFromVNF(vnf_id=vnf.db_id)
        Graph().deleteVNF(graph_vnf_id=vnf.id, graph_id=self.graph_id)
        Graph().deletePort(port_id=None, graph_id=self.graph_id, vnf_id=vnf.db_id)
                
    def waitForPortInstantiation(self, token_id, vnf, port):
        while True:
            status = Neutron().getPortStatus(self.neutronEndpoint, token_id, port.internal_id)
            if status != 'ACTIVE':
                logging.debug("VNF "+str(vnf.internal_id)+" status "+status)
                vnf.ports.remove(port)
                break
            if status == 'ERROR':
                raise Exception('Port status ERROR - '+vnf.internal_id)
            logging.debug("Port "+str(vnf.internal_id)+" status "+status)
            
    def waitForVNFInstantiation(self, token_id, nffg, vnf):
        while True:
            status = Nova().getServerStatus(self.novaEndpoint, token_id, vnf.internal_id)
            if status != 'ACTIVE':
                logging.debug("VNF "+str(vnf.internal_id)+" status "+status)
                nffg.vnfs.remove(vnf)
                break
            if status == 'ERROR':
                raise Exception('VNF status ERROR - '+vnf.internal_id)
            logging.debug("VNF "+str(vnf.internal_id)+" status "+status)
        
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
        networks = Graph().getNetworks(self.graph_id)
        for network in networks:
            resources_status['networks'][network.id] = Neutron().getNetworkStatus(self.neutronEndpoint, token_id, network.id)
        resources_status['subnets'] = {}
        subnets = Graph().getSubnets(self.graph_id)
        for subnet in subnets:
            resources_status['subnets'][subnet.id] = Neutron().getSubNetStatus(self.neutronEndpoint, token_id, subnet.id)
        resources_status['ports'] = {}
        ports = Graph().getPorts(self.graph_id)
        for port in ports:
            if port.type == 'openstack':
                resources_status['ports'][port.id] = Neutron().getPortStatus(self.neutronEndpoint, token_id, port.internal_id)
        resources_status['vnfs'] = {}
        vnfs = Graph().getVNFs(self.graph_id)
        for vnf in vnfs:
            resources_status['vnfs'][vnf.id] = Nova().getServerStatus(self.novaEndpoint, token_id, vnf.internal_id)
        resources_status['flowrules'] = {}
        flowrules = Graph().getFlowRules(self.graph_id)
        
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
            Graph().deleteNetwork(unused_network_ref.id)
                
    def openstackResourcesDeletion(self, token_id, nffg):
        subnets = Graph().getSubnets(self.graph_id)
        networks = Graph().getNetworks(self.graph_id)
        flowrules = Graph().getFlowRules(self.graph_id)
        for flowrule in flowrules:
            Neutron().deleteFlowrule(self.neutronEndpoint, token_id, flowrule.internal_id)
        vnfs = Graph().getVNFs(self.graph_id)
        for vnf in vnfs:
            Nova().deleteServer(self.novaEndpoint, token_id, vnf.internal_id)   
        for vnf in nffg.vnfs:
            self.waitForVNFInstantiation(token_id, nffg, vnf)
        ports = Graph().getPorts(self.graph_id)
        for port in ports:
            Neutron().deletePort(self.neutronEndpoint, token_id, port.internal_id)
        for vnf in nffg.vnfs:
            for port in vnf.ports:
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
                    Graph().setPortInternalID(graph_id=self.graph_id, vnf_id=nffg.getVNF(vnf.id).db_id, port_graph_id=port.name, port_internal_id=port.port_id, port_status=port.status, port_type='openstack')
                    Graph().setOSNetwork(os_network_id=port.net.network_id, graph_port_id=port.name, vnf_id=nffg.getVNF(vnf.id).db_id,
                                        internal_id=port.port_id, graph_id=self.graph_id)
            logging.debug("VNF: "+json.dumps(vnf.getResourceJSON())+" Status: "+str(vnf.status))
            if vnf.status == 'new':
                vnf.vnf_id = Nova().createServer(self.novaEndpoint, self.token.get_token(), vnf.getResourceJSON())['server']['id']
                Graph().setVNFInternalID(graph_id=self.graph_id, graph_vnf_id=vnf.id, internal_id=vnf.vnf_id, status=vnf.status)
        
        thread = Thread(target = self.setFlows, args = (graph, nffg ))
        thread.start()
        
    def setFlows(self, graph, nffg):
        '''
        Thread responsible of the flow-rule instantiation.
        '''
        try:
            while True:
                time.sleep(1)
                complete = True
                resources_status = {}
                resources_status['vnfs'] = {}
                vnfs = Graph().getVNFs(graph_id=self.graph_id)
                for vnf in vnfs:
                    resources_status['vnfs'][vnf.internal_id] = Nova().getServerStatus(self.novaEndpoint, self.token.get_token(), vnf.internal_id)
                for value in resources_status['vnfs'].itervalues():
                    if value != 'ACTIVE':
                        complete = False
                if complete is True:
                    break
            for flow in graph.archs:
                logging.debug("Flowrule: "+str(self.graph_id)+":"+flow.flow_rule.id+" "+json.dumps(flow.flow_rule.getDict(extended = True)))
                flowroute = flow.getResourcesJSON(self.token.get_tenantID(), graph.edges)
                #  Don't instantiate the flow-rules of type 'shall_not_be_installed' or 'shadow'
                if flow.flow_rule.type != self.shadow and flow.flow_rule.type != self.shall_not_be_installed and flow.flow_rule.type != self.shall_not_be_installed_connection_end_point:
                    if flow.flow_rule.status == 'new' or flow.flow_rule.status is None:
                        logging.debug("Flowrule for Neutron: "+str(self.graph_id)+":"+flow.flow_rule.id+" "+json.dumps(flowroute)+" Status: "+str(flow.flow_rule.status))
                        flowrule_id = Neutron().createFlowrule(self.neutronEndpoint, self.token.get_token(), flowroute)['flowrule']['id']
                        Graph().setFlowRuleInternalID(graph_id=self.graph_id, graph_flow_rule_id=flow.flow_rule.id, internal_id=flowrule_id, status=flow.flow_rule.status)
            logging.debug("Instantiation of graph "+nffg.id+" completed")
        except Exception as ex:
            logging.exception(ex)
            raise ex
            

    
        
    ######################################################################################################
    ###############################       Manage graphs connection        ################################
    ######################################################################################################
    
    def prepareEndPointConnection(self, nffg, endpoint):
        for prepare_connection_to_remote_endpoint_id in endpoint.prepare_connection_to_remote_endpoint_ids:
            # Check if the prepare_connection_to_remote_endpoint_id correspond to an already connected remote endpoint or not
            if Graph().checkConnection(endpoint_id=prepare_connection_to_remote_endpoint_id, endpoint_type='external'):
                # Connection already managed
                continue
            
            # Crate new end-point and move all the information (all except ID) from original end-point to new end-point
            new_end_point_id  = uuid.uuid4().hex
            new_end_point = EndPoint(_id=new_end_point_id, name=endpoint.name, _type=endpoint.type+self.connection_end_point, remote_endpoint_id=endpoint.remote_endpoint_id,
                                      node=endpoint.node, switch_id=endpoint.switch_id, interface=endpoint.interface, remote_ip=endpoint.remote_ip,
                                      local_ip=endpoint.local_ip, ttl=endpoint.ttl, vlan_id=endpoint.vlan_id,
                                       interface_internal_id=endpoint.interface_internal_id,
                                       prepare_connection_to_remote_endpoint_id=prepare_connection_to_remote_endpoint_id)
            nffg.addEndPoint(new_end_point)
            
            # Save the end-point on DB
            new_end_point.db_id = Graph().addEndPoint(graph_endpoint_id=new_end_point.id, graph_id=self.graph_id, name=new_end_point.name, 
                                _type=new_end_point.type, location=new_end_point.node)
            if new_end_point.type == 'interface' or new_end_point.type == 'interface-out':
                # Create Port
                port_id = Graph().addPort(graph_port_id=new_end_point.interface, graph_id=self.graph_id, name=new_end_point.interface,
                                 virtual_switch=new_end_point.switch_id, location=new_end_point.node)
                Graph().addEndpointResource(endpoint_id=new_end_point.db_id, endpoint_type=new_end_point.type,
                                             port_id=port_id)
            elif new_end_point.type == 'gre':
                raise NotImplementedError()
            elif new_end_point.type == 'vlan':
                raise NotImplementedError()
            
            # Update graph_connection table on BD with the new end-point ID
            Graph().addGraphConnection(endpoint_id_2=new_end_point.db_id, endpoint_id_1=prepare_connection_to_remote_endpoint_id, endpoint_id_2_type='internal', endpoint_id_1_type='external')
            
            # Check if there are multiple connections for this end-point, if there are multiple connection
            #  create an end-point switch. Or, if an end-point switch already exists, create a new port
            #  in it, connected to the just created end-point
            remote_connections_ref = Graph().getGraphConnections(self.graph_id, endpoint.name)
            manager = NFFGManagerCA(nffg)
            if len(remote_connections_ref) == 1:
                # Add the end-point switch, connect it to the graph VNFs and connect it to the new end-point
                end_point_switch = manager.createEndPointSwitch(old_end_point=endpoint, availability_zone=self.availability_zone)
                end_point_switch.status = 'new'
                end_point_switch.db_id = Graph().addVNF(graph_vnf_id=end_point_switch.id, graph_id=self.graph_id, name=end_point_switch.name,
                                vnf_template_location=end_point_switch.vnf_template_location, status=end_point_switch.status)
                switch_flowrules = manager.connectEndPointSwitchToGraph(end_point_switch=end_point_switch, old_end_point=endpoint)
                nffg.flow_rules += switch_flowrules
                
                new_flow_rules = manager.connectNewEndPointToEndPointSwitch(old_end_point=endpoint, new_end_point=new_end_point)
                for port in end_point_switch.ports:
                    port.status = 'new'
                    port.db_id = Graph().addPort(graph_port_id=port.id, graph_id=self.graph_id, name=port.name, vnf_id=end_point_switch.db_id,
                                    _type='openstack', status=port.status)
                for switch_flowrule in switch_flowrules:
                    switch_flowrule.type = self.connection_end_point
                    switch_flowrule.db_id = Graph().addFlowRule(graph_id=self.graph_id, flow_rule=switch_flowrule, nffg=nffg)
            else:
                # Connect the new end-point to the end-point switch
                new_flow_rules = manager.connectNewEndPointToEndPointSwitch(old_end_point=endpoint, new_end_point=new_end_point)
            nffg.flow_rules += new_flow_rules
            for new_flow_rule in new_flow_rules:
                new_flow_rule.type = self.shall_not_be_installed_connection_end_point
                new_flow_rule.db_id = Graph().addFlowRule(graph_id=self.graph_id, flow_rule=new_flow_rule, nffg=nffg)
            
            
            # Set the original end-point as a 'shadow end-point' (The shadow end-point will not be drawn on the GUI)
            endpoint.type = self.shadow
            Graph().updateEndpointType(graph_endpoint_id=endpoint.id, graph_id=self.graph_id, endpoint_type=endpoint.type)
            # Delete the end-point resources associated to the original end-point
            Graph().deleteEndpointResource(endpoint.db_id)
             
            # Mark the flow-rules from or to the original end-point as 'shadow flow-rules' (The shadow flow-rules 
            #  will not be instantiated and drawn on the GUI)
            # The Shadow characteristic is different from an internal end-point, an internal end-point will have un-instantiated
            #  flow-rules but it will be visible with its flow-rule from the GUI
            flow_rules = manager.setFlowRuleOfEndPointType(end_point_id=endpoint.id, _type=self.shadow)
            for flow_rule in flow_rules:
                Graph().updateFlowRuleType(flow_rule_id=flow_rule.db_id, _type=flow_rule.type)
                
        # Delete old end-point connections
        complete_nffg = Graph().get_nffg(graph_id=self.graph_id, complete=True)
        same_end_points = complete_nffg.getEndPointsFromName(endpoint.name)
        for same_end_point in same_end_points:
            connections = Graph().checkConnection(same_end_point.db_id, endpoint_type='internal')
            if connections:
                if connections[0].endpoint_id_1_type == 'external':
                    external_endpoint = connections[0].endpoint_id_1
                elif connections[0].endpoint_id_2_type == 'external':
                    external_endpoint = connections[0].endpoint_id_2
                if external_endpoint not in endpoint.prepare_connection_to_remote_endpoint_ids:
                    self.disconnectEndpoint(complete_nffg, endpoint, same_end_point)
    
    def connectEndPoints(self, nffg, end_point):
        '''
        Characterize the endpoints that should be connected to another graph
        (We are here only if the two graph that have to be connected are in the same node.)
        '''
        # TODO: Getting the real remote end-point
        remote_endpoint = self.getRemoteEndpoint(end_point.remote_endpoint_id.split(':')[0],
                                                  end_point.remote_endpoint_id.split(':')[1],
                                                  self.graph_id, end_point.id)
        manager = NFFGManagerCA(nffg)
        if remote_endpoint.type == 'internalconnection_end_point':
            remote_nffg = Graph().get_nffg(end_point.remote_endpoint_id.split(':')[0], complete=True)
            manager.connectToRemoteEndPoint(ovsdb=self.ovsdb, graph_id=self.graph_id, end_point=end_point, remote_nffg=remote_nffg,
                                             remote_end_point_id=remote_endpoint.graph_endpoint_id, new_flow_rule_type=self.connection_end_point,
                                              end_point_and_flow_rule_type=self.shall_not_be_installed) 
        else:
            raise NotImplementedError()
    
    def disconnectEndpoint(self, nffg, original_endpoint, endpoint_to_delete):
        remote_connections_ref = Graph().getGraphConnections(self.graph_id, original_endpoint.name)
        manager = NFFGManagerCA(nffg)
        token_id = self.token.get_token()
        if len(remote_connections_ref) == 1:
            # Delete end-point switch and its flows
            end_point_switch, end_point_switch_flow_rules = manager.deleteEndPointSwitch(end_point_id=original_endpoint.id)
            
            for end_point_switch_flow_rule in end_point_switch_flow_rules:
                nffg.flow_rules.remove(end_point_switch_flow_rule)
                self.deleteFlowrule(token_id, end_point_switch_flow_rule)
                Graph().deleteFlowRule(end_point_switch_flow_rule.db_id)
            networks = []
            subnets =[]
            for port in end_point_switch.ports:
                network = Graph().getPortNetwork(port.db_id)
                networks.append(network)
                subnets.append(Graph().getSubnet(network.id))
            self.deleteVNF(token_id, end_point_switch)
            self.waitForVNFInstantiation(token_id, nffg, end_point_switch)
            for network, subnet in zip(networks, subnets):
                Neutron().deleteSubNet(self.neutronEndpoint, token_id, subnet.id)
                Neutron().deleteNetwork(self.neutronEndpoint, token_id, network.id)
                Graph().deleteNetwork(network.id)
                Graph().deleteSubnet(network.id)
            Graph().deletePort(None, self.graph_id, vnf_id=end_point_switch.id)
            Graph().deleteVNF(graph_vnf_id=end_point_switch.id, graph_id=self.graph_id)
            
            # Delete end-point
            nffg.end_points.remove(endpoint_to_delete)
            
            # Update original end-point type
            original_endpoint.type = endpoint_to_delete.type.split('connection_end_point')[0]
            Graph().updateEndpointType(original_endpoint.id, self.graph_id, original_endpoint.type)
        else:
            # Delete end-point switch port
            endpoint_port = manager.deleteEndPointPort(endpoint_to_delete.id)
            port = self.deletePort(token_id, endpoint_port)
            network = Graph().getPortNetwork(port.db_id)
            subnet = Graph().getSubnet(network.id)
            Neutron().deleteSubNet(self.neutronEndpoint, token_id, subnet.id)
            Neutron().deleteNetwork(self.neutronEndpoint, token_id, network.id)
            Graph().deleteNetwork(network.id)
            Graph().deleteSubnet(network.id)
            Graph().deletePort(port.db_id, self.graph_id)
            
            # Delete end-point flows
            removed_flowrules = manager.deleteEndPointFlows(endpoint_to_delete.id)
            # Delete flow-rule from DB
            for removed_flowrule in removed_flowrules:                        
                nffg.flow_rules.remove(removed_flowrule)
                self.deleteFlowrule(token_id, removed_flowrule)
                Graph().deleteFlowRule(removed_flowrule.db_id)
            # Delete end-point
            nffg.endpoints.remove(endpoint_to_delete)
            
        # Delete end-point from DB
        Graph().deleteEndpoint(graph_endpoint_id=endpoint_to_delete.id, graph_id=self.graph_id)
        # Delete the connection on the DB
        Graph().deleteGraphConnection(endpoint_to_delete.db_id)
    
    def deleteEndPointConnection(self, nffg, end_point):
        '''
        Delete connection to endpoints those are not connected to any interface or other graph
        '''        
        logging.debug("Setting flow type to shall_not_be_installed for endoints not characterized: "+str(end_point.name))           
        logging.debug("Setting flow type to shall_not_be_installed for not connected end-point: "+end_point.name+" in graph: "+nffg.id+"("+nffg.name+")")
        manager = NFFGManagerCA(nffg)
        flow_rules = manager.setFlowRuleOfEndPointType(end_point_id=end_point.id, _type=self.shall_not_be_installed)
        
        # Update end-point type in DB
        Graph().updateEndpointType(graph_endpoint_id=end_point.id, graph_id=end_point.db_id, endpoint_type=end_point.type)

        # Update flow-rules type in DB
        for flow_rule in flow_rules:
            Graph().updateFlowRuleType(flow_rule_id=flow_rule.db_id, _type=flow_rule.type)
        
        # These flows for now are useless, because we set a base drop flow in br-int.
        # Anyway if we would use them, they must be saved in the db, couse if we install a flow 
        # with the same matches and priority the ODL mechanism driver raise an exception that
        # cause the lost of samo following flow (Known bug).
        # Add drop flows to avoid that that packets match normal flows
        '''
        for connected_port in ports:
            connected_port.setDropFlow()
        '''
        pass

    def getRemoteEndpoint(self, remote_graph_id, remote_end_point_id, graph_id, end_point_id):
        conections_ref = Graph().checkConnection(str(graph_id)+':'+end_point_id, 'external')
        assert (len(conections_ref) == 1)
        assert (conections_ref[0].endpoint_id_2_type == 'internal')
        return Graph()._getEndpoint(conections_ref[0].endpoint_id_2)
            
    
    ######################################################################################################
    ######################   Authentication towards infrastructure controllers        ####################
    ######################################################################################################
    
    def getAuthTokenAndEndpoints(self, node):
        self.node_endpoint = Node().getNode(node.openstack_controller).domain_id
        self.compute_node_address = node.domain_id
        self.availability_zone = node.availability_zone
                
        self.keystoneEndpoint = 'http://' + self.node_endpoint + ':35357'
        self.token = KeystoneAuthentication(self.keystoneEndpoint, self.userdata.tenant, self.userdata.username, self.userdata.password)        
        self.novaEndpoint = self.token.get_endpoints('compute')[0]['publicURL']
        self.glanceEndpoint = self.token.get_endpoints('image')[0]['publicURL']
        self.neutronEndpoint = self.token.get_endpoints('network')[0]['publicURL']
        
        odl = Node().getOpenflowController(node.openflow_controller)
        self.odlendpoint = odl.endpoint
        self.odlusername = odl.username
        self.odlpassword = odl.password
        self.ovsdb = OVSDB(self.odlendpoint, self.odlusername, self.odlpassword, self.compute_node_address)
    
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
        Disabled because the orchestrator_core dont't know the phisical ports of node 
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
    
    def manageIngressEndpoint(self, ingress_end_point):    
        bridge_datapath_id = self.ovsdb.getBridgeDatapath_id(ingress_end_point.interface)
        if bridge_datapath_id is None:
            raise Exception("Bridge datapath id doesn't found for this interface: "+str(ingress_end_point.interface))
        ingress_end_point.interface_internal_id = "INGRESS_"+bridge_datapath_id+":"+ingress_end_point.interface
        self.createVirtualIngressNetwork(self.compute_node_address)
        # TODO: set port internal ID in db
        
    def manageExitEndpoint(self, nf_fg, exit_end_point):
        '''
        Characterize exit endpoint with virtual interface that bring the traffic
        to a switch that is used to forward packets on the right graph
        '''
        logging.debug("Managing single exit endpoint : "+exit_end_point.id)
        graph_exit_port = self.createVirtualExitNetwork(nf_fg, exit_end_point, self.compute_node_address)
        # TODO: set port internal ID in db   
        bridge_datapath_id = self.ovsdb.getBridgeDatapath_id(graph_exit_port)
        if bridge_datapath_id is None:
            raise Exception("Bridge datapath id doesn't found for this interface: "+str(graph_exit_port))
        exit_end_point.interface_internal_id = "INGRESS_"+bridge_datapath_id+":"+graph_exit_port

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