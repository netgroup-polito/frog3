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
from Orchestrator.controller import UpperLayerOrchestratorController
from Common.config import Configuration
from Common.SQL.session import update_session, get_active_user_session, add_mac_address_in_the_session, get_active_user_device_session, set_ended,get_instantiated_profile,checkDeviceSession, del_mac_address_in_the_session
from Common.authentication import KeystoneAuthentication 
from Common.ServiceGraph.keystone import KeystoneProfile
from Common.users import User
from Common.NF_FG.nf_fg import NF_FG
from Common.NF_FG.nf_fg_managment import NF_FG_Management
from Common.ServiceGraph.service_graph import ServiceGraph
from Common.exception import ISPNotDeployed, NoMacAddress
from Orchestrator.scheduler import Select
from ServiceLayerApplication.common.user_session import UserSession
from ServiceLayerApplication.common.endpoint import Endpoint
from Orchestrator import scheduler

ISP = Configuration().ISP
ISP_USERNAME = Configuration().ISP_USERNAME
ISP_PASSWORD = Configuration().ISP_PASSWORD
ISP_TENANT = Configuration().ISP_TENANT
# End-points type
USER_EGRESS = Configuration().USER_EGRESS
CONTROL_EGRESS = Configuration().CONTROL_EGRESS
ISP_INGRESS = Configuration().ISP_INGRESS
CONTROL_INGRESS = Configuration().CONTROL_INGRESS

INGRESS_PORT = Configuration().INGRESS_PORT
INGRESS_TYPE = Configuration().INGRESS_TYPE
EGRESS_PORT = Configuration().EGRESS_PORT
EGRESS_TYPE = Configuration().EGRESS_TYPE
ISP_EGRESS = Configuration().ISP_EGRESS
USER_INGRESS = Configuration().USER_INGRESS


