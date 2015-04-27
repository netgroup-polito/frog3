'''
Created on Oct 1, 2014

@author: fabiomignini
'''

import sys, os, inspect, falcon, logging

from Common.config import Configuration
from ServiceLayerApplication.service_layer_application import Orchestrator
from Orchestrator.orchestrator import UpperLayerOrchestrator
from ServiceLayerApplication.isp import ISP
from Common.exception import Wrong_ISP_Graph, ISPNotDeployed

conf = Configuration()

# set log level
if conf.DEBUG is True:
    log_level = logging.DEBUG
    requests_log = logging.getLogger("requests")
    requests_log.setLevel(logging.WARNING)
elif conf.VERBOSE is True:
    log_level = logging.INFO
    requests_log = logging.getLogger("requests")
    requests_log.setLevel(logging.WARNING)
else:
    log_level = logging.WARNING

#format = '%(asctime)s %(filename)s %(funcName)s %(levelname)s %(message)s'
log_format = '%(asctime)s %(levelname)s %(message)s - %(filename)s'

logging.basicConfig( filename=conf.LOG_FILE, level=log_level, format=log_format, datefmt='%m/%d/%Y %I:%M:%S %p')
logging.debug("Orchestrator Starting")
print "Welcome to the UN orchestrator"

try:
    
    # Instantiate isp stack
    if conf.ISP is True:
        isp = ISP(conf.AUTH_SERVER, conf.ISP_USERNAME, conf.ISP_PASSWORD, conf.ISP_TENANT, conf.ISP_EMAIL, conf.ISP_DESCRIPTION, conf.ISP_ROLE, conf.ORCH_USERNAME,conf.ORCH_PASSWORD,conf.ORCH_TENANT);
        isp.instatiateISP()
        print "ISP deployed"
        logging.info("ISP deployed") 
        
except Wrong_ISP_Graph as err:
    logging.exception(err.message)
    raise falcon.HTTPInternalServerError('Wrong_ISP_Graph',err.message)

except ISPNotDeployed as err:
    logging.exception(err.message)
    raise falcon.HTTPInternalServerError('ISPNotDeployed',err.message)
    
except:
    logging.exception("FATAL ERROR: The UNorchestrator incurred in an unexpected exception")
    logging.exception("FATAL ERROR: The UNorchestrator execution will be stopped")
    raise

    

# Falcon starts
app = falcon.API()
logging.info("Starting Orchestration Server application")

orch = Orchestrator(conf.AUTH_SERVER, conf.ORCH_USERNAME,conf.ORCH_PASSWORD,conf.ORCH_TENANT)
app.add_route('/orchestrator', orch)
app.add_route('/orchestrator/{mac_address}', orch)

upper_layer_API = UpperLayerOrchestrator(conf.AUTH_SERVER,conf.ORCH_USERNAME,conf.ORCH_PASSWORD,conf.ORCH_TENANT)
app.add_route('/NF-FG', upper_layer_API)
app.add_route('/NF-FG/{session_id}', upper_layer_API)


logging.info("Falcon Successfully started")






    
    
