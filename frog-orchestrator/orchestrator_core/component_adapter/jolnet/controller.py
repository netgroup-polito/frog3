'''
Created on 13/apr/2015
@author: vida
'''

import logging
import json, copy

from orchestrator_core.config import Configuration
from orchestrator_core.exception import StackError, GraphError
from orchestrator_core.sql.graph import Graph
from orchestrator_core.sql.node import Node

from orchestrator_core.component_adapter.interfaces import OrchestratorInterface
from nffg_library.nffg import FlowRule
from orchestrator_core.component_adapter.jolnet.rest import ODL, Glance, Nova, Neutron
from orchestrator_core.component_adapter.jolnet.resources import Action, Match, Flow, ProfileGraph, VNF, Endpoint
from orchestrator_core.component_adapter.openstack_common.authentication import KeystoneAuthentication
from copy import deepcopy

DEBUG_MODE = Configuration().DEBUG_MODE
JOLNET_NETWORKS = Configuration().JOLNET_NETWORKS

class JolnetAdapter(OrchestratorInterface):
    
    def __init__(self, graph_id, userdata):
        '''
        Initialize the Jolnet component adapter
        Args:
            session_id:
                identifier for the current user session
            userdata:
                credentials to get Keystone token for the user
        '''
        self.graph_id = graph_id
        self.userdata = userdata
    
    @property
    def URI(self):
        return self.compute_node_address
    
    '''
    ######################################################################################################
    #########################    Orchestrator interface implementation        ############################
    ######################################################################################################
    '''
    def getStatus(self, node):
        self.getAuthTokenAndEndpoints(node)
        return self.openstackResourcesStatus(self.token.get_token())
    
    def instantiateProfile(self, nf_fg, node):
        '''
        Override method of the abstract class for instantiating the user graph
        '''
        self.getAuthTokenAndEndpoints(node)
        
        logging.debug("Forwarding graph: " + nf_fg.getJSON(True))
        try:            
            #Read the nf_fg JSON structure and map it into the proper objects and db entries
            profile_graph = self.buildProfileGraph(nf_fg)
            self.openstackResourcesInstantiation(profile_graph, nf_fg)
            logging.debug("Graph " + profile_graph.id + " correctly instantiated!")
            
        except Exception as err:
            logging.error(err.message)
            logging.exception(err) 
            raise err
    
    def updateProfile(self, new_nf_fg, old_nf_fg, node):
        '''
        Override method of the abstract class for updating the user graph
        '''        
        self.getAuthTokenAndEndpoints(node)
        
        try:
            updated_nffg = old_nf_fg.diff(new_nf_fg)
            logging.debug("Diff: "+updated_nffg.getJSON(True))
            
            remote_update = False
            #Check if it is a remote update of endpoints triggered by the orchestrator
            for endpoint in updated_nffg.end_points:
                if endpoint.status == 'to_be_updated':
                    remote_update = True
                    #Check if we have to add graph connections
                    for prepare_connection_to_remote_endpoint_id in endpoint.prepare_connection_to_remote_endpoint_ids:
                        if Graph().checkConnection(endpoint_id=prepare_connection_to_remote_endpoint_id, endpoint_type='external'):
                            continue
                        Graph().addGraphConnection(endpoint_id_2=endpoint.db_id, endpoint_id_1=prepare_connection_to_remote_endpoint_id, endpoint_id_2_type='internal', endpoint_id_1_type='external')
                    #Check if we have to delete graph connections
                    allconnectionstoendpoint = Graph().checkConnection(endpoint_id=endpoint.db_id, endpoint_type='internal')
                    for graph_connection in allconnectionstoendpoint:
                        if graph_connection.endpoint_id_1 not in endpoint.prepare_connection_to_remote_endpoint_ids:
                            Graph().deleteGraphConnection(endpoint_id_1=graph_connection.endpoint_id_1, endpoint_id_2=None)
                            
            if remote_update is False:
                self.openstackResourcesControlledDeletion(updated_nffg, self.token.get_token())
                Graph().updateNFFG(updated_nffg, self.graph_id)
                profile_graph = self.buildProfileGraph(updated_nffg)
                self.openstackResourcesInstantiation(profile_graph, updated_nffg)
                logging.debug("Graph " + old_nf_fg.id + " correctly updated!")
            
        except Exception as err:
            logging.error(err.message)
            logging.exception(err) 
            raise err
        
    def deinstantiateProfile(self, nf_fg, node):
        '''
        Override method of the abstract class for deleting the user graph
        '''
        self.getAuthTokenAndEndpoints(node)
        
        logging.debug("Forwarding graph: " + nf_fg.getJSON())
        
        try:
            self.openstackResourcesDeletion()
            logging.debug("Graph " + nf_fg.id + " correctly deleted!") 
        except Exception as err:
            logging.error(err.message)
            logging.exception(err) 
            raise err
 
    '''
    ######################################################################################################
    ######################   Authentication towards infrastructure controllers        ####################
    ######################################################################################################
    ''' 
    
    def getAuthTokenAndEndpoints(self, node):
        self.node_endpoint = Node().getNode(node.openstack_controller).domain_id
        self.compute_node_address = node.domain_id
        
        self.keystoneEndpoint = 'http://' + self.node_endpoint + ':35357'
        self.token = KeystoneAuthentication(self.keystoneEndpoint, self.userdata.tenant, self.userdata.username, self.userdata.password)
        self.novaEndpoint = self.token.get_endpoints('compute')[0]['publicURL']
        self.glanceEndpoint = self.token.get_endpoints('image')[0]['publicURL']
        self.neutronEndpoint = self.token.get_endpoints('network')[0]['publicURL']
        
        #logging.debug(self.token.get_token())
        
        odl = Node().getOpenflowController(node.openflow_controller)
        self.odlendpoint = odl.endpoint
        self.odlusername = odl.username
        self.odlpassword = odl.password
        self.odlversion = odl.version
    
    '''
    ######################################################################################################
    #############################    Resources preparation phase        ##################################
    ######################################################################################################
    '''      
    def buildProfileGraph(self, nf_fg):
        profile_graph = ProfileGraph()
        profile_graph.setId(nf_fg.id)
        
        #Remove from the pool of available openstack networks vlans used in endpoints of type vlan
        for endpoint in nf_fg.end_points:
            if endpoint.type == 'vlan':
                if endpoint.vlan_id.isdigit() is False:
                    name = endpoint.vlan_id
                else:                                
                    name = "exp" + str(endpoint.vlan_id)
                if name in JOLNET_NETWORKS:              
                    JOLNET_NETWORKS.remove(name)
        
        for vnf in nf_fg.vnfs:
            nf = self.buildVNF(vnf)
            profile_graph.addVNF(nf)
        
        for vnf in profile_graph.functions.values():
            self.setVNFNetwork(nf_fg, vnf, profile_graph)

        for endpoint in nf_fg.end_points:
            ep = self.buildEndpoint(endpoint)
            profile_graph.addEndpoint(ep)
        
        for flowrule in nf_fg.flow_rules:
            if flowrule.status is None:
                flowrule.status = 'new'
            profile_graph.addFlowrule(flowrule)
                  
        return profile_graph                        
    
    def buildVNF(self, vnf):
        #Get the necessary info (glance URI and Nova flavor) and create a VNF object
        template = vnf.template
        cpuRequirements = template.cpu_requirements.socket
        if DEBUG_MODE is True:
            logging.debug(template.uri)
        image = Glance().getImage(template.uri, self.token.get_token())
        flavor = self.findFlavor(int(template.memory_size), int(template.root_file_system_size),
            int(template.ephemeral_file_system_size), int(cpuRequirements[0]['coreNumbers']), self.token.get_token())
        if vnf.status is None:
            status = "new"
        else:
            status = vnf.status
        #TODO: add image location to the database
        return VNF(vnf.id, vnf, image, flavor, vnf.availability_zone, status)
    
    def setVNFNetwork(self, nf_fg, nf, profile_graph):
        for port in nf.ports.values():
            if port.net is None and port.status != 'already_deployed':  
                for flowrule in nf_fg.getFlowRulesSendingTrafficFromPort(nf.id, port.id):
                    logging.debug(flowrule.getDict(True))
                    if flowrule.match is not None:
                        if flowrule.match.vlan_id is not None:
                            #vlan_id already specified in nffg
                            for action in flowrule.actions:
                                if action.output is not None:
                                    net_vlan = flowrule.match.vlan_id
                                    #Check if is a numeric vlan (e.g 288) or a management one 
                                    if net_vlan.isdigit() is False:
                                        name = net_vlan
                                    else:                                
                                        name = "exp" + str(net_vlan)
                                    net_id = self.getNetworkIdfromName(name)
                                    port.setNetwork(net_id, net_vlan)                        
                                    networks = Graph().getAllNetworks()
                                    found = False
                                    for net in networks:
                                        if net.id == net_id:
                                            found = True
                                            break
                                    if found is False:
                                        Graph().addOSNetwork(net_id, name, 'complete', net_vlan)
                                    if name in JOLNET_NETWORKS:              
                                        JOLNET_NETWORKS.remove(name)     
                                    break   
                        else:
                            #match.vlan_id None
                            #check if vlan_id is constrained by a local or a remote endpoint
                            for action in flowrule.actions:
                                if action.output is not None:
                                    if action.output.split(":")[0] == 'endpoint':
                                        endp = nf_fg.getEndPoint(action.output.split(":")[1])
                                        if endp.type =='vlan' or endp.remote_endpoint_id is not None:
                                            if endp.type =='vlan':
                                                net_vlan = endp.vlan_id
                                            elif endp.remote_endpoint_id is not None:
                                                remote_endp = Graph().get_nffg(endp.remote_endpoint_id.split(':')[0]).getEndPoint(endp.remote_endpoint_id.split(':')[1])
                                                net_vlan = remote_endp.vlan_id
                                            if net_vlan.isdigit() is False:
                                                name = net_vlan
                                            else:                                
                                                name = "exp" + str(net_vlan)
                                            net_id = self.getNetworkIdfromName(name)
                                            port.setNetwork(net_id, net_vlan)                        
                                            networks = Graph().getAllNetworks()
                                            found = False
                                            for net in networks:
                                                if net.id == net_id:
                                                    found = True
                                                    break
                                            if found is False:
                                                Graph().addOSNetwork(net_id, name, 'complete', net_vlan)
                                            if name in JOLNET_NETWORKS:              
                                                JOLNET_NETWORKS.remove(name)                                                   
                                            break   
                            #Choose a network arbitrarily (no constraints)    
                            if port.net is None:
                                name, net_id = self.getUnusedNetwork()
                                if name is None:
                                    raise StackError("No available network found")
                                port.net = net_id
                                #Ports sending traffic to this port need to be in the same network
                                for flowrule in nf_fg.getFlowRulesSendingTrafficToPort(nf.id, port.id):
                                    if flowrule.match is not None and flowrule.match.port_in is not None and flowrule.match.port_in.split(':')[0] == 'vnf':
                                        tmp = flowrule.match.port_in.split(':', 2)
                                        vnf_id = tmp[1]
                                        port1_id = tmp[2]
                                        port1 = profile_graph.functions[vnf_id].ports[port1_id]
                                        port1.net = net_id                                    
                                networks = Graph().getAllNetworks()
                                found = False
                                for net in networks:
                                    if net.id == net_id:
                                        found = True
                                        break
                                if found is False:
                                    Graph().addOSNetwork(net_id, name, 'complete', None) 
              
                
    def buildEndpoint(self, endpoint):
        if endpoint.status is None:
            status = "new"
        else:
            status = endpoint.status
        if endpoint.remote_endpoint_id is not None:
            delimiter = endpoint.remote_endpoint_id.find(":")
            remote_graph = endpoint.remote_endpoint_id[:delimiter]
            remote_id = endpoint.remote_endpoint_id[delimiter+1:] 
            return Endpoint(endpoint.id, endpoint.name, endpoint.type, endpoint.vlan_id, endpoint.switch_id, endpoint.interface, status, remote_graph, remote_id)
        else:
            return Endpoint(endpoint.id, endpoint.name, endpoint.type, endpoint.vlan_id, endpoint.switch_id, endpoint.interface, status)
    
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
                for port in vnf.listPort:
                    if port.status == "new":
                        self.addPorttoVNF(port, vnf, nf_fg)
        
                   
        #Create flow on the SDN network for graphs interconnection
        for endpoint in profile_graph.endpoints.values():
            if endpoint.status == "new":
                if endpoint.remote_id is not None:
                    #Check if the remote graph exists and the requested endpoint is available
                    graph = Graph().get_nffg(endpoint.remote_graph)
                    remote_endpoint = None
                    remote_endpoint = graph.getEndPoint(endpoint.remote_id)
                    
                    if remote_endpoint is not None:
                        vlan = remote_endpoint.vlan_id
                        switch1 = endpoint.switch_id
                        port1 = endpoint.interface                                       
                                                                  
                        switch1_id = Node().getNodeFromDomainID(switch1).id
                        switch2_id = Graph().getNodeID(endpoint.remote_graph)
                        switch2 = Node().getNodeDomainID(switch2_id)     
                        port2 = remote_endpoint.interface
                        
                        #TODO: add the port on the endpoint switch
                        local_endpoint_db_id = nf_fg.getEndPoint(endpoint.id).db_id
                        self.linkZones(self.graph_id, switch1, port1, switch1_id, switch2, port2, switch2_id, vlan, local_endpoint_db_id)
                        if not Graph().checkConnection(endpoint_id=str(self.graph_id)+":"+endpoint.id, endpoint_type='external'):
                            Graph().addGraphConnection(endpoint_id_1=str(self.graph_id)+":"+endpoint.id, endpoint_id_2=remote_endpoint.db_id, endpoint_id_2_type='internal', endpoint_id_1_type='external')

                    else:
                        logging.error("Remote graph " + endpoint.remote_graph + " has not a " + endpoint.id + " endpoint available!")
                
                Graph().setEndpointLocation(self.graph_id, endpoint.id, endpoint.interface)
          
        
        for flowrule in profile_graph.flowrules.values():
            if flowrule.status =='new':
                #TODO: check priority
                if flowrule.match is not None:
                    if flowrule.match.port_in is not None:
                        tmp1 = flowrule.match.port_in.split(':')
                        port1_type = tmp1[0]
                        port1_id = tmp1[1]
                        if port1_type == 'vnf':
                            if len(flowrule.actions) > 1 or flowrule.actions[0].output is None:
                                raise GraphError("Multiple actions or action different from output are not supported between vnfs")
                        elif port1_type == 'endpoint':
                            endpoint_to_vnf = False
                            for action in flowrule.actions:
                                if action.output is not None and action.output.split(':')[0] == "vnf":
                                    endpoint_to_vnf= True
                                    break
                            if endpoint_to_vnf is True:
                                if len(flowrule.actions) > 1:
                                    raise GraphError("Multiple actions are not supported between an endpoint and a vnf")
                                else:
                                    continue
                            endp1 = profile_graph.endpoints[port1_id]
                            if endp1.type == 'interface':        
                                self.processFlowrule(endp1, flowrule, profile_graph)  
                                  
            
    def openstackResourcesDeletion(self):       
        #Delete every resource one by one
        flows = Graph().getFlowRules(self.graph_id)
        for flow in flows:
            if flow.type == "external" and flow.status == "complete":
                switch_id = Node().getNodeDomainID(flow.node_id)
                ODL(self.odlversion).deleteFlow(self.odlendpoint, self.odlusername, self.odlpassword, switch_id, flow.graph_flow_rule_id)
        
        vnfs = Graph().getVNFs(self.graph_id)
        for vnf in vnfs:
            Nova().deleteServer(self.novaEndpoint, self.token.get_token(), vnf.internal_id)        
        #TODO: Delete also networks and subnets if previously created
        
    def openstackResourcesControlledDeletion(self, updated_nffg, token_id):
        # Delete VNFs
        for vnf in updated_nffg.vnfs[:]:
            if vnf.status == 'to_be_deleted':
                self.deleteServer(vnf, updated_nffg)              
            else:
                # Delete ports
                for port in vnf.ports[:]:
                    self.deletePort(vnf, port, updated_nffg)
        
        for endpoint in updated_nffg.end_points[:]:
            if endpoint.status == 'to_be_deleted':                      
                flows = Graph().getEndpointResource(endpoint.db_id, "flowrule")
                for flow in flows:
                    if flow.type == "external" and flow.status == "complete":
                        switch_id = Node().getNodeDomainID(flow.node_id)
                        ODL(self.odlversion).deleteFlow(self.odlendpoint, self.odlusername, self.odlpassword, switch_id, flow.id)
                Graph().deleteEndpoint(endpoint.id, self.graph_id)
                Graph().deleteEndpointResourceAndResources(endpoint.db_id)
                if endpoint.remote_endpoint_id is not None: 
                    Graph().deleteGraphConnection(endpoint_id_1=str(self.graph_id)+":"+endpoint.id, endpoint_id_2=None) 
                
                flowrule_out = updated_nffg.getFlowRulesSendingTrafficFromEndPoint(endpoint.id)
                flowrule_in = updated_nffg.getFlowRulesSendingTrafficToEndPoint(endpoint.id)
                associated_flowrules = flowrule_out + flowrule_in
                for flowrule in associated_flowrules:
                    if flowrule.status == 'already_deployed':
                        flowrule.status = 'to_be_deleted'
                        new_flowrule = copy.deepcopy(flowrule)
                        new_flowrule.status = 'new'
                        updated_nffg.flow_rules.append(new_flowrule)
                        
                updated_nffg.end_points.remove(endpoint)                             
                                      
        for flowrule in updated_nffg.flow_rules[:]:
            if flowrule.status == 'to_be_deleted' and flowrule.type != 'external':
                self.deleteFlowRule(flowrule, updated_nffg)
        
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
        ports = Graph().getPorts(self.graph_id)
        for port in ports:
            if port.type == 'openstack':
                resources_status['ports'][port.id] = Neutron().getPortStatus(self.neutronEndpoint, token_id, port.internal_id)
        resources_status['vnfs'] = {}
        vnfs = Graph().getVNFs(self.graph_id)
        for vnf in vnfs:
            resources_status['vnfs'][vnf.id] = Nova().getServerStatus(self.novaEndpoint, token_id, vnf.internal_id)
        
        num_resources = len(resources_status['ports']) + len(resources_status['vnfs'])                
        num_resources_completed = 0
        
        for value in resources_status['ports'].itervalues():
            logging.debug("port - "+value)
            if value == 'ACTIVE' or value == 'DOWN':
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
            if num_resources != 0:
                status['percentage_completed'] = num_resources_completed/num_resources*100
            else:
                status['percentage_completed'] = 100
        else:
            status['status'] = 'in_progress'
            if num_resources != 0:
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
        Graph().setVNFInternalID(nf_fg.db_id, vnf.id, vnf.OSid, 'complete')
    
    def deleteServer(self, vnf, nf_fg):
        Nova().deleteServer(self.novaEndpoint, self.token.get_token(), vnf.internal_id)
        Graph().deleteFlowRuleFromVNF(vnf.db_id)
        Graph().deleteVNFNetworks(self.graph_id, vnf.db_id)     
        Graph().deletePort(None, self.graph_id, vnf.db_id)
        Graph().deleteVNF(vnf.id, self.graph_id)
        nf_fg.vnfs.remove(vnf)
    
    def createPort(self, port, vnf, nf_fg):
        if port.net is None:
            raise StackError("No network found for this port")
        
        json_data = port.getResourceJSON()      
        resp = Neutron().createPort(self.neutronEndpoint, self.token.get_token(), json_data)
        if resp['port']['status'] == "DOWN":
            port_internal_id = resp['port']['id']
            port.setInternalId(port_internal_id)
            Graph().setPortInternalID(self.graph_id, nf_fg.getVNF(vnf.id).db_id, port.id, port_internal_id, port.status, port_type='openstack')
            Graph().setOSNetwork(port.net, port.id, nf_fg.getVNF(vnf.id).db_id, port_internal_id, nf_fg.db_id,  vlan_id = port.vlan)
    
    def deletePort(self, vnf, port, nf_fg): 
        if port.status == 'to_be_deleted':
            Neutron().deletePort(self.neutronEndpoint, self.token.get_token(), port.internal_id)
            Graph().deleteFlowspecFromPort(port.id)
            p = Graph().getPortFromInternalID(port.internal_id, self.graph_id)
            Graph().deleteNetwork(p.os_network_id)
            Graph().deletePort(port.db_id, self.graph_id)
        else:
            # Delete flow-rules associated to that port
            for flowrule in nf_fg.getFlowRulesSendingTrafficFromPort(vnf.id, port.id):
                if flowrule.status == 'to_be_deleted':
                    Neutron().deletePort(self.neutronEndpoint, self.token.get_token(), port.internal_id)                                
                    p = Graph().getPortFromInternalID(port.internal_id, self.graph_id)
                    Graph().deleteNetwork(p.os_network_id)
                    Graph().deletePort(port.db_id, self.graph_id)
                    port.status = 'new'
            '''        
            for flowrule in nf_fg.getFlowRulesSendingTrafficToPort(vnf.id, port.id):
                if flowrule.status == 'to_be_deleted':
                    #check se endpoint o altra vnf per cancellare eventualmetne il flusso o la network sull'altra porta
                    Graph().deleteFlowRule(flowrule.db_id) # toglila
                    """
                    Neutron().deletePort(self.neutronEndpoint, self.token.get_token(), port.internal_id)                                
                    Graph().deleteFlowRule(flowrule.db_id)
                    p = Graph().getPortFromInternalID(port.internal_id)
                    Graph().deleteNetwork(p.os_network_id)
                    Graph().deletePort(port.db_id, self.graph_id)   
                    """                
                    nf_fg.flow_rules.remove(flowrule)
                    #port.status = 'new'                    
            '''
                
    def addPorttoVNF(self, port, vnf, nf_fg):
        vms = Graph().getVNFs(self.graph_id)
        for vm in vms:
            if vm.graph_vnf_id == vnf.id:
                self.createPort(port, vnf, nf_fg)
                Nova().attachPort(self.novaEndpoint, self.token.get_token(), port.internal_id, vm.internal_id)
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
    
    def getUnusedNetwork(self):
        '''
        Finds an unused openstack network
        '''
        for network in JOLNET_NETWORKS[:]:
            network_free = True
            net_id = self.getNetworkIdfromName(network)
            if net_id is not None:
                #Check if there are ports on this network
                json_data = Neutron().getPorts(self.neutronEndpoint, self.token.get_token())
                ports = json.loads(json_data)['ports']
                for port in ports:
                    if port['network_id'] == net_id:
                        network_free = False
                        JOLNET_NETWORKS.remove(network)
                        break
                if network_free is False:
                    continue
                JOLNET_NETWORKS.remove(network)
                return network, net_id
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
    #########################    Interactions with OpenDaylight              #############################
    ######################################################################################################
    ''' 
    def deleteFlowRule(self, flowrule, nf_fg):    
        flows = Graph().getFlowRules(self.graph_id)
        for flow in flows:
            if flow.type == "external" and flow.status == "complete" and flow.internal_id == flowrule.id:
                switch_id = Node().getNodeDomainID(flow.node_id)
                ODL(self.odlversion).deleteFlow(self.odlendpoint, self.odlusername, self.odlpassword, switch_id, flow.graph_flow_rule_id)
                Graph().deleteFlowRule(flow.id)
        Graph().deleteFlowRule(flowrule.db_id)
        nf_fg.flow_rules.remove(flowrule)
        
    def getLinkBetweenSwitches(self, switch1, switch2):             
        '''
        Retrieve the link between two switches, where you can find ports to use
        Args:
            switch1:
                OpenDaylight identifier of the source switch (example: openflow:123456789 or 00:00:64:e9:50:5a:90:90 in Hydrogen)
            switch2:
                OpenDaylight identifier of the destination switch (example: openflow:987654321 or 00:00:64:e9:50:5a:90:90 in Hydrogen)
        '''
        json_data = ODL(self.odlversion).getTopology(self.odlendpoint, self.odlusername, self.odlpassword)
        topology = json.loads(json_data)
        if self.odlversion == "Hydrogen":
            tList = topology["edgeProperties"]
            for link in tList:
                source_node = link["edge"]["headNodeConnector"]["node"]["id"]
                dest_node = link["edge"]["tailNodeConnector"]["node"]["id"]
                if (source_node == switch1 and dest_node == switch2):
                    return link
        else:
            tList = topology["network-topology"]["topology"][0]["link"]
            for link in tList:
                source_node = link["source"]["source-node"]
                dest_node = link["destination"]["dest-node"]
                if (source_node == switch1 and dest_node == switch2):
                    return link
    
    def pushVlanFlow(self, source_node, flow_id, vlan, in_port, out_port):
        '''
        Push a flow into a Jolnet switch with 
            matching on VLAN id and input port
            output through the specified port
        Args:
            source_node:
                OpenDaylight identifier of the source switch (example: openflow:123456789 or 00:00:64:e9:50:5a:90:90 in Hydrogen)
            flow_id:
                unique identifier of the flow on the whole OpenDaylight domain
            vlan:
                VLAN id of the traffic (for matching)
            in_port:
                ingoing port of the traffic (for matching)
            out_port:
                output port where to send out the traffic (action)
        '''
        action1 = Action()
        action1.setOutputAction(out_port, 65535)
        actions = [action1]
        
        match = Match()
        match.setInputMatch(in_port)
        match.setVlanMatch(vlan)
        
        flowj = Flow("jolnetflow", flow_id, 0, 65535, True, 0, 0, actions, match)        
        json_req = flowj.getJSON(self.odlversion, source_node)
        ODL(self.odlversion).createFlow(self.odlendpoint, self.odlusername, self.odlpassword, json_req, source_node, flow_id)

    def linkZones(self, graph_id, switch_user, port_vms_user, switch_user_id, switch_isp, port_vms_isp, switch_isp_id, vlan_id, endpoint_db_id):
        '''
        Link two graphs (or two parts of a single graph) through the SDN network
        Args:
            graph_id:
                id of the user's graph
            switch_user:
                OpenDaylight identifier of the first switch (example: openflow:123456789 or 00:00:64:e9:50:5a:90:90 in Hydrogen)
            port_vms_user:
                port on the OpenFlow switch where virtual machines are linked
            switch_user_id:
                id of the node in the database
            switch_isp:
                OpenDaylight identifier of the second switch (example: openflow:987654321 or 00:00:64:e9:50:5a:90:90 in Hydrogen)
            port_vms_isp:
                port on the OpenFlow switch where virtual machines are linked
            switch_isp_id:
                id of the node in the database
            vlan_id:
                VLAN id of the OpenStack network which links the graphs
            endpoint_db_id:
                DB ID of the endpoint which this flows are related to
        '''
        edge = None
        link = None
        if self.odlversion == "Hydrogen":
            edge = self.getLinkBetweenSwitches(switch_user, switch_isp)
            if edge is not None:
                port12 = edge["edge"]["headNodeConnector"]["id"]
                port21 = edge["edge"]["tailNodeConnector"]["id"]    
        else:
            link = self.getLinkBetweenSwitches(switch_user, switch_isp)
            if link is not None:        
                tmp = link["source"]["source-tp"]
                tmpList = tmp.split(":")
                port12 = tmpList[2]
                    
                tmp = link["destination"]["dest-tp"]
                tmpList = tmp.split(":")
                port21 = tmpList[2]
                
        if link is not None or edge is not None:
            fid = int(str(vlan_id) + str(1))              
            self.pushVlanFlow(switch_user, fid, vlan_id, port_vms_user, port12)
            flow_rule = FlowRule(_id=fid,node_id=Node().getNodeFromDomainID(switch_user).id,_type='external', status='complete',priority=65535)  
            Graph().addFlowRuleAsEndpointResource(self.graph_id, flow_rule, None, endpoint_db_id)
            
            fid = int(str(vlan_id) + str(2))
            self.pushVlanFlow(switch_isp, fid, vlan_id, port21, port_vms_isp)
            flow_rule = FlowRule(_id=fid,node_id=Node().getNodeFromDomainID(switch_isp).id,_type='external', status='complete',priority=65535)  
            Graph().addFlowRuleAsEndpointResource(self.graph_id, flow_rule, None, endpoint_db_id)
            
            fid = int(str(vlan_id) + str(3))               
            self.pushVlanFlow(switch_isp, fid, vlan_id, port_vms_isp, port21)
            flow_rule = FlowRule(_id=fid,node_id=Node().getNodeFromDomainID(switch_isp).id,_type='external', status='complete',priority=65535)  
            Graph().addFlowRuleAsEndpointResource(self.graph_id, flow_rule, None, endpoint_db_id)

            fid = int(str(vlan_id) + str(4))               
            self.pushVlanFlow(switch_user, fid, vlan_id, port12, port_vms_user)
            flow_rule = FlowRule(_id=fid,node_id=Node().getNodeFromDomainID(switch_user).id,_type='external', status='complete',priority=65535)  
            Graph().addFlowRuleAsEndpointResource(self.graph_id, flow_rule, None, endpoint_db_id)
        else:
            logging.debug("Cannot find a link between " + switch_user + " and " + switch_isp)
            
    def processFlowrule(self, endpoint1, flowrule, profile_graph):
        match1 = Match(flowrule.match)
        match2 = None
        actions1 = []
        actions2 = []
        switch1 = None
        switch2 = None
        flowname1 = None
        flowname2 = None
        
        for act in flowrule.actions:
            if act.drop is True:
                action = Action(act)
                actions = [action]
                match1.setInputMatch(endpoint1.interface)
                flowname = str(flowrule.id)
                flowj = Flow("flowrule", flowname, 0, flowrule.priority, True, 0, 0, actions, match1)        
                json_req = flowj.getJSON(self.odlversion, endpoint1.switch_id)
                ODL(self.odlversion).createFlow(self.odlendpoint, self.odlusername, self.odlpassword, json_req, endpoint1.switch_id, flowname)
                
                flow_rule = FlowRule(_id=flowname,node_id=Node().getNodeFromDomainID(endpoint1.switch_id).id,_type='external', status='complete',priority=flowrule.priority, internal_id=flowrule.id)  
                Graph().addFlowRule(self.graph_id, flow_rule, None)
                return  
    
        for act in flowrule.actions:
            #TODO: multiple output actions not supported
            if act.output is not None:
                tmp2 = act.output.split(':')
                port2_type = tmp2[0]
                port2_id = tmp2[1]
                if port2_type == 'endpoint': 
                    endpoint2 = profile_graph.endpoints[port2_id]
                                
                    if endpoint1.switch_id == endpoint2.switch_id:
                        if endpoint1.interface == endpoint2.interface:
                            raise GraphError("Flowrule "+flowrule.id+" is wrong: endpoints are overlapping")
                        else:
                            action1 = Action(act)
                            action1.setOutputAction(endpoint2.interface, 65535)
                            actions1.append(action1)

                            match1.setInputMatch(endpoint1.interface)
                            
                            flowname1 = str(flowrule.id)
                            switch1 = endpoint1.switch_id              
                    else:
                        edge = None
                        link = None
                        if self.odlversion == "Hydrogen":
                            edge = self.getLinkBetweenSwitches(endpoint1.switch_id, endpoint2.switch_id)
                            if edge is not None:
                                port12 = edge["edge"]["headNodeConnector"]["id"]
                                port21 = edge["edge"]["tailNodeConnector"]["id"]        
                        else:
                            link = self.getLinkBetweenSwitches(endpoint1.switch_id, endpoint2.switch_id)
                            if link is not None:            
                                tmp = link["source"]["source-tp"]
                                tmpList = tmp.split(":")
                                port12 = tmpList[2]
                                        
                                tmp = link["destination"]["dest-tp"]
                                tmpList = tmp.split(":")
                                port21 = tmpList[2]
                                
                        if link is not None or edge is not None:
                            if endpoint1.interface != port12 and endpoint2.interface != port21:
                                # endpoints are not on the link: 2 flows 
                                action1 = Action(act)
                                action1.setOutputAction(port12, 65535)
                                actions1.append(action1)
                                
                                match1.setInputMatch(endpoint1.interface)
                                
                                flowname1 = str(flowrule.id) + str(1) 
                                switch1 = endpoint1.switch_id

                                # second flow
                                action2 = Action()
                                action2.setOutputAction(endpoint2.interface, 65535)
                                actions2 = [action2]
                                match2 = Match()
                                match2.setInputMatch(port21) 
                                
                                flowname2 = str(flowrule.id) + str(2)
                                switch2 = endpoint2.switch_id
                                
                            elif endpoint1.interface != port12 and endpoint2.interface == port21:
                                #flow installed on first switch
                                action1 = Action(act)
                                action1.setOutputAction(port12, 65535)
                                actions1.append(action1)
                                
                                match1.setInputMatch(endpoint1.interface)
                                
                                flowname1 = str(flowrule.id)
                                switch1 = endpoint1.switch_id                                
                                
                            elif endpoint1.interface == port12 and endpoint2.interface != port21:
                                #flow installed on second switch
                                action1 = Action(act)
                                action1.setOutputAction(endpoint2.interface, 65535)
                                actions1.append(action1)
                                
                                match1.setInputMatch(port21)
                                
                                flowname1 = str(flowrule.id)
                                switch1 = endpoint2.switch_id
                                
                            elif endpoint1.interface == port12 and endpoint2.interface == port21:
                                #endpoints are on the link: cannot install flow
                                logging.warning("Flow not installed for flowrule id "+flowrule.id+ ": both endpoints are on the same link")
                        else:
                            logging.debug("Cannot find a link between " + endpoint1.switch_id + " and " + endpoint2.switch_id)
            elif act.output is None:
                action = Action(act)
                actions1.append(action)
                
        if switch1 is not None:        
            self.pushFlow(switch1, actions1, match1, flowname1, flowrule.priority, flowrule.id)
            if switch2 is not None:
                self.pushFlow(switch2, actions2, match2, flowname2, flowrule.priority, flowrule.id)
        
    def pushFlow(self, switch_id, actions, match, flowname, priority, flow_id):
        flowname = flowname.replace(' ', '')
        flowj = Flow("flowrule", flowname, 0, priority, True, 0, 0, actions, match)        
        json_req = flowj.getJSON(self.odlversion, switch_id)
        ODL(self.odlversion).createFlow(self.odlendpoint, self.odlusername, self.odlpassword, json_req, switch_id, flowname)
        
        flow_rule = FlowRule(_id=flowname,node_id=Node().getNodeFromDomainID(switch_id).id,_type='external', status='complete',priority=priority, internal_id=flow_id)  
        Graph().addFlowRule(self.graph_id, flow_rule, None)
