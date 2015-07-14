'''
@author: fabiomignini
'''

from __future__ import division

import json
import time
import copy
import falcon
import logging

from ServiceLayerApplication.validate_request import UserProfileValidator
from Common.config import Configuration
from Common.SQL.session import Session
from Common.SQL.graph import Graph
#from Common.SQL.session import get_active_user_devices, update_session, get_active_user_session, add_mac_address_in_the_session, get_active_user_device_session, set_ended,get_instantiated_profile,checkDeviceSession, del_mac_address_in_the_session
from Common.authentication import KeystoneAuthentication 
from Common.ServiceGraph.keystone import KeystoneProfile
from Common.users import User
from Common.NF_FG.nf_fg import NF_FG
from Common.NF_FG.nf_fg_managment import NF_FG_Management
from Common.ServiceGraph.service_graph import ServiceGraph
from Common.exception import ISPNotDeployed, NoMacAddress
from ServiceLayerApplication.common.user_session import UserSession
from ServiceLayerApplication.common.endpoint import Endpoint
from ServiceLayerApplication.orchestrator_rest import GlobalOrchestrator

ISP = Configuration().ISP
ISP_USERNAME = Configuration().ISP_USERNAME
ISP_PASSWORD = Configuration().ISP_PASSWORD
ISP_TENANT = Configuration().ISP_TENANT
# End-points type
USER_EGRESS = Configuration().USER_EGRESS
CONTROL_EGRESS = Configuration().CONTROL_EGRESS
ISP_INGRESS = Configuration().ISP_INGRESS
ISP_EGRESS = Configuration().ISP_EGRESS
CONTROL_INGRESS = Configuration().CONTROL_INGRESS

INGRESS_PORT = Configuration().INGRESS_PORT
INGRESS_TYPE = Configuration().INGRESS_TYPE
EGRESS_PORT = Configuration().EGRESS_PORT
EGRESS_TYPE = Configuration().EGRESS_TYPE
USER_INGRESS = Configuration().USER_INGRESS


