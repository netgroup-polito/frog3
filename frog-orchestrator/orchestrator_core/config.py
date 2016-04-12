'''
Created on Oct 1, 2014

@author: fabiomignini
'''
import ConfigParser, os, inspect
from orchestrator_core.exception import WrongConfigurationFile 


class Configuration(object):
    
    _instance = None
    _AUTH_SERVER = None
    
    def __new__(cls, *args, **kwargs):
        
        if not cls._instance:
            cls._instance = super(Configuration, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance 
    
    def __init__(self):
        #if self._AUTH_SERVER is None:
        self.inizialize()
    
    def inizialize(self): 
        config = ConfigParser.RawConfigParser()
        base_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0])).rpartition('/')[0]
        try:
            if base_folder == "":
                config.read(base_folder+'configuration/orchestrator.conf')
            else:
                config.read(base_folder+'/configuration/orchestrator.conf')
                
            self._LOG_FILE = config.get('log', 'log_file')
            self._VERBOSE = config.getboolean('log', 'verbose')
            self._DEBUG = config.getboolean('log', 'debug')
            self._CONNECTION = config.get('db','connection')
            
            
            self._SWITCH_NAME = [e.strip() for e in config.get('switch', 'switch_l2_name').split(',')]
            self._CONTROL_SWITCH_NAME = [e.strip() for e in config.get('switch', 'switch_l2_control_name').split(',')]
                        
            self._DEBUG_MODE = config.getboolean('orchestrator', 'debug_mode')
            
            self._UNIFY_NUM_ENDPOINTS = config.getint('UniversalNodeCA','number_of_endpoint')
    
            self._ORCH_PORT = config.get('orchestrator','port')
            self._ORCH_IP = config.get('orchestrator','ip')
            self._ORCH_TIMEOUT = config.get('orchestrator','timeout')
            
            self._SWITCH_TEMPLATE = config.get('switch','template')
            self._DEFAULT_PRIORITY = config.get('flowrule', "default_priority")
            self._TEMPLATE_SOURCE = config.get('templates','source')
            self._TEMPLATE_PATH = config.get('templates','path')
            
            # OVS agent     
            if config.has_section('ovs_agent'):
                if config.has_option('ovs_agent', 'endpoint'):
                    self._OVS_ENDPOINT = config.get('ovs_agent','endpoint')       
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
            
            # JOLNET
            if config.has_option('JolnetCA', 'openstack_networks'):
                self._JOLNET_NETWORKS = [e.strip() for e in config.get('JolnetCA', 'openstack_networks').split(',')]
                
        except Exception as ex:
            raise WrongConfigurationFile(str(ex))
    
    @property
    def ORCH_TIMEOUT(self):
        return self._ORCH_TIMEOUT

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
    def INTEGRATION_BRIDGE(self):
        return self._INTEGRATION_BRIDGE
    
    @property
    def OVS_ENDPOINT(self):
        return self._OVS_ENDPOINT
    
    @property
    def JOLNET_NETWORKS(self):
        return self._JOLNET_NETWORKS
    
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

