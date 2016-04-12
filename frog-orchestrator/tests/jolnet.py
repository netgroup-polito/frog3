'''
Created on 11 nov 2015

@author: stefanopetrangeli
'''
import requests, json, logging
from orchestrator_core.config import Configuration
from orchestrator_core.userAuthentication import UserData
from orchestrator_core.controller import UpperLayerOrchestratorController
from nffg_library.nffg import NF_FG
from nffg_library.validator import ValidateNF_FG

username = 'AdminPoliTO'
password = 'AdminPoliTO'
tenant = 'PoliTO_chain1'

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

log_format = '%(asctime)s %(levelname)s %(message)s - %(filename)s'

logging.basicConfig( filename=conf.LOG_FILE, level=log_level, format=log_format, datefmt='%m/%d/%Y %I:%M:%S %p')
logging.debug("Orchestrator Starting")

#in_file = open("/home/stack/Documents/LiClipse Workspace/frog3/Orchestrator/Graphs/jolnet_ispHe.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog3/Orchestrator/Graphs/jolnet_ispHe_2endp_2.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog3/Orchestrator/Graphs/jolnet_ispHe_ctrl.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog3/Orchestrator/Graphs/jolnet_isp_addVM.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog3/Orchestrator/Graphs/jolnet_graphHe.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog3/Orchestrator/Graphs/jolnet_graphHe_2_299.json","r")


#in_file = open("/home/stack/Documents/LiClipse Workspace/frog-orchestrator/graphs/jolnet_endp200.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog-orchestrator/graphs/jolnet_endp201.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog-orchestrator/graphs/jolnet_tel_FW_1TN.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog3/Orchestrator/Graphs/jolnet_endp200_he.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog3/Orchestrator/Graphs/jolnet_graphFW2_mgmt.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog3/Orchestrator/Graphs/jolnet_graphFW2_new_he.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog3/Orchestrator/Graphs/jolnet_graphFW2_new_he_2.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog3/Orchestrator/Graphs/jolnet_graphFW2_new_he_3.json","r")


#in_file = open("/home/stack/Documents/LiClipse Workspace/frog3/Orchestrator/Graphs/jolnet_ispHy.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog3/Orchestrator/Graphs/jolnet_isp_addVMHy.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog3/Orchestrator/Graphs/jolnet_graphHy.json","r")

#in_file = open("/home/stack/Documents/LiClipse Workspace/frog3/Orchestrator/Graphs/isp.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog3/Orchestrator/Graphs/nobody.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog3/Orchestrator/Graphs/unify_example.json","r")

in_file = open("/home/stack/Documents/LiClipse Workspace/frog-orchestrator/graphs/jolnet_ispHe_noVLAN.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog-orchestrator/graphs/jolnet_graphHe_2endp_noVLAN.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog-orchestrator/graphs/jolnet_graphHe_2endp_MI_noVLAN.json","r")
in_file = open("/home/stack/Documents/LiClipse Workspace/frog-orchestrator/graphs/jolnet_graphHe_2endp_MI_noVLAN_noRemote.json","r")

#in_file = open("/home/stack/Documents/LiClipse Workspace/frog-orchestrator/graphs/jolnet_graphHe_3endp_PI_noVLAN.json","r")

#in_file = open("/home/stack/Documents/LiClipse Workspace/frog-orchestrator/graphs/jolnet_ispHe_new.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog-orchestrator/graphs/jolnet_graphHe_new_2endp_MI.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog-orchestrator/graphs/jolnet_graphHe_new_2endp_MI_upd.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog-orchestrator/graphs/jolnet_graphHe_new_3endp.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog-orchestrator/graphs/jolnet_prova.json","r")

#in_file = open("/home/stack/Documents/LiClipse Workspace/frog-orchestrator/graphs/jolnet_ispHy.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog-orchestrator/graphs/jolnet_graphHy_2endp_MI.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog-orchestrator/graphs/jolnet_graphHy_2endp_MI_upd.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog-orchestrator/graphs/jolnet_graphHy_3endp.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog-orchestrator/graphs/jolnet_prova2.json","r")
nf_fg_file = json.loads(in_file.read())

ValidateNF_FG().validate(nf_fg_file)
nffg = NF_FG()
nffg.parseDict(nf_fg_file)

controller = UpperLayerOrchestratorController(user_data=UserData(username, password, tenant))
#controller.put(nffg)
#controller.delete(51)
#controller.delete(250)
controller.delete(52)
#controller.delete(200)
#controller.delete(201)

print 'Job completed'
exit()

orchestrator_endpoint = "http://127.0.0.1:9000/NF-FG"
headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 
           'X-Auth-User': username, 'X-Auth-Pass': password, 'X-Auth-Tenant': tenant}
requests.put(orchestrator_endpoint, json.dumps(nf_fg_file), headers=headers)
print 'Job completed'
