'''
Created on 16 nov 2015

@author: stefanopetrangeli
'''
import requests, json, logging
from orchestrator_core.config import Configuration
from orchestrator_core.userAuthentication import UserData
from orchestrator_core.controller import UpperLayerOrchestratorController
from orchestrator_core.scheduler import Scheduler
from nffg_library.nffg import NF_FG
from nffg_library.validator import ValidateNF_FG


#in_file = open("/home/stack/Documents/LiClipse Workspace/frog4/grafo0.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog4/grafo0_AR.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog4/grafo1.json","r")
in_file = open("/home/stack/Documents/LiClipse Workspace/frog4/grafo2.json","r")
#in_file = open("/home/stack/Documents/LiClipse Workspace/frog4/grafo3_4vnf.json","r")

nf_fg_file = json.loads(in_file.read())

ValidateNF_FG().validate(nf_fg_file)
nffg = NF_FG()
nffg.parseDict(nf_fg_file)

nffg1, nffg2 = nffg.split(nffg.end_points, nffg.vnfs) # for graph 0,2

# 3
"""
left = []
left.append(nffg.end_points[0])
nffg1, nffg2 = nffg.split(left, nffg.vnfs) # for graph 3
"""
"""
left = []
left.append(nffg.vnfs[0])
left.append(nffg.vnfs[1])
right= []
right.append(nffg.vnfs[2])
right.append(nffg.vnfs[3])
nffg1, nffg2 = nffg.split(left, right) # for graph 3
"""

"""
left = []
left.append(nffg.vnfs[0])
left.append(nffg.vnfs[1])
right= []
right.append(nffg.vnfs[2])
nffg1, nffg2 = nffg.split(left, right) # for graph1 or 3 
"""

print nffg1.getJSON()
print nffg2.getJSON()

nffg1.join(nffg2)
print nffg1.getJSON()
#print nffg2.getJSON()


print 'Job completed'
