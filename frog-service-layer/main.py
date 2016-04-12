'''
Created on Oct 1, 2014

@author: fabiomignini
'''

import falcon, logging

from service_layer_application_core.config import Configuration
from service_layer_application_core.service_layer_application import  ServiceLayer

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
print "Welcome to the User-oriented Service Layer Application"

# Falcon starts
app = falcon.API()
logging.info("Starting Service Layer application")

orch = ServiceLayer()
app.add_route('/service-layer', orch)
app.add_route('/service-layer/{mac_address}', orch)




logging.info("Falcon Successfully started")






    
    
