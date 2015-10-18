'''
Created on Oct 1, 2014

@author: fabiomignini
'''

import sys, os, inspect, falcon, logging

from Common.config import Configuration
from Orchestrator.orchestrator import UpperLayerOrchestrator, TemplateAPI, YANGAPI
from Common.exception import Wrong_ISP_Graph, ISPNotDeployed

conf = Configuration()

# set log level
if conf.DEBUG is True:
    log_level = logging.DEBUG
    requests_log = logging.getLogger("requests")
    requests_log.setLevel(logging.WARNING)
    sqlalchemy_log = logging.getLogger('sqlalchemy.engine')
    sqlalchemy_log.setLevel(logging.WARNING)
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
    

# Falcon starts
app = falcon.API()
logging.info("Starting Orchestration Server application")

#upper_layer_API = UpperLayerOrchestrator(conf.AUTH_SERVER,conf.ORCH_USERNAME,conf.ORCH_PASSWORD,conf.ORCH_TENANT)
#template = TemplateAPI(conf.AUTH_SERVER,conf.ORCH_USERNAME,conf.ORCH_PASSWORD,conf.ORCH_TENANT)
#yang = YANGAPI(conf.AUTH_SERVER,conf.ORCH_USERNAME,conf.ORCH_PASSWORD,conf.ORCH_TENANT)

upper_layer_API = UpperLayerOrchestrator()
template = TemplateAPI()
yang = YANGAPI()

app.add_route('/NF-FG', upper_layer_API)
app.add_route('/NF-FG/{nffg_id}', upper_layer_API)
app.add_route('/template/{image_id}', template)
app.add_route('/yang/{image_id}', yang)


logging.info("Falcon Successfully started")






    
    
