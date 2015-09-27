'''
Created on Oct 1, 2014

@author: fabiomignini
'''
import ConfigParser, os, inspect
from Common.exception import  WrongConfigurationFile


class Configuration(object):
    
    _instance = None
    _AUTH_SERVER = None
    
    def __new__(cls, *args, **kwargs):
        
        if not cls._instance:
            cls._instance = super(Configuration, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance 
    
    def __init__(self):
        if self._AUTH_SERVER is None:
            self.inizialize()
    
    def inizialize(self): 
        config = ConfigParser.RawConfigParser()
        base_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0])).rpartition('/')[0]
        config.read(base_folder+'/Configuration/orchestrator.conf')
        self._AUTH_SERVER = config.get('authentication', 'server')
        self._ORCH_USERNAME = config.get('authentication', 'orch_username')
        self._ORCH_PASSWORD = config.get('authentication', 'orch_password')
        self._ORCH_TENANT = config.get('authentication', 'orch_tenant')        
        self._ADMIN_TENANT_NAME = config.get('authentication', 'admin_tenant_name')
        self._ADMIN_USER = config.get('authentication', 'admin_user')
        self._ADMIN_PASSWORD = config.get('authentication', 'admin_password')
        self._LOG_FILE = config.get('log', 'log_file')
        self._VERBOSE = config.getboolean('log', 'verbose')
        self._DEBUG = config.getboolean('log', 'debug')
        self._CONNECTION = config.get('db','connection')
        self._NOBODY_USERNAME = config.get('nobody','username')
        self._NOBODY_PASSWORD = config.get('nobody','password')
        self._NOBODY_TENANT = config.get('nobody','tenant')
        self._NOBODY_EMAIL = config.get('nobody','email')
        self._NOBODY_DESCRIPTION = config.get('nobody','description')
        self._NOBODY_ROLE = config.get('nobody','role')
        
        self._ISP_GRAPH_FILE = config.get('ISP','file')
        self._ISP_USERNAME = config.get('ISP','username')
        self._ISP_PASSWORD = config.get('ISP','password')
        self._ISP_TENANT = config.get('ISP','tenant')
        self._ISP_EMAIL = config.get('ISP','email')
        self._ISP_DESCRIPTION = config.get('ISP','description')
        self._ISP_ROLE = config.get('ISP','role')
        
        self._INGRESS_PORT = config.get('user_connection', 'ingress_port')
        self._INGRESS_TYPE = config.get('user_connection', 'ingress_type')
        self._EGRESS_PORT = config.get('user_connection', 'egress_port')
        self._EGRESS_TYPE = config.get('user_connection', 'egress_type')
        
        
        self._SWITCH_NAME = config.get('switch', 'switch_l2_name')
        self._CONTROL_SWITCH_NAME = config.get('switch', 'switch_l2_control_name')
        
        self._DRIVERS = config.get('drivers', 'drivers')
        
        self._DEBUG_MODE = config.getboolean('orchestrator', 'debug_mode')
        
        
        self._UNIFY_ENDPOINTS = config.get('UniversalNodeCA', 'endpoints')
        self._UNIFY_NUM_ENDPOINTS = config.getint('UniversalNodeCA','number_of_endpoint')

        self._SW_ENDPOINT = config.get('nobody', 'sw_endpoint')
        self._ORCH_PORT = config.get('orchestrator','port')
        self._ORCH_IP = config.get('orchestrator','ip')
        self._ORCH_TIMEOUT = config.get('orchestrator','timeout')
        
        self._FLOW_PRIORITY = config.get('user_connection', 'flow_priority')
        self._MAXIMUM_NUMBER_OF_VNF_IN_GRAPH = config.get('constraints','maximum_number_of_vnf_in_graph')
        self._SWITCH_TEMPLATE = config.get('switch','template')
        self._DEFAULT_PRIORITY = config.get('flowrule', "default_priority")
        self._INGRESS_GRAPH_FILE = config.get('ingress_nf_fg', "file")
        self._EGRESS_GRAPH_FILE = config.get('engress_nf_fg', "file")
        self._TEMPLATE_SOURCE = config.get('templates','source')
        self._TEMPLATE_PATH = config.get('templates','path')
        
        # End-point types
        self._SG_USER_INGRESS = config.get('endpoint_type','sg_user_ingress')
        self._SG_USER_EGRESS = config.get('endpoint_type','sg_user_egress')
        self._USER_INGRESS = config.get('endpoint_type','user_ingress')
        self._USER_EGRESS = config.get('endpoint_type','user_egress')
        self._ISP_INGRESS = config.get('endpoint_type','isp_ingress')
        self._ISP_EGRESS = config.get('endpoint_type','isp_egress')
        self._CONTROL_INGRESS = config.get('endpoint_type','control_ingress')
        self._CONTROL_EGRESS = config.get('endpoint_type','control_egress')
        
        # OVS agent     
        if config.has_section('ovs_agent'):
            if config.has_option('ovs_agent', 'endpoint'):
                self._OVS_ENDPOINT = config.get('ovs_agent','endpoint')
            
        
        # ODL
        self._ODL_VERSION = config.get('odl','version')
        self._ODL_ENDPOINT = config.get('odl','endpoint')
        self._ODL_USER = config.get('odl', 'odl_user')
        self._ODL_PASS = config.get('odl', 'odl_password')
        
        if config.has_option('odl', 'integration_bridge'):
            self._INTEGRATION_BRIDGE = config.get('odl','integration_bridge')
        if config.has_option('odl', 'exit_switch'):
            self._EXIT_SWITCH = config.get('odl','exit_switch')
        if config.has_option('odl', 'ingress_switch'):
            self._INGRESS_SWITCH = config.get('odl','ingress_switch')
        if config.has_option('odl', 'timeout'):
            self._TIMEOUT_ODL = config.get('odl','timeout')
        else:
            self._TIMEOUT_ODL = 10
        
        # HEAT
        if config.has_option('heat', 'timeout'):
            self._TIMEOUT_HEAT = config.get('heat','timeout')
        else:
            self._TIMEOUT_HEAT = 10
            
        # GLANCE
        if config.has_option('glace', 'timeout'):
            self._TIMEOUT_GLANCE = config.get('glace','timeout')
        else:
            self._TIMEOUT_GLANCE = 10
            
        # NOVA
        if config.has_option('nova', 'timeout'):
            self._TIMEOUT_NOVA = config.get('nova','timeout')
        else:
            self._TIMEOUT_NOVA = 10
            
        # Orchestrator
        self._ISP = config.getboolean('orchestrator', 'isp')
        self._NOBODY = config.getboolean('orchestrator', 'nobody')
    
    @property
    def ORCH_TIMEOUT(self):
        return self._ORCH_TIMEOUT
    
    @property
    def ODL_VERSION(self):
        return self._ODL_VERSION
    
    @property
    def ODL_ENDPOINT(self):
        return self._ODL_ENDPOINT
    
    @property
    def ODL_USER(self):
        return self._ODL_USER
    
    @property
    def ODL_PASSWORD(self):
        return self._ODL_PASS

    @property
    def TIMEOUT_NOVA(self):
        return self._TIMEOUT_NOVA
    
    @property
    def TIMEOUT_GLANCE(self):
        return self._TIMEOUT_GLANCE
    
    @property
    def TIMEOUT_HEAT(self):
        return self._TIMEOUT_HEAT

    
    @property
    def TIMEOUT_ODL(self):
        return self._TIMEOUT_ODL
        
    @property
    def EXIT_SWITCH(self):
        return self._EXIT_SWITCH
    
    @property
    def INGRESS_SWITCH(self):
        return self._INGRESS_SWITCH
    
    @property
    def ISP(self):
        return self._ISP
    
    @property
    def NOBODY(self):
        return self._NOBODY
    
    @property
    def INTEGRATION_BRIDGE(self):
        return self._INTEGRATION_BRIDGE
    
    @property
    def OVS_ENDPOINT(self):
        return self._OVS_ENDPOINT
        
    @property
    def SG_USER_INGRESS(self):
        return self._SG_USER_INGRESS
    
    @property
    def SG_USER_EGRESS(self):
        return self._SG_USER_EGRESS
    
    @property
    def USER_INGRESS(self):
        return self._USER_INGRESS
    
    @property
    def USER_EGRESS(self):
        return self._USER_EGRESS
    
    @property
    def ISP_INGRESS(self):
        return self._ISP_INGRESS
    
    @property
    def ISP_EGRESS(self):
        return self._ISP_EGRESS
    
    @property
    def CONTROL_INGRESS(self):
        return self._CONTROL_INGRESS
    
    @property
    def CONTROL_EGRESS(self):
        return self._CONTROL_EGRESS
    
    @property
    def DEBUG_MODE(self):
        return self._DEBUG_MODE
    
    @property
    def CONTROL_SWITCH_NAME(self):
        return self._CONTROL_SWITCH_NAME
    
    @property
    def SWITCH_NAME(self):
        return self._SWITCH_NAME
    
    @property
    def TEMPLATE_SOURCE(self):
        return self._TEMPLATE_SOURCE
    
    @property
    def TEMPLATE_PATH(self):
        return self._TEMPLATE_PATH
    
    @property
    def EGRESS_PORT(self):
        return self._EGRESS_PORT
    
    @property
    def EGRESS_TYPE(self):
        return self._EGRESS_TYPE
    
    @property
    def INGRESS_TYPE(self):
        return self._INGRESS_TYPE   
        
    @property
    def UNIFY_NUM_ENDPOINTS(self):
        return self._UNIFY_NUM_ENDPOINTS
    
    @property
    def ISP_GRAPH_FILE(self):
        return self._ISP_GRAPH_FILE
    
    @property
    def ISP_ROLE(self):
        return self._ISP_ROLE
    
    @property
    def ISP_DESCRIPTION(self):
        return self._ISP_DESCRIPTION

    @property
    def ISP_EMAIL(self):
        return self._ISP_EMAIL
    
    @property
    def ISP_USERNAME(self):
        return self._ISP_USERNAME
    
    @property
    def ISP_PASSWORD(self):
        return self._ISP_PASSWORD
    
    @property 
    def ISP_TENANT(self):
        return self._ISP_TENANT  
    
    @property
    def EGRESS_GRAPH_FILE(self):
        return self._EGRESS_GRAPH_FILE 
    
    @property
    def INGRESS_GRAPH_FILE(self):
        return self._INGRESS_GRAPH_FILE 
     
    @property
    def DEFAULT_PRIORITY(self):
        return self._DEFAULT_PRIORITY
    
    @property
    def SWITCH_TEMPLATE(self):
        return self._SWITCH_TEMPLATE
        
    @property
    def MAXIMUM_NUMBER_OF_VNF_IN_GRAPH(self):
        return self._MAXIMUM_NUMBER_OF_VNF_IN_GRAPH
        
    @property
    def FLOW_PRIORITY(self):
        return self._FLOW_PRIORITY
    
    @property
    def ORCH_IP(self):
        return self._ORCH_IP
    
    @property
    def ORCH_PORT(self):
        return self._ORCH_PORT
    
    @property
    def SW_ENDPOINT(self):
        return self._SW_ENDPOINT
    

    
    @property
    def UNIFY_ENDPOINTS(self):
        return self._UNIFY_ENDPOINTS
    
    @property
    def DRIVERS(self):
        return self._DRIVERS
    
    @property
    def ADMIN_TENANT_NAME(self):
        return self._ADMIN_TENANT_NAME
    
    @property
    def ADMIN_USER(self):
        return self._ADMIN_USER
    
    @property
    def ADMIN_PASSWORD(self):
        return self._ADMIN_PASSWORD    
        
    @property
    def INGRESS_PORT(self):
        return self._INGRESS_PORT
        
    @property
    def NOBODY_ROLE(self):
        return self._NOBODY_ROLE
    
    @property
    def NOBODY_DESCRIPTION(self):
        return self._NOBODY_DESCRIPTION

    @property
    def NOBODY_EMAIL(self):
        return self._NOBODY_EMAIL
    
    @property
    def NOBODY_USERNAME(self):
        return self._NOBODY_USERNAME
    
    @property
    def NOBODY_PASSWORD(self):
        return self._NOBODY_PASSWORD
    
    @property 
    def NOBODY_TENANT(self):
        return self._NOBODY_TENANT  
        
    @property
    def CONNECTION(self):
        return self._CONNECTION
        
    @property
    def AUTH_SERVER(self):
        return self._AUTH_SERVER

    @property
    def ORCH_USERNAME(self):
        return self._ORCH_USERNAME
    
    @property
    def ORCH_PASSWORD(self):
        return self._ORCH_PASSWORD
    
    @property
    def ORCH_TENANT(self):
        return self._ORCH_TENANT

    @property
    def LOG_FILE(self):
        return self._LOG_FILE

    @property
    def VERBOSE(self):
        return self._VERBOSE

    @property
    def DEBUG(self):
        return self._DEBUG