class OrchestratorController():

    def __init__(self, keystone_server, OrchestratorToken, method, response = None, request = None, mac_address = None, token = None):
        #logging.debug('OrchestratorController - init - begin')
        
        self.user_mac = None
        self.keystone_server = keystone_server
        self.response = response
        self.orchToken = OrchestratorToken
        self.request = request
        session_flag = False
        self.nobody_flag = False
        self.orchestrator_ip = Configuration().ORCH_IP
        self.orchestrator_port = Configuration().ORCH_PORT
        
        if request is not None:
            if method != "GET" and method != "DELETE":
                session = json.load(request.stream, 'utf-8')
                session_flag = True
            if method == "DELETE":
                if mac_address is not None:
                    mac_address = mac_address.lower()
                self.user_mac = mac_address
            
        if (session_flag):
            # Validate the request Json
            UserProfileValidator().validate_sessione(session)
            if 'mac' in session['session']['session_param']:
                self.user_mac = session['session']['session_param']['mac'].lower()
            else: 
                self.user_mac = None
            
            self.session = copy.copy(session['session'])
            logging.debug("Session param : "+json.dumps(self.session))
        
            
        # Get token from header 
        #if request is not None:
        if token is None:
            token = request.get_header("X-Auth-Token")
            if token is None:
                description = "{\"error\":{\"message\":\"Please provide an auth token\",\"code\":\"401\",\"title\":\"Unauthorized\"}}"            
                raise falcon.HTTPUnauthorized('Auth token required',
                                              description,
                                              href='http://docs.example.com/auth')
        self.token = token
        
        self.orchestrator = GlobalOrchestrator(self.token, self.orchestrator_ip, self.orchestrator_port)
    
    def get(self):
        #getStackStatus(self.token)
        logging.debug("Authenticating the user - GET")
        token = KeystoneAuthentication(self.keystone_server,user_token=self.token, orch_token=self.orchToken)
        
        session = Session().get_active_user_session(token.get_userID()) 

        
        status = json.loads(self.orchestrator.checkNFFG(session.service_graph_id))
        logging.debug("Status : "+status['status'])
        if status['status'] == "complete":
            code = falcon.HTTP_201
        else:
            code = falcon.HTTP_202

        logging.debug("Username : "+token.get_username()+", Resources : "+json.dumps(status))
        
        
        self.response.body = json.dumps(status)
        self.response.status = code    
  
        logging.debug("GET from Username : "+token.get_username())
    
    def delete(self):
        # Authenticate the User
        logging.debug("Authenticating the user - DELETE")
        token = KeystoneAuthentication(self.keystone_server,user_token=self.token, orch_token=self.orchToken)
        
        # Retrieve the session data, from active session on a port of a switch passed, if no active session raise an exception
        #session = get_active_user_device_session(token.get_userID(), self.session)
        #logging.debug("self.request.stream: "+str(self.request.stream))
        #session_id = json.load(self.request.stream, 'utf-8')['session_id']
        """
        If there are more active session for specific user a delete become an update
        that erase a mac rule of user, otherwise if there is only one active session for the user
        the nf-fg will be de-instantiated
        """
        # TODO: delete of one device
        
        # returns the number of active session for the user, 
        # and if exists the session for the requested device
        logging.debug("User to delete: "+str(token.get_userID()))
        logging.debug("Device to delete: "+str(self.user_mac))
        
        num_sessions, session = Session().get_active_user_device_session(token.get_userID(), self.user_mac) 
        #num_sessions, session = get_active_user_device_session(token.get_userID())
        
        
        #UpperLayerOrchestratorController 
        logging.debug("Number of session for the user: "+str(num_sessions))
        

        if num_sessions == 1:
            # De-instantiate User Profile Graph
            self.orchestrator.delete(session.service_graph_id)
            logging.debug('Deinstantiate profile - user \"'+token.get_username()+'\" - Success')
            print 'ServiceLayerApplication - DELETE - User "'+token.get_username()+'"'
            
            # Set the field ended in the table session to the actual datatime
            #set_ended(session.id)
        else:
            logging.debug('Delete access for specific device')
            # Get profile from session
            old_profile = Graph().get_instantiated_nffg(token.get_userID())
            logging.debug('old_profile :'+old_profile.getJSON())
            
            #profile_analisis = ProfileAnalisis()
            manage = NF_FG_Management(old_profile)
            new_nf_fg = manage.deleteMacAddressInFlows(self.user_mac, USER_INGRESS)
            logging.debug('new_nf_fg :'+new_nf_fg.getJSON())
            
            
            #new_profile = profile_analisis.deleteMacAddressInFlows(old_profile, self.user_mac)
            
            
                    
            # Call CA for update graph without rule for deleted device
            self.orchestrator.put(new_nf_fg)
            #updateProfile(new_nf_fg._id,json.dumps(new_nf_fg.getJSON()))  
            
            # Set the field ended in the table session to the actual datatime
            
            
            logging.debug('ServiceLayerApplication - DELETE - Device deleted "'+self.user_mac+'" of user "'+token.get_username()+'"')
            print 'ServiceLayerApplication - DELETE - Device deleted "'+self.user_mac+'" of user "'+token.get_username()+'"'
        
        if self.user_mac is not None:
            Session().del_mac_address_in_the_session(self.user_mac, session.id)
         
    def put(self):
        """
        Request of profile scheduling from specific user
        
        """
        
        # Authenticate the User
        logging.debug('ServiceLayerApplication - PUT - Authenticating the user ')
        token = KeystoneAuthentication(self.keystone_server,user_token=self.token, orch_token=self.orchToken)
        logging.debug('ServiceLayerApplication - PUT - User "'+token.get_username())
           
       
        # Update last_login field in keystone.user table
        user = User()
        user.updateUser(token.get_token(), token.get_userID(), time.time(), self.keystone_server)
        
        
        #get user profile
        profile = KeystoneProfile(self.keystone_server, token.get_userID())
        self.graph = profile.get(self.token)['profile']['graph']
        
        # Check if the user have an active session
        logging.debug('ServiceLayerApplication - PUT - Checking session ')
        if UserSession(token.get_userID(), token).checkSession(self.graph['profile']['id'], self.orchestrator) is True:
            # Existent session for this user
            
            logging.debug('ServiceLayerApplication - PUT - Add device')
            
            # Manage new device
            if Session().checkDeviceSession(token.get_userID(), self.user_mac) is True:
                """
                 A rule for this mac address is already implemented,
                 only an update of the graph is needed 
                 (This update is necessary only if the graph is different from the last instantiated, 
                 but in this moment the graph is always re-instantiated).
                """
                self.user_mac = None
                
            """
             WARNING: the update, when a graph is connected to ISP, is not supported
            """
            new_nffg, isp_nf_fg = self.addDeviceToNF_FG(token)
            if isp_nf_fg is not None:
                raise NotImplemented("Update of graph attached to ISP graph")
            
            
            # Call orchestrator to update NF-FG
            logging.debug('ServiceLayerApplication - PUT - Calling orchestrator sending the following NF-FG')
            logging.debug(json.dumps(new_nffg))
            session_id = self.orchestrator.put(new_nffg)
            if self.user_mac is not None:
                logging.debug('ServiceLayerApplication - PUT - Added device "'+self.user_mac+'" of user "'+token.get_username()+'"')
                print 'ServiceLayerApplication - PUT - Added device "'+self.user_mac+'" of user "'+token.get_username()+'"'
            else:
                logging.debug('ServiceLayerApplication - PUT - User "'+token.get_username()+'"')
                print 'ServiceLayerApplication - PUT - User "'+token.get_username()+'"'
        else:
            # New session for this user
            
            logging.debug('ServiceLayerApplication - PUT - Instantiate profile')
        
            # Manage profile
            logging.debug("before"+json.dumps(self.graph))
            self.nf_fg, isp_nf_fg = self.prepareProfile(token)  
              
            
            # Call orchestrator to instantiate NF-FG
            logging.debug('ServiceLayerApplication - PUT - Calling orchestrator sending NF-FG')
            logging.debug("\n"+json.dumps(self.nf_fg))
            session_id = self.orchestrator.put(self.nf_fg)
            logging.debug('ServiceLayerApplication - PUT - Profile instantiated for user "'+token.get_username()+'"')
            print 'ServiceLayerApplication - PUT - Profile instantiated for user "'+token.get_username()+'"'
            
        # Set mac address in the session
        if self.user_mac is not None:
            Session().add_mac_address_in_the_session(self.user_mac, session_id)
    
        
    def addDeviceToNF_FG(self, token):
        
        
        
        # Get MAC addresses from previous session
        logging.debug('Get MAC addresses from previous session')
        session_mac_addresses = Session().get_active_user_devices(token.get_userID())
        mac_addresses = []
        if session_mac_addresses is not None:
            mac_addresses = mac_addresses+session_mac_addresses
        if self.user_mac is not None:
            logging.debug('new MAC : '+str(self.user_mac))      
            mac_addresses.append(str(self.user_mac))
        logging.debug('MAC addresses: '+str(mac_addresses))        
        
        # Retrieve the user profile
        logging.debug('ServiceLayerApplication -  addDeviceToNF_FG - Getting user profile')
        profile = KeystoneProfile(self.keystone_server, token.get_userID())
        self.graph = profile.get(token.get_token())['profile']['graph']
        #logging.debug('\n'+json.dumps(self.graph))

        # Add device specific rules
        logging.debug('ServiceLayerApplication -  addDeviceToNF_FG - Adding devices specific rules')
        nf_fg = NF_FG(self.graph)
        
        nf_fg, isp_nf_fg = self._prepareProfile(token, nf_fg)

        # TODO: I should check the mac address already used in the ingress end point, but then
        # use the new graph to add all the mac (both those old and that new)
        if len(mac_addresses) != 0:
            manage_nf_fg = NF_FG_Management(nf_fg, self.token)
            manage_nf_fg.addDevicesFlows(mac_addresses)
        
            
        return json.loads(nf_fg.getJSON()), isp_nf_fg
    
    def _prepareProfile(self, token, nf_fg):
        
        manage = NF_FG_Management(nf_fg, self.token)        
        
        # Get INGRESS NF-FG
        logging.debug('Getting INGRESS NF-FG')
        ingress_nf_fg = manage.getIngressNF_FG()
        
        # Attach INGRESS NF_FG to USER_INGESS ENDPOINT
        logging.debug('Attach INGRESS NF_FG to USER_INGESS ENDPOINT')
        #logging.info(ingress_nf_fg.getJSON())
        manage.attachIngressNF_FG(ingress_nf_fg)
                
        # Get EGRESS NF-FG
        logging.debug('Getting EGRESS NF-FG')
        egress_nf_fg =manage.getEgressNF_FG()
        
        # Attach EGRESS NF_FG to USER_EGRESS ENDPOINT
        logging.debug('Attach EGRESS NF_FG to USER_EGRESS ENDPOINT')
        manage.attachEgressNF_FG(egress_nf_fg)
        
        # Add control network
        logging.debug('Adding controll network')
        for vnf in nf_fg.listVNF:
            #logging.info("Control vnf : "+vnf.name)
            need_control_net, port = manage.checkIfControlNetIsNedeed(vnf)
            #logging.info("Control port")
            if need_control_net is True:
                #logging.info(port.id)
                if ISP is True:
                    control_switch = manage.addToControlNet(vnf, port, CONTROL_EGRESS)
                else:
                    control_switch = manage.addToControlNet(vnf, port, ISP_EGRESS)
                    
                if nf_fg.name == 'ISP_graph':
                    
                    if control_switch is not None:
                        user_control_egress  = nf_fg.createEndpoint(CONTROL_INGRESS)
                        port = nf_fg.addPortToSwitch(control_switch)
                        port.setFlowRuleToEndpoint(user_control_egress.id)
                        port.setFlowRuleFromEndpoint(control_switch.id, user_control_egress.id)
                            
            #logging.info("")
            
        # TODO: if endpoint is ... then connect tu ISP
        # Create connection to another NF-FG
        isp_nf_fg = None
        # TODO: The following row should be executed only if  we want to concatenate ISP to our graphs
        if ISP is True and nf_fg.name != 'ISP_graph':
            isp_nf_fg = self.remoteConnection(nf_fg)
        
        Endpoint(nf_fg).characterizeEndpoint(token.get_userID())
    
        return nf_fg, isp_nf_fg

    def prepareProfile(self, token):
        # Retrieve the user profile
        logging.debug('ServiceLayerApplication -  addDeviceToNF_FG - Getting user profile')
        profile = KeystoneProfile(self.keystone_server, token.get_userID())
        self.graph = profile.get(token.get_token())['profile']['graph']
        
        # Transform profile in NF_FG
        nf_fg = ServiceGraph(self.graph).getNF_FG()
        manage = NF_FG_Management(nf_fg, self.token)                

        
        nf_fg, isp_nf_fg = self._prepareProfile(token, nf_fg)
        
        # Add flow that permits to user device to reach his NF-FG  
        if self.user_mac is not None:
            logging.debug('ServiceLayerApplication -  adding device flows ')
            manage.setDeviceFlows(self.user_mac)
        else:
            logging.warning("No mac address for user "+token.get_username())
        
        
       
                            
        return json.loads(nf_fg.getJSON()), isp_nf_fg  
    
    def remoteConnection(self, nf_fg):
        """
        Connect the nf_fg passed with the ISP graph
        """
        # Create endpoint switch
        #endpoint_control_switch = nf_fg.addEndpointSwitch(CONTROL_EGRESS)
        #endpoint_switch = nf_fg.addEndpointSwitch(USER_EGRESS)
        
        # Add one endpoint connected to endpoint_switch
        #edge_control_endpoint =  nf_fg.addEdgeEndpoint(endpoint_control_switch)
        #edge_endpoint = nf_fg.addEdgeEndpoint(endpoint_switch)
        
        # Retrieve isp NF-FG
        self.isp = KeystoneAuthentication(self.keystone_server,ISP_TENANT,ISP_USERNAME, ISP_PASSWORD)
        if UserSession(self.isp.get_userID(), self.isp).checkSession('ISP_graph', self.orchestrator) is True:
            isp_nf_fg = Graph().get_instantiated_nffg(self.isp.get_userID())
            #logging.debug("ISP - \n"+isp_profile.getJSON())
        else:
            raise ISPNotDeployed("ISP NF-FG is not deployed, impossible connect to endpoint of NF-FG not yet deployed")
        
        #edge_control_endpoint.connectToExternalNF_FG(nf_fg, isp_nf_fg, CONTROL_INGRESS)
        #edge_endpoint.connectToExternalNF_FG(nf_fg, isp_nf_fg, ISP_INGRESS)
        update_isp = False
        if nf_fg.getEndpointFromName(CONTROL_EGRESS) is not None:
            if Graph().getGraphConnections() is not None:
                if len(Graph().getGraphConnections(isp_nf_fg.id, CONTROL_EGRESS)) != 0:
                    if len(Graph().getGraphConnections(isp_nf_fg.id, CONTROL_EGRESS)) == 1:
                        # Crate a switch
                        control_endpoint_switch = isp_nf_fg.addEndpointSwitch(CONTROL_EGRESS)
                    else:
                        # Add a port to switch
                        control_endpoint_switch = isp_nf_fg.getVNFConnectedToEndpoint(CONTROL_EGRESS)
                    control_endpoint_port = isp_nf_fg.addPortToSwitch(control_endpoint_switch)
                    update_isp = True
        
        data_endpoint_switch = None
        data_endpoint_port = None
        if nf_fg.getEndpointFromName(USER_EGRESS) is not None:
            if len(Graph().getGraphConnections(isp_nf_fg.id, ISP_INGRESS)) == 0:
                # Crate a switch
                data_endpoint_switch = isp_nf_fg.addEndpointSwitch(ISP_INGRESS)
                data_endpoint_port = data_endpoint_switch.listPort[0]
                
                switch_connection_port = isp_nf_fg.addPortToSwitch(data_endpoint_switch)
                NF_FG_Management(isp_nf_fg).connectEndpointSwitchToVNF(isp_nf_fg.getEndpointFromName(ISP_INGRESS), data_endpoint_switch, switch_connection_port)
            else:
                data_endpoint_switch = isp_nf_fg.getVNFConnectedToEndpoint(ISP_INGRESS)
                
                # TODO: Create a new endpoint
                
                # Add a port to switch    
                data_endpoint_port = isp_nf_fg.addPortToSwitch(data_endpoint_switch)
                
                # TODO: Connect the endpoint to the port just created
                
            update_isp = True
                    
        if update_isp is True:
            #isp_nf_fg = Session().get_instantiated_nffg(self.ISP.get_userID())
            logging.debug("new isp graph:")
            logging.debug(isp_nf_fg.getJSON())
            self.orchestrator.put(json.loads(isp_nf_fg.getJSON()), self.isp.get_token())
            isp_nf_fg = Graph().get_instantiated_nffg(self.isp.get_userID())
            if nf_fg.getEndpointFromName(CONTROL_EGRESS) is not None:
                control_endpoint_switch = isp_nf_fg.getVNFConnectedToEndpoint(isp_nf_fg.getEndpointFromName(CONTROL_INGRESS).id)[0]
            if nf_fg.getEndpointFromName(USER_EGRESS) is not None:
                data_endpoint_switch = isp_nf_fg.getVNFConnectedToEndpoint(isp_nf_fg.getEndpointFromName(ISP_INGRESS).id)[0]           
        
        if nf_fg.getEndpointFromName(CONTROL_EGRESS) is not None:  
            nf_fg.getEndpointFromName(CONTROL_EGRESS).connectToExternalNF_FGWithoutEdgeEndpoint(nf_fg, isp_nf_fg, CONTROL_INGRESS, control_endpoint_switch, control_endpoint_port)
        if nf_fg.getEndpointFromName(USER_EGRESS) is not None:
            nf_fg.getEndpointFromName(USER_EGRESS).connectToExternalNF_FGWithoutEdgeEndpoint(nf_fg, isp_nf_fg, ISP_INGRESS, data_endpoint_switch, data_endpoint_port)

        
        logging.info("After remote connection : "+str(nf_fg.getJSON()))

        return isp_nf_fg
        
