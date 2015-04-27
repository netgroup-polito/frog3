'''
Created on Oct 1, 2014

@author: fabiomignini
''''''
Created on 30/mag/2014

@author: fabiomignini
'''
from Orchestrator.ComponentAdapter.Openstack.heat import HeatOrchestrator
from Orchestrator.ComponentAdapter.Unify.unify import UnifyCA
from Common.config import Configuration

import logging




def Schedule(session_id, heat_endpoint, nova_endpoint):
    '''
    Method that create a concrete instance of the orchestrator
    '''
    # TODO: determine the driver we should use
    
    drivers = Configuration().DRIVERS
    drivers = drivers.split(',')
    if drivers[0] == "HeatCA":
        orchestratorCA_instance = HeatOrchestrator(heat_endpoint, nova_endpoint, session_id)
    elif drivers[0] == "UnifiedNode":
        endpoints = Configuration().UNIFY_ENDPOINTS
        endpoints = endpoints.split(',')
        
        if endpoints[0] is not None:
            pass
        else:
            logging.error("No Unify endpoint found")
        if len(endpoints) > 1:
            logging.warning("Only first  unify endpoint is used")
            
        core_port = Configuration().EGRESS_PORT
        if core_port is not None:
            orchestratorCA_instance = UnifyCA(endpoints[0], core_port);
        else: 
            logging.error("No core port defined")
        
    else:
        logging.error("Driver not supported: "+drivers[0])
        #raise an exception
    
    
    if len(drivers) > 1:
        logging.warning("Only first driver is used")
        #raise an exception
        
    return orchestratorCA_instance




def Select(infrastructure, session_id, heat_endpoint = None, nova_endpoint = None):
    # TODO: take, the list of drivers, compare with infrastructure and instantiate when find a match
    if infrastructure['infrastructure']['name'] == 'UnifyCA':
        endpoints = Configuration().UNIFY_ENDPOINTS
        endpoints = endpoints.split(',')
        
        if endpoints[0] is not None:
            pass
        else:
            logging.error("No Unify endpoint found")
        if len(endpoints) > 1:
            logging.warning("Only first  unify endpoint is used")
            
        core_port = Configuration().EGRESS_PORT
        if core_port is not None:
            orchestratorCA_instance = UnifyCA(endpoints[0], core_port);
        else: 
            logging.error("No core port defined")
    if infrastructure['infrastructure']['name'] == 'HeatOrchestrator':
        orchestratorCA_instance = HeatOrchestrator(heat_endpoint, nova_endpoint, session_id)
        
    return orchestratorCA_instance