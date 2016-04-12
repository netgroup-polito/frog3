'''
Created on Oct 1, 2014

@author: fabiomignini
'''
import ConfigParser, os, inspect


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
        config.read(base_folder+'/configuration/service_layer.conf')
        self._LOG_FILE = config.get('log', 'log_file')
        self._VERBOSE = config.getboolean('log', 'verbose')
        self._DEBUG = config.getboolean('log', 'debug')
        self._CONNECTION = config.get('db','connection')
        self._NOBODY_USERNAME = config.get('nobody','username')
        self._NOBODY_PASSWORD = config.get('nobody','password')
        self._NOBODY_TENANT = config.get('nobody','tenant')
        
        self._ISP_USERNAME = config.get('ISP','username')
        self._ISP_PASSWORD = config.get('ISP','password')
        self._ISP_TENANT = config.get('ISP','tenant')
        
        self._INGRESS_PORT = config.get('user_connection', 'ingress_port')
        self._INGRESS_TYPE = config.get('user_connection', 'ingress_type')
        self._EGRESS_PORT = config.get('user_connection', 'egress_port')
        self._EGRESS_TYPE = config.get('user_connection', 'egress_type')
        
        
        self._SWITCH_NAME = [e.strip() for e in config.get('switch', 'switch_l2_name').split(',')]
        self._CONTROL_SWITCH_NAME = config.get('switch', 'switch_l2_control_name')
        
        self._DEBUG_MODE = config.getboolean('orchestrator', 'debug_mode')

        self._ORCH_PORT = config.get('orchestrator','port')
        self._ORCH_IP = config.get('orchestrator','ip')
        self._ORCH_TIMEOUT = config.get('orchestrator','timeout')
        
        self._FLOW_PRIORITY = config.get('user_connection', 'flow_priority')
        self._SWITCH_TEMPLATE = config.get('switch','template')
        self._DEFAULT_PRIORITY = config.get('flowrule', "default_priority")
        self._INGRESS_GRAPH_FILE = config.get('ingress_nf_fg', "file")
        self._EGRESS_GRAPH_FILE = config.get('engress_nf_fg', "file")
        
        # End-point types
        self._SG_USER_INGRESS = config.get('endpoint_type','sg_user_ingress')
        self._SG_USER_EGRESS = config.get('endpoint_type','sg_user_egress')
        self._USER_INGRESS = config.get('endpoint_type','user_ingress')
        self._USER_EGRESS = config.get('endpoint_type','user_egress')
        self._ISP_INGRESS = config.get('endpoint_type','isp_ingress')
        self._ISP_EGRESS = config.get('endpoint_type','isp_egress')
        self._CONTROL_INGRESS = config.get('endpoint_type','control_ingress')
        self._CONTROL_EGRESS = config.get('endpoint_type','control_egress')
    
        # Orchestrator
        self._ISP = config.getboolean('orchestrator', 'isp')
        self._NOBODY = config.getboolean('orchestrator', 'nobody')
    
    @property
    def ORCH_TIMEOUT(self):
        return self._ORCH_TIMEOUT
    
    @property
    def ISP(self):
        return self._ISP
    
    @property
    def NOBODY(self):
        return self._NOBODY
        
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
    def EGRESS_PORT(self):
        return self._EGRESS_PORT
    
    @property
    def EGRESS_TYPE(self):
        return self._EGRESS_TYPE
    
    @property
    def INGRESS_TYPE(self):
        return self._INGRESS_TYPE   
    
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
    def FLOW_PRIORITY(self):
        return self._FLOW_PRIORITY
    
    @property
    def ORCH_IP(self):
        return self._ORCH_IP
    
    @property
    def ORCH_PORT(self):
        return self._ORCH_PORT
        
    @property
    def INGRESS_PORT(self):
        return self._INGRESS_PORT
    
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
    def LOG_FILE(self):
        return self._LOG_FILE

    @property
    def VERBOSE(self):
        return self._VERBOSE

    @property
    def DEBUG(self):
        return self._DEBUG
