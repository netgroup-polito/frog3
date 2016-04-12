'''
@author: fabiomignini
'''

from __future__ import division

import json
import falcon
import logging
import uuid

from service_layer_application_core.config import Configuration
from service_layer_application_core.sql.session import Session
from service_layer_application_core.sql.user import User
from nffg_library.nffg import NF_FG
from service_layer_application_core.nffg_manager import NFFG_Manager
from service_layer_application_core.common.user_session import UserSession
from service_layer_application_core.common.endpoint import Endpoint
from service_layer_application_core.orchestrator_rest import GlobalOrchestrator
from service_layer_application_core.user_authentication import UserData
from service_layer_application_core.exception import SessionNotFound, ISPNotDeployed

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

DEBUG_MODE = Configuration().DEBUG_MODE

class ServiceLayerController():
    
    orchestrator_ip = Configuration().ORCH_IP
    orchestrator_port = Configuration().ORCH_PORT

    def __init__(self, user_data):
        self.user_data = user_data
        self.orchestrator = GlobalOrchestrator(self.user_data, self.orchestrator_ip, self.orchestrator_port)
    
    def get(self):
        
        session = Session().get_active_user_session(self.user_data.getUserID()) 

        
        status = self.orchestrator.getNFFGStatus(session.service_graph_id)
        logging.debug("Status : "+status['status'])
        if status['status'] == "complete":
            code = falcon.HTTP_201
        else:
            code = falcon.HTTP_202

        logging.debug("Username : "+self.user_data.username+", Resources : "+json.dumps(status))
        
        
        self.response.body = json.dumps(status)
        self.response.status = code    
  
        logging.debug("GET from username: "+self.user_data.username+" completed")
    
    def delete(self, mac_address):
        """
        If there are more active session for specific user a delete become an update
        that erase a mac rule of user, otherwise if there is only one active session for the user
        the nf-fg will be de-instantiated
        """
        # Returns the number of active session for the user, and if exists the session for the requested device
        num_sessions, session = Session().get_active_user_device_session(self.user_data.getUserID(), mac_address, error_aware=False)
        if mac_address is not None:
            logging.debug("Delete access for device: "+str(mac_address)+" of User: "+self.user_data.username)
        else:
            logging.debug("Delete user service graph: "+self.user_data.username)                 
        logging.debug("Number of devices for the user: "+str(num_sessions))
        if num_sessions == 1:            
            # De-instantiate User Profile Graph
            if DEBUG_MODE is False:
                try:
                    self.orchestrator.delete(session.service_graph_id)
                except:
                    Session().set_error(session.id)       
            logging.debug('Deleted profile of user \"'+self.user_data.username+'\"')
            print 'Deleted profile of user "'+self.user_data.username+'"'
            
            # Set the field ended in the table session to the actual datatime
            Session().set_ended(session.id)
        else:
            logging.debug('Delete access for specific device')
            # Get profile from session
            nffg = self.orchestrator.getNFFG(session.service_graph_id)
            logging.debug('Old user profile :'+nffg.getJSON())
            
            #profile_analisis = ProfileAnalisis()
            manager = NFFG_Manager(nffg)
            manager.deleteMacAddressInFlows(mac_address, USER_INGRESS)
            logging.debug('New user profile :'+nffg.getJSON())
            
            if DEBUG_MODE is False:      
                # Call CA for update graph without rule for deleted device
                try:    
                    self.orchestrator.put(nffg)
                except:
                    Session().set_error(session.id)            
            logging.debug('Device deleted "'+mac_address+'" of user "'+self.user_data.username+'"')
            print 'Device deleted "'+mac_address+'" of user "'+self.user_data.username+'"'
        
        if mac_address is not None:
            Session().del_mac_address_in_the_session(mac_address, session.id)
        Session().updateStatus(session.id, 'deleted')
         
    def put(self, mac_address):
        # Get user network function forwarding graph
        service_graph_dict = json.loads(User().getServiceGraph(self.user_data.username))
        nffg = NF_FG()
        nffg.parseDict(service_graph_dict)
        
        # Check if the user have an active session
        if UserSession(self.user_data.getUserID(), self.user_data).checkSession(nffg.id, self.orchestrator) is True:
            # Existent session for this user
            logging.debug('The FG for this user is already instantiated, the FG will be update if it has been modified')
            
            session = Session().get_active_user_session_by_nf_fg_id(nffg.id, error_aware=True)
            session_id = session.id
            Session().updateStatus(session_id, 'updating')
            
            # Manage new device
            if Session().checkDeviceSession(self.user_data.getUserID(), mac_address) is True:
                """
                 A rule for this mac address is already implemented,
                 only an update of the graph is needed 
                 (This update is necessary only if the graph is different from the last instantiated, 
                 but in this moment the graph is always re-instantiated, will be the orchestrator accountable
                 for a smart update of the FG).
                """
                mac_address = None
            
            self.addDeviceToNF_FG(mac_address, nffg)
            
            # Call orchestrator to update NF-FG
            logging.debug('Call orchestrator sending the following NF-FG: '+nffg.getJSON())
            if DEBUG_MODE is False:
                try:
                    self.orchestrator.put(nffg)
                except:
                    Session().set_error(session_id)
            if mac_address is not None:
                logging.debug('Added device "'+mac_address+'" of user "'+self.user_data.username+'"')
                print 'Added device "'+mac_address+'" of user "'+self.user_data.username+'"'
            else:
                logging.debug('User profile updated "'+self.user_data.username+'"')
                print 'User profile updated "'+self.user_data.username+'"'
        else:
            # New session for this user
            logging.debug('Instantiate profile')
            session_id  = uuid.uuid4().hex
            Session().inizializeSession(session_id, self.user_data.getUserID(), nffg.id, nffg.name)
        
            # Manage profile
            logging.debug("User service graph: "+nffg.getJSON())
            self.prepareProfile(mac_address, nffg)  
              
            # Call orchestrator to instantiate NF-FG
            logging.debug('Calling orchestrator sending NF-FG: '+nffg.getJSON())
            print nffg.getJSON()
            if DEBUG_MODE is False:
                try:
                    self.orchestrator.put(nffg)
                except:
                    Session().set_error(session_id)
            logging.debug('Profile instantiated for user "'+self.user_data.username+'"')
            print 'Profile instantiated for user "'+self.user_data.username+'"'
            
        # Set mac address in the session
        if mac_address is not None:
            Session().add_mac_address_in_the_session(mac_address, session_id)
        Session().updateStatus(session_id, 'complete')
        
    def addDeviceToNF_FG(self, mac_address, nffg):
        # Get MAC addresses from previous session
        logging.debug('Get MAC addresses from previous session')
        session_mac_addresses = Session().get_active_user_devices(self.user_data.getUserID())
        mac_addresses = []
        if session_mac_addresses is not None:
            mac_addresses = mac_addresses+session_mac_addresses
        if mac_address is not None:
            logging.debug('new MAC : '+str(mac_address))      
            mac_addresses.append(str(mac_address))
        logging.debug('MAC addresses: '+str(mac_addresses))        
        
        # If the graph is already attached to ISP, we don't have to reconnect it again
        if ISP is True and (nffg.getEndPointsFromName(CONTROL_EGRESS) or nffg.getEndPointsFromName(CONTROL_EGRESS)):
            already_connected = True
        else:
            already_connected = False
        
        self._prepareProfile(nffg, already_connected=already_connected)

        # TODO: I should check the mac address already used in the ingress end point, but then
        # use the new graph to add all the mac (both those old and that new)
        if len(mac_addresses) != 0:
            manager = NFFG_Manager(nffg)
            manager.addDevicesFlows(mac_addresses)
            
    def _prepareProfile(self, nffg, already_connected = False):
        
        manager = NFFG_Manager(nffg)        
        
        # Get INGRESS NF-FG
        logging.debug('Getting INGRESS NF-FG')
        ingress_nf_fg = manager.getIngressNF_FG()
        
        # Attach INGRESS NF_FG to USER_INGESS ENDPOINT
        logging.debug('Attach INGRESS NF_FG to USER_INGESS ENDPOINT')
        #logging.info(ingress_nf_fg.getJSON())
        manager.attachIngressNF_FG(ingress_nf_fg)
                
        # Get EGRESS NF-FG
        logging.debug('Getting EGRESS NF-FG')
        egress_nf_fg =manager.getEgressNF_FG()
        
        # Attach EGRESS NF_FG to USER_EGRESS ENDPOINT
        logging.debug('Attach EGRESS NF_FG to USER_EGRESS ENDPOINT')
        manager.attachEgressNF_FG(egress_nf_fg)

        # Add control network
        logging.debug('Adding controll network')
        for vnf in nffg.vnfs:
            template = self.orchestrator.getTemplate(vnf.vnf_template_location)
            need_control_net, port = manager.checkIfControlNetIsNedeed(vnf, template)
            if need_control_net is True:
                if ISP is True and nffg.name != 'ISP_graph':
                    control_switch = manager.addPortToControlNet(vnf, port.id, CONTROL_EGRESS)
                else:
                    control_switch = manager.addPortToControlNet(vnf, port.id, ISP_EGRESS)
                    
                if nffg.name == 'ISP_graph':                    
                    user_control_egress  = manager.createEndPoint(CONTROL_INGRESS)
                    port = manager.createSwitchPort(control_switch)
                    control_switch.ports.append(port)
                    manager.connectVNFAndEndPoint(vnf_id=control_switch.id, port_id=port.id, end_point_id=user_control_egress.id)
                                        
        # TODO: if end-point is ... then connect to ISP
        # Create connection to another NF-FG
        # TODO: The following row should be executed only if  we want to concatenate ISP to our graphs
        if ISP is True and nffg.name != 'ISP_graph':
            self.remoteConnection(nffg)
            
        manager.mergeUselessVNFs()   
        
        Endpoint(nffg).characterizeEndpoint(User().getUser(self.user_data.username).id)

    def prepareProfile(self, mac_address, nffg):
        # Transform profile in NF_FG
        manager = NFFG_Manager(nffg)                

        
        self._prepareProfile(nffg)
        
        # Add flow that permits to user device to reach his NF-FG  
        if mac_address is not None:
            logging.debug('Adding device flows for mac address: '+str(mac_address))
            manager.setDeviceFlows(mac_address)
        else:
            logging.warning("No mac address for user "+self.user_data.username)
    
    def remoteConnection(self, nffg):
        """
        Connect the nf_fg passed with the ISP graph
        """
        isp_user_data = UserData(usr=ISP_USERNAME, pwd=ISP_PASSWORD, tnt=ISP_TENANT)
        
        try:
            control_egress_endpoint = nffg.getEndPointsFromName(CONTROL_EGRESS)
            if control_egress_endpoint:
                remote_endpoint_id = self.orchestrator.getNFFG(Session().get_profile_id_from_active_user_session(isp_user_data.getUserID())).\
                                            getEndPointsFromName(CONTROL_INGRESS)[0].id
                control_egress_endpoint[0].remote_endpoint_id = Session().get_profile_id_from_active_user_session(isp_user_data.getUserID())\
                    +':'+remote_endpoint_id
            user_egress_endpoint = nffg.getEndPointsFromName(USER_EGRESS)
            if user_egress_endpoint:
                remote_endpoint_id = self.orchestrator.getNFFG(Session().get_profile_id_from_active_user_session(isp_user_data.getUserID())).\
                                            getEndPointsFromName(ISP_INGRESS)[0].id
                user_egress_endpoint[0].remote_endpoint_id = Session().get_profile_id_from_active_user_session(isp_user_data.getUserID())\
                    +':'+remote_endpoint_id
        except SessionNotFound:
            raise ISPNotDeployed("ISP's graph not deployed. By configuration the SLApp try to connect the user service graph to the ISP's graph.")
                
    def deleteRemoteConnections(self):
        raise NotImplementedError()