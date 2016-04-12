'''
Created on Oct 1, 2014

@author: fabiomignini
'''
from orchestrator_core.component_adapter.interfaces import OrchestratorInterface
from orchestrator_core.component_adapter.unify.rest import Unify
from orchestrator_core.component_adapter.unify.resources import VNFTemplate, ProfileGraph, FlowGraph, VNF
from nffg_library.nffg import NF_FG
from orchestrator_core.config import Configuration
#from Common.SQL.endpoint import set_endpoint,delete_endpoint_connections

import json, logging, copy, uuid
"""
INGRESS_PORT = Configuration().INGRESS_PORT
INGRESS_TYPE = Configuration().INGRESS_TYPE
EGRESS_PORT = Configuration().EGRESS_PORT
EGRESS_TYPE = Configuration().EGRESS_TYPE
"""
DEBUG_MODE = Configuration().DEBUG_MODE


class UnifyCA(OrchestratorInterface):
    '''
    Override class of the abstract class OrchestratorInterface
    Instantiate the user profile for the Unify node
    '''

    def __init__(self, session_id, compute_node_address, token):
        '''
        Constructor
        Args:
            unifyEndpoint:
                The endpoint of the unify node to contact
            the physical port of the unify node connected to the internet
        '''
        #check
        self._URI = "http://"+compute_node_address+":8080"
        self.token = token
        #self.corePort = corePort
        self.VNFs = {}
        #self.switch = Switch()
        
    @property
    def URI(self):
        return self._URI
    
    '''
    def checkProfile(self, session_id, token = None):
        return True
        """
        try:
            Unify().checkGraph(self.URI, session_id)
            logging.debug("Unify - checkProfile - Already deployed")
            return True
        except:
            logging.debug("Unify - checkProfile - Not deployed")
            return False
        """
    '''    
    
    def getStatus(self, session_id, node_endpoint):
        pass
    
    def buildProfileGraph(self, nf_fg):
        profile_graph = ProfileGraph()
        profile_graph.setId(nf_fg.id)
        
        for vnf in nf_fg.listVNF:
            #self.VNFs[vnf.id] = VNFTemplate(vnf)  # to check
            #nf = self.buildVNF(vnf)
            vn = VNF(vnf.id, vnf)
            profile_graph.addVNF(vn)
            
        for endpoint in nf_fg.listEndpoint:
            ep = self.buildEndpoint(endpoint)
            profile_graph.addEndpoint(ep)            
        
        '''
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
                           '''  
        return profile_graph    
    
    
    def buildEndpoint(self, endpoint):
        if endpoint.connection is False and endpoint.attached is False and endpoint.edge is False:
                #edge_endpoints = nf_fg.getEdgeEndpoint(endpoint.name, True)
                #logging.debug("NF-FG name: "+nf_fg.name)
                #logging.debug("Endpoint - endpoint.name: "+endpoint.name)
                    
                # Write in DB endpoint 1 to n
                '''
                for edge_endpoint in edge_endpoints:
                    set_endpoint(nf_fg._id, edge_endpoint.id, True, endpoint.name, endpoint._id, endpoint_type="endpoint")   
                '''
                         
        if endpoint.connection is True:
            endpoint.port = endpoint.remote_graph+":"+endpoint.remote_id
            
        return endpoint
    
    def reconciliateName(self, profile, output_graph):
        #TODO: do not use a global counter 
        counter = 1
        seen = set()

        for vnf in profile.VNFs.values():
            if vnf.name in seen:
                logging.debug("vnf[name] "+vnf.name)
                vnf.name = vnf.name + str(counter)
                logging.debug(" to ->>>vnf[name] "+vnf.name)
                counter += 1
            seen.add(vnf.name)
            output_graph.addVNF(vnf.name)
    
    def instantiateProfile(self, nf_fg, node_endpoint):
        '''
        Instatiate the profile on a Unify node
        Args
            profile:
                The user NF-FG        
        '''               
        try:
            output_graph = FlowGraph()
            profile_graph = self.buildProfileGraph(nf_fg)
            self.reconciliateName(profile_graph, output_graph)
                        
            for vnf in profile_graph.VNFs.values():
                for port in vnf.listPort:
                    for flowrule in port.list_outgoing_label:
                        logging.debug("vnf: "+vnf.id+" - port: "+port.id + " - outgoing")
                        self.analyzeLinks(output_graph, profile_graph, vnf, port, flowrule)
                    for flowrule in port.list_ingoing_label:
                        #if flowrule.action.type == "output":
                            #if flowrule.matches is not None:
                        logging.debug("vnf: "+vnf.id+" - port: "+port.id + " - ingoing")
                        self.analyzeLinks(output_graph, profile_graph, vnf, port, flowrule)
            
            '''
            for vnf in nf_fg['profile']['VNFs']:
            # ..and each contained flowrules
            for port in vnf["ports"]:
                #logging.debug(port)
                for flowrule in port['outgoing_label']['flowrules']:
                    logging.debug("vnf: "+vnf["id"]+" - port: "+port["id"])
                    self.analyzeLinks(graph, nf_fg, vnf, port, flowrule, counter_id)
                if 'ingoing_label' in port:
                    for flowrule in port['ingoing_label']['flowrules']:
                        logging.debug("vnf: "+vnf["id"]+" - port: "+port["id"])
                        self.analyzeLinks(graph, nf_fg, vnf, port, flowrule, counter_id)
             '''           
            logging.debug("Unify - instantiateProfile - nf-fg")
            logging.debug(json.dumps(output_graph.getJSON()))
            
            #if DEBUG_MODE is not True:
            ##    Unify().instantiateGraph(self.URI, nf_fg['profile']['id'] , graph)  
            Unify().instantiateGraph(self.URI, profile_graph.id , output_graph.getJSON()) 

            
        except Exception as err:
            logging.error(err.message)
            logging.exception(err) 
            raise


    def analyzeLinks(self, output_graph, profile_graph, vnf, port, flowrule):

        if flowrule.action.type == "output":    
            # IF ingress --> we have to set the ingress port with the actual port where the user is connected
            if flowrule.action.vnf is None:
                #Endpoint
                if profile_graph.endpoints[flowrule.action.endpoint['id']].port is not None and profile_graph.endpoints[flowrule.action.endpoint['id']].port.find(":") != -1:
                    # External endpoint
                    action = {"endpoint_id": profile_graph.endpoints[flowrule.action.endpoint['id']].port}
                elif 'id' in flowrule.action.endpoint and profile_graph.endpoints[flowrule.action.endpoint['id']].type == "physical":
                    # Endpoint Characterized
                    action = {"port": profile_graph.endpoints[flowrule.action.endpoint['id']].interface}
                else:
                    endpoint = profile_graph.id +":"+ str(flowrule.action.endpoint['id'])
                    action = {"endpoint_id": endpoint}
            else:
                # VNF
                port_id  = int(profile_graph.VNFs[flowrule.action.vnf['id']].ports_label[flowrule.action.vnf['port'].split(":")[0]]) + int(flowrule.action.vnf['port'].split(":")[1])
                action = {"VNF_id": profile_graph.VNFs[flowrule.action.vnf['id']].name + ":" + str(port_id+1)}
            
            if "ingress_endpoint" in flowrule.flowspec:
                physical_port = False
                if profile_graph.endpoints[flowrule.flowspec["ingress_endpoint"]].port is not None and profile_graph.endpoints[flowrule.flowspec["ingress_endpoint"]].port.find(":") != -1:
                    # External endpoint
                    new_port = profile_graph.endpoints[flowrule.flowspec["ingress_endpoint"]].port
                elif 'ingress_endpoint' in flowrule.flowspec and profile_graph.endpoints[flowrule.flowspec["ingress_endpoint"]].type == "physical":
                    # Endpoint Characterized
                    new_port = profile_graph.endpoints[flowrule.flowspec["ingress_endpoint"]].interface
                    physical_port = True
                else:                   
                    new_port = profile_graph.id+ ":" +flowrule.flowspec['ingress_endpoint']
                edge = True
            else:
                port_id  = int(profile_graph.VNFs[vnf.id].ports_label[port.id.split(":")[0]]) + int(port.id.split(":")[1])
    
                ##new_port = self.VNFs_name[vnf["id"]] + ":" + str(port_id+1)
                new_port = profile_graph.VNFs[vnf.id].name + ":" + str(port_id+1)
                edge = False
            
            for match in flowrule.matches:
                link = {}
                """
                if update is True:
                    link["id"] = uuid.uuid4().hex
                else:
                    link["id"] = match["id"]
                """          
                link["id"] = match.id
                link["action"] = action
                #link["id"] = str(counter_id)
                ##counter_id = counter_id + 1
                linkMatch = {}
                if not edge:
                    linkMatch["VNF_id"] = new_port
                else:
                    if physical_port is True:
                        linkMatch["port"] = new_port
                    else:
                        linkMatch["endpoint_id"] = new_port
                protocol = None
                sourcePort = -1
                destPort = -1
                for rule in match.of_field:
                    if rule == "id" or rule == "hardTimeout" or rule == "vlanPriority" or rule == "tosBits":
                        continue
                    if rule == "etherType":
                        linkMatch["ethertype"] = match.of_field[rule]
                    elif rule == "vlanId":
                        linkMatch["vlan_id"] = match.of_field[rule]
                    elif rule == "sourceMAC":
                        linkMatch["eth_src"] = match.of_field[rule]
                    elif rule == "destMAC":
                        linkMatch["eth_dst"] = match.of_field[rule]
                    elif rule == "sourceIP":
                        linkMatch["ipv4_src"] = match.of_field[rule]
                    elif rule == "destIP":
                        linkMatch["ipv4_dst"] = match.of_field[rule]
                    elif rule == "protocol":
                        protocol = match[rule]
                        if protocol == "tcp":
                            linkMatch["ip_proto"] = "6"
                        if sourcePort != -1:
                            if protocol == "tcp":
                                linkMatch["tcp_src"] = str(sourcePort)
                            elif protocol == "udp":
                                linkMatch["udp_src"] = str(sourcePort)
                        if destPort != -1:
                            if protocol == "tcp":
                                linkMatch["tcp_dst"] = str(destPort)
                            elif protocol == "udp":
                                linkMatch["udp_dst"] = str(destPort)
                    elif rule == "sourcePort":
                        if protocol == "tcp":
                            linkMatch["tcp_src"] = str(match.of_field[rule])
                        elif protocol == "udp":
                            linkMatch["udp_src"] = str(match.of_field[rule])
                        elif protocol == None:
                            sourcePort = int(match.of_field[rule])
                    elif rule == "destPort":
                        if protocol == "tcp":
                            linkMatch["tcp_dst"] = str(match.of_field[rule])
                        elif protocol == "udp":
                            linkMatch["udp_dst"] = str(match.of_field[rule])
                        elif protocol == None:
                            destPort = int(match.of_field[rule])
                    else:
                        # Fields that don't change will be copied without any modification 
                        linkMatch[rule] = match.of_field[rule]
                # Dirty workaround to remove priority from match --> to be fixed!!!!
                linkMatch.pop("priority") 
                link["match"] = linkMatch                  
                link["priority"] = match.of_field["priority"]
                
                output_graph.addFlowrule(link)
                
    def deinstantiateProfile(self, nf_fg, node_endpoint):
        '''
        Delete the flow with ID "flow_id" from the graph with name "myGraph".
        DELETE /graph/myGraph/flow_id HTTP/1.1
        '''
        
        #delete_endpoint_connections(profile_id) 
        
        # unifyEndpoint, graphID, unifyJSON
        if DEBUG_MODE is not True:
            Unify().deinstantiateGraph(self.URI, nf_fg.id)    
        
    def computeDiff(self, new_nf_fg, old_nf_fg):
        '''
        find the new flowrules
        '''
        new_nf_fg = NF_FG(new_nf_fg)
        old_nf_fg = NF_FG(old_nf_fg)
        
        manage_old_nf_fg = NF_FG_Management(old_nf_fg)
        mac_addresses = manage_old_nf_fg.getMacAddressFlows()
        logging.debug("Device/s that still alive"+str(mac_addresses))
        
        manage_new_nf_fg = NF_FG_Management(new_nf_fg)
        return manage_new_nf_fg.getNewFlows(mac_addresses)
               
    #def updateProfile(self, nf_fg_id, new_nf_fg, old_nf_fg, token, delete = False):
    def updateProfile(self, new_nf_fg, old_nf_fg, node_endpoint):
        '''
        Compute a diff between new nf-fg and old nf-fg, 
        then send the changes to Unified node
        '''       
        #updated_nffg = NFFG_Management().diff(old_nf_fg, new_nf_fg)    
        updated_nffg = None
        logging.debug("diff: " + updated_nffg.getJSON()) 
        
        
        
        # initialize data-structures for the UN-NODE
        graph = {}
        graph["flow-graph"] = {}
        graph["flow-graph"]["VNFs"] = []
        graph["flow-graph"]["flow-rules"] = []
        

        
        endpoint = Endpoint(self, copy.deepcopy(new_nf_fg))
        new_nf_fg = endpoint.nf_fg
        self.reconciliateName(new_nf_fg, graph)
        nf_fg = NF_FG(copy.deepcopy(new_nf_fg))

        
        endpoint = Endpoint(self, copy.deepcopy(old_nf_fg))
        old_nf_fg = endpoint.nf_fg
        self.reconciliateName(old_nf_fg, graph)
        
        
        for vnf in new_nf_fg['profile']['VNFs']:
            self.VNFs[vnf["id"]] = VNFTemplate(vnf)
            

        
        logging.debug("Unify CA - Update - new_nf_fg : "+json.dumps(new_nf_fg))
        
        if delete == False:
            logging.debug("            Unify CA - Update - new_nf_fg : FALSE")
            update_flows = self.computeDiff(new_nf_fg, old_nf_fg)
        else:
            logging.debug("            Unify CA - Update - new_nf_fg : TRUE")
            
            update_flows = self.computeDiff(old_nf_fg, new_nf_fg)
            update_flows_str  = nf_fg.getIngoingFlowruleJson(update_flows)
            logging.debug("Unify CA - Update - flowrule : "+update_flows_str)
            for update_flow in update_flows:
                for match in update_flow.flowspec['matches']:
                    logging.debug("Unify CA - Update - update_flows - delete flow :"+str(match._id))
                    Unify().deleteFlow(self.URI, nf_fg_id, match._id )
            return
        
        for update_flow in update_flows:
            logging.debug("Unify CA - Update - update_flows - ingress endpoint :"+str(update_flow.flowspec['ingress_endpoint']))
            logging.debug("Unify CA - Update - update_flows - action :"+str(self.VNFs_name[update_flow.action.vnf['id']]))
            for match in update_flow.matches:
                if 'sourceMAC' in match.of_field:
                    logging.debug("Unify CA - Update - update_flows - match :"+str(match.of_field['sourceMAC']))
                
        update_flows  = nf_fg.getIngoingFlowruleJson(update_flows)
        logging.debug("Unify CA - Update - flowrule : "+update_flows)
        
        for flowrule in json.loads(update_flows):
            self.analyzeLinks(graph, new_nf_fg, vnf, None, flowrule, 0, True)
        logging.debug("Unify - updateProfile - nf-fg")
        
        # Insert list of VNFs with link modified
        logging.debug("\n"+json.dumps(graph))
        new_vnfs = [] 
        for flowrule in graph["flow-graph"]["flow-rules"]:
            
            # Action
            if "VNF_id" in flowrule["action"]:
                vnf = flowrule["action"]["VNF_id"].split(":")[0]
                find = False
                for new_vnf in new_vnfs:
                    if vnf["id"] == new_vnf["id"]:
                        find = True
                if find is False:
                    new_vnfs.append(vnf)
                
            # Match
            if "VNF_id" in flowrule["match"]:
                vnf = flowrule["match"]["VNF_id"].split(":")[0]
                find = False
                for new_vnf in new_vnfs:
                    if vnf["id"] == new_vnf["id"]:
                        find = True
                if find is False:
                    new_vnfs.append(vnf)
        
        del graph["flow-graph"]["VNFs"]
        graph["flow-graph"]["VNFs"] = []
        for new_vnf in new_vnfs:
            id_vnf = {}
            id_vnf['id'] = new_vnf
            graph["flow-graph"]["VNFs"].append(id_vnf)
        
        #graph["flow-graph"]["VNFs"] = vnfs
        logging.debug("\n"+json.dumps(graph))
        if DEBUG_MODE is not True:
            Unify().updateGraph(self.URI, nf_fg_id, graph)
                      
                    
    def reconciliateNameOLD(self, profile, graph):
        self.VNFs_name = {}
        switch_counter = 0
        bridge_counter = 0
        for vnf in profile['profile']['VNFs']:
            logging.debug("vnf[name] "+vnf["name"])
            
            if profile['profile']['id'] == "3" and vnf["name"] == "dhcp_blue":
                vnf["name"] = "dhcp_red"
            if profile['profile']['id'] == "3" and vnf["name"] == "nat_blue":
                vnf["name"] = "nat_red"
            
            if "Endpoint_Switch" in vnf["name"] and profile['profile']['name'] != "ISPgraph":
                #logging.debug("vnf[name]: "+ vnf["name"])
                #vnf["name"] = "bridge"+str(bridge_counter)
                #bridge_counter = bridge_counter + 1
                
                logging.debug("vnf[name]: "+ vnf["name"])
                vnf["name"] = "switch"+str(switch_counter)
                switch_counter = switch_counter + 1
            

                
            if "Switch" in vnf["name"]:
                logging.debug("vnf[name]: "+ vnf["name"])
                vnf["name"] = "switch"+str(switch_counter)
                
                switch_counter = switch_counter + 1

            if vnf['id'] == "Nobody_Switch":
                vnf["name"] = "sw_openflow"
            
            """
            if vnf['id'] == "Switch_ISP":
                vnf["name"] = "bridge1"
            """
            
            logging.debug(" to ->>>vnf[name] "+vnf["name"])
            graph["flow-graph"]["VNFs"].append({"id": vnf["name"]})
            self.VNFs_name[vnf["id"]] = vnf["name"]
        
          
    def analyzeLinksOLD(self, graph, nf_fg, vnf, port, flowrule, counter_id, update = None):
        nf_fg_obj = NF_FG(copy.deepcopy(nf_fg))
        
        # Action != output not supported now
        if flowrule["action"]["type"] == "output":
            
            # IF ingress --> we have to set the ingress port with the actual port where the user is connected
            if "VNF" not in flowrule["action"]:
                
                if nf_fg_obj.getEndpointMap()[flowrule["action"]["endpoint"]["id"]].port is not None and nf_fg_obj.getEndpointMap()[flowrule["action"]["endpoint"]["id"]].port.find(":") != -1:
                    # External endpoint
                    action = {"endpoint_id": nf_fg_obj.getEndpointMap()[flowrule["action"]["endpoint"]["id"]].port}
                elif 'id' in flowrule["action"]["endpoint"] and nf_fg_obj.getEndpointMap()[flowrule["action"]["endpoint"]["id"]].type == "physical":
                    # Endpoint Characterized
                    action = {"port": nf_fg_obj.getEndpointMap()[flowrule["action"]["endpoint"]["id"]].interface}
                else:
                    endpoint = nf_fg['profile']['id']+":"+ str(flowrule["action"]["endpoint"]["id"])
                    action = {"endpoint_id": endpoint}
            else:
                # Normal flowrule translation
                port_id  = int(self.VNFs[flowrule["action"]["VNF"]["id"]].ports_label[flowrule["action"]["VNF"]["port"].split(":")[0]]) + int(flowrule["action"]["VNF"]["port"].split(":")[1])
                action = {"VNF_id": self.VNFs_name[flowrule["action"]["VNF"]["id"]] + ":" + str(port_id+1)}
            
            if "ingress_endpoint" in flowrule["flowspec"]:
                physical_port = False
                if nf_fg_obj.getEndpointMap()[flowrule["flowspec"]["ingress_endpoint"]].port is not None and nf_fg_obj.getEndpointMap()[flowrule["flowspec"]["ingress_endpoint"]].port.find(":") != -1:
                    # External endpoint
                    new_port = nf_fg_obj.getEndpointMap()[flowrule["flowspec"]["ingress_endpoint"]].port
                elif 'ingress_endpoint' in flowrule["flowspec"] and nf_fg_obj.getEndpointMap()[flowrule["flowspec"]["ingress_endpoint"]].type == "physical":
                    # Endpoint Characterized
                    new_port = nf_fg_obj.getEndpointMap()[flowrule["flowspec"]["ingress_endpoint"]].interface
                    physical_port = True
                else:                   
                    # port = profile['session_param']["port"]
                    #port = flowrule["flowspec"]["ingressPort"]
                    new_port = nf_fg['profile']['id']+ ":" +flowrule["flowspec"]['ingress_endpoint']
                edge = True
            else:
                port_id  = int(self.VNFs[vnf["id"]].ports_label[port["id"].split(":")[0]]) + int(port["id"].split(":")[1])
    
                new_port = self.VNFs_name[vnf["id"]] + ":" + str(port_id+1)
                edge = False
            
            for match in flowrule["flowspec"]["matches"]:
                link = {}
                """
                if update is True:
                    link["id"] = uuid.uuid4().hex
                else:
                    link["id"] = match["id"]
                """

                
                link["id"] = match["id"]
                link["action"] = action
                #link["id"] = str(counter_id)
                counter_id = counter_id + 1
                linkMatch = {}
                if not edge:
                    linkMatch["VNF_id"] = new_port
                else:
                    if physical_port is True:
                        linkMatch["port"] = new_port
                    else:
                        linkMatch["endpoint_id"] = new_port
                protocol = None
                sourcePort = -1
                destPort = -1
                for rule in match.keys():
                    if rule == "id" or rule == "hardTimeout" or rule == "vlanPriority" or rule == "tosBits":
                        continue
                    if rule == "etherType":
                        linkMatch["ethertype"] = match[rule]
                    elif rule == "vlanId":
                        linkMatch["vlan_id"] = match[rule]
                    elif rule == "sourceMAC":
                        linkMatch["eth_src"] = match[rule]
                    elif rule == "destMAC":
                        linkMatch["eth_dst"] = match[rule]
                    elif rule == "sourceIP":
                        linkMatch["ipv4_src"] = match[rule]
                    elif rule == "destIP":
                        linkMatch["ipv4_dst"] = match[rule]
                    elif rule == "protocol":
                        protocol = match[rule]
                        if protocol == "tcp":
                            linkMatch["ip_proto"] = "6"
                        if sourcePort != -1:
                            if protocol == "tcp":
                                linkMatch["tcp_src"] = str(sourcePort)
                            elif protocol == "udp":
                                linkMatch["udp_src"] = str(sourcePort)
                        if destPort != -1:
                            if protocol == "tcp":
                                linkMatch["tcp_dst"] = str(destPort)
                            elif protocol == "udp":
                                linkMatch["udp_dst"] = str(destPort)
                    elif rule == "sourcePort":
                        if protocol == "tcp":
                            linkMatch["tcp_src"] = str(match[rule])
                        elif protocol == "udp":
                            linkMatch["udp_src"] = str(match[rule])
                        elif protocol == None:
                            sourcePort = int(match[rule])
                    elif rule == "destPort":
                        if protocol == "tcp":
                            linkMatch["tcp_dst"] = str(match[rule])
                        elif protocol == "udp":
                            linkMatch["udp_dst"] = str(match[rule])
                        elif protocol == None:
                            destPort = int(match[rule])
                    else:
                        # Fields that don't change will be copied without any modification 
                        linkMatch[rule] = match[rule]
                # Dirty workaround to remove priority from match --> to be fixed!!!!
                linkMatch.pop("priority") 
                link["match"] = linkMatch                  
                link["priority"] = match["priority"]
                graph["flow-graph"]["flow-rules"].append(link)      
      
          
        
'''
class Switch(object):
    
    def __init__(self):
        self.vnf = None
        self.listVNF = {}
        self.num_port = 1
        
    def addPort(self, otherVNF):
        self.listVNF[self.num_port] = otherVNF
        self.num_port += 1
'''