class OrchestratorController():
    '''
    '''
    def __init__(self, keystone_server, OrchestratorToken, method, response, request, keystone, mac_address = None):
        #logging.debug('OrchestratorController - init - begin')
        
        self.keystone = keystone
        self.keystone_server = keystone_server
        self.response = response
        self.orchToken = OrchestratorToken
        self.request = request
        session_flag = False
        self.nobody_flag = False
        
        if request is not None:
            # TODO: DELETE should take the MAC of device
            #if method != "GET" and method !="DELETE":
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
        token = request.get_header("X-Auth-Token")
        if token is None:
            description = "{\"error\":{\"message\":\"Please provide an auth token\",\"code\":\"401\",\"title\":\"Unauthorized\"}}"            
            raise falcon.HTTPUnauthorized('Auth token required',
                                          description,
                                          href='http://docs.example.com/auth')
        self.token = token
        
        self.controller = UpperLayerOrchestratorController(self.keystone_server, self.orchToken, "ServiceLayerApplication", self.token)

    """    
        TODO: should be moved in HeatCA
    """
    def resourcesStatusStat(self, resources):
        num_resources = len(resources['resources'])
        num_resources_completed = 0
        resourcesStat = {}
        resourcesStat['resources'] = []
        for resource in resources['resources']:
            resourcesStat['resources'].append({"resource_name":resource['resource_name'], "resource_status" : resource['resource_status']})
            if resource['resource_status'] == "CREATE_COMPLETE":
                num_resources_completed = num_resources_completed + 1
        percentage_completed = num_resources_completed/num_resources*100
        resourcesStat['percentage_completed'] = percentage_completed
        return resourcesStat
 
    def get(self):
        #getStackStatus(self.token)
        logging.debug("Authenticating the user - GET");
        token = KeystoneAuthentication(self.keystone_server,user_token=self.token, orch_token=self.orchToken)
        
        nf_fg_session = get_active_user_session(token.get_userID()) 
        orchestrator = scheduler.Select(json.loads(nf_fg_session.infrastructure), nf_fg_session.id, token.get_endpoints("orchestration"), token.get_endpoints("compute"))
        
        profile = get_instantiated_profile(token.get_userID())
        profile = json.loads(profile)
        nf_fg = NF_FG(profile)
        
        status = orchestrator.getStackStatus(self.token, nf_fg.name)
        logging.debug("Status : "+status);
        if status == "CREATE_COMPLETE":
            code = falcon.HTTP_201
        else:
            code = falcon.HTTP_202
        
        resources = orchestrator.getStackResourcesStatus(self.token, nf_fg.name)
        resources = self.resourcesStatusStat(resources)
        resources['status'] = status
        logging.debug("Username : "+token.get_username()+", Resources : "+json.dumps(resources))
        
        
        self.response.body = json.dumps(resources)
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
        
        num_sessions, session = get_active_user_device_session(token.get_userID(), self.user_mac) 
        #num_sessions, session = get_active_user_device_session(token.get_userID())
        
        
        #UpperLayerOrchestratorController 
        logging.debug("Number of session for the user: "+str(num_sessions))
        

        if num_sessions == 1:
            # De-instantiate User Profile Graph
            self.controller.delete(session.id)
            logging.debug('Deinstantiate profile - user \"'+token.get_username()+'\" - Success')
            print 'ServiceLayerApplication - DELETE - User "'+token.get_username()+'"'
            
            # Set the field ended in the table session to the actual datatime
            #set_ended(session.id)
        else:
            logging.debug('Delete access for specific device')
            # Get profile from session
            old_profile = get_instantiated_profile(token.get_userID())
            logging.debug('old_profile :'+old_profile)
            old_profile = json.loads(old_profile)
            
            #profile_analisis = ProfileAnalisis()
            manage = NF_FG_Management(NF_FG(old_profile))
            new_nf_fg = manage.deleteMacAddressInFlows(self.user_mac, USER_INGRESS)
            logging.debug('new_nf_fg :'+new_nf_fg.getJSON())
            
            
            #new_profile = profile_analisis.deleteMacAddressInFlows(old_profile, self.user_mac)
            
            
                    
            # Call CA for update graph without rule for deleted device
            self.controller.update(new_nf_fg, True)
            #updateProfile(new_nf_fg._id,json.dumps(new_nf_fg.getJSON()))  
            
            # Set the field ended in the table session to the actual datatime
            del_mac_address_in_the_session(self.user_mac, session.id)
            
            logging.debug('ServiceLayerApplication - DELETE - Device deleted "'+self.user_mac+'" of user "'+token.get_username()+'"')
            print 'ServiceLayerApplication - DELETE - Device deleted "'+self.user_mac+'" of user "'+token.get_username()+'"'
            
     
    def update(self):
        pass
 
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
        
        
        # Check if the user have an active session
        logging.debug('ServiceLayerApplication - PUT - Checking session ')
        if UserSession(token.get_userID(), token).checkSession() is True:
            # Existent session for this user
            
            logging.debug('ServiceLayerApplication - PUT - Add device')
            
            # Manage new device
            if self.user_mac is not None:
                new_profile = self.addDeviceToNF_FG(token)
            else:
                logging.error("No mac address for user "+token.get_username())
                raise NoMacAddress("No mac address for user "+token.get_username())
            
            
            # Call orchestrator to update NF-FG
            logging.debug('ServiceLayerApplication - PUT - Calling orchestrator sending NF-FG')
            logging.debug("\n"+json.dumps(new_profile))
            session_id = self.controller.put(new_profile)
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
            self.nf_fg, isp_nf_fg = self.prepareProfile(token)  
            if isp_nf_fg is not None:
                self.updateISP(isp_nf_fg)  
            
            # Call orchestrator to instantiate NF-FG
            logging.debug('ServiceLayerApplication - PUT - Calling orchestrator sending NF-FG')
            logging.debug("\n"+json.dumps(self.nf_fg))
            session_id = self.controller.put(self.nf_fg)
            logging.debug('ServiceLayerApplication - PUT - Profile instantiated for user "'+token.get_username()+'"')
            print 'ServiceLayerApplication - PUT - Profile instantiated for user "'+token.get_username()+'"'
            
        # Set mac address in the session
        if self.user_mac is not None:
            add_mac_address_in_the_session(self.user_mac, session_id)
            
    def updateISP(self, isp_nf_fg):
        nf_fg_session = get_active_user_session(self.ISP.get_userID()) 
        
        logging.debug(self.ISP.get_endpoints("orchestration"))
        orchestrator = Select(json.loads(nf_fg_session.infrastructure), nf_fg_session.id, self.keystone.get_endpoints("orchestration"), self.keystone.get_endpoints("compute"))
        
        #orchestrator.updateProfile(self.nf_fg, old_profile)
        
        update_session(isp_nf_fg._id,
                       isp_nf_fg.getJSON(),
                       json.dumps({"infrastructure":{"name":type(orchestrator).__name__,"module": type(orchestrator).__module__}}))
        
    def addDeviceToNF_FG(self, token):
        
        # If the mac address passed is already involved in an active session (both in his active session, or in all active session?), throw an exception
        if checkDeviceSession(token.get_userID(), self.user_mac) is True:
            logging.debug('ServiceLayerApplication -  addDeviceToNF_FG - User: '+str(token.get_username())+' already have an active session with this device')
            raise falcon.HTTPConflict("Conflict", "There are already an active session for this user's device")
               
        # Get nf-fg from session
        logging.debug('ServiceLayerApplication -  addDeviceToNF_FG - Getting instantiated NF-FG')
        old_profile = get_instantiated_profile(token.get_userID())
        logging.debug('\n'+old_profile)
        old_profile = json.loads(old_profile)      
        
        # Retrieve the user profile
        logging.debug('ServiceLayerApplication -  addDeviceToNF_FG - Getting user profile')
        profile = KeystoneProfile(self.keystone_server, token.get_userID())
        self.graph = profile.get(token.get_token())['profile']['graph']
        logging.debug('\n'+json.dumps(self.graph))

        # Add device specific rules
        logging.debug('ServiceLayerApplication -  addDeviceToNF_FG - Adding device specific rules')
        old_nf_fg = NF_FG(old_profile)
        nf_fg = copy.deepcopy(old_nf_fg)
        manage_nf_fg = NF_FG_Management(nf_fg, self.token)
        manage_nf_fg.addDeviceFlows(self.user_mac)
        
            
        return json.loads(nf_fg.getJSON())

    def prepareProfile(self, token):
        # Retrieve the user profile
        logging.debug('ServiceLayerApplication -  addDeviceToNF_FG - Getting user profile')
        profile = KeystoneProfile(self.keystone_server, token.get_userID())
        self.graph = profile.get(token.get_token())['profile']['graph']
        
        # Transform profile in NF_FG
        nf_fg = ServiceGraph(self.graph).getNF_FG()
        manage = NF_FG_Management(nf_fg, self.token)        
        
        # Get INGRESS NF-FG
        logging.debug('ServiceLayerApplication -  addDeviceToNF_FG - Getting INGRESS NF-FG')
        ingress_nf_fg = manage.getIngressNF_FG()
        
        # Attach INGRESS NF_FG to USER_INGESS ENDPOINT
        logging.debug('ServiceLayerApplication -  addDeviceToNF_FG - Attach INGRESS NF_FG to USER_INGESS ENDPOINT')
        #logging.info(ingress_nf_fg.getJSON())
        manage.attachIngressNF_FG(ingress_nf_fg)
                
        # Get EGRESS NF-FG
        logging.debug('ServiceLayerApplication -  addDeviceToNF_FG - Getting EGRESS NF-FG')
        egress_nf_fg =manage.getEgressNF_FG()
        
        # Attach EGRESS NF_FG to USER_EGRESS ENDPOINT
        logging.debug('ServiceLayerApplication -  addDeviceToNF_FG - Attach EGRESS NF_FG to USER_EGRESS ENDPOINT')
        manage.attachEgressNF_FG(egress_nf_fg)
        
        # Add control network
        logging.debug('ServiceLayerApplication -  addDeviceToNF_FG - Adding controll network')
        for vnf in nf_fg.listVNF:
            #logging.info("Control vnf : "+vnf.name)
            need_control_net, port = manage.checkIfControlNetIsNedeed(vnf)
            #logging.info("Control port")
            if need_control_net is True:
                #logging.info(port.id)
                manage.addToControlNet(vnf, port)
            #logging.info("")
        
        # Add flow that permits to user device to reach his NF-FG  
        if self.user_mac is not None:
            logging.debug('ServiceLayerApplication -  adding device flows ')
            manage.setDeviceFlows(self.user_mac)
        else:
            logging.warning("No mac address for user "+token.get_username())
        
        
        # TODO: if endpoint is ... then connect tu ISP
        # Create connection to another NF-FG
        isp_nf_fg = None
        # TODO: The following row should be executed only if  we want to concatenate ISP to our graphs
        if ISP is True:
            isp_nf_fg = self.remoteConnection(nf_fg)
        
        Endpoint(nf_fg).characterizeEndpoint()
                            
        logging.info(nf_fg.getJSON())
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
        self.ISP = KeystoneAuthentication(self.keystone_server,ISP_TENANT,ISP_USERNAME, ISP_PASSWORD)
        if UserSession(self.ISP.get_userID(), self.ISP).checkSession() is True:
            isp_profile = get_instantiated_profile(self.ISP.get_userID())
            logging.debug("ISP - \n"+isp_profile)
            isp_profile = json.loads(isp_profile) 
            isp_nf_fg = NF_FG(isp_profile)
        else:
            raise ISPNotDeployed("ISP NF-FG is not deployed, impossible connect to endpoint of NF-FG not yet deployed")
        
        #edge_control_endpoint.connectToExternalNF_FG(nf_fg, isp_nf_fg, CONTROL_INGRESS)
        #edge_endpoint.connectToExternalNF_FG(nf_fg, isp_nf_fg, ISP_INGRESS)
        
        if nf_fg.getEndpointFromName(CONTROL_EGRESS) is not None:
            nf_fg.getEndpointFromName(CONTROL_EGRESS).connectToExternalNF_FGWithoutEdgeEndpoint(nf_fg, isp_nf_fg, CONTROL_INGRESS)
        if nf_fg.getEndpointFromName(USER_EGRESS) is not None:
            nf_fg.getEndpointFromName(USER_EGRESS).connectToExternalNF_FGWithoutEdgeEndpoint(nf_fg, isp_nf_fg, ISP_INGRESS)

        
        logging.info("ECCO : "+str(nf_fg.getJSON()))

        return isp_nf_fg
    
    
        # Instantiate ISP 
        # TODO: I should move this after user NF-FG instantiation
        # TODO: WARNING is not really needed for unifyCA, instead for heatCA???
        #controller = UpperLayerOrchestratorController(self.keystone_server, self.orchToken,"ISP", ISP.get_token())
        #controller.put(json.loads(isp_nf_fg.getJSON()))
        
