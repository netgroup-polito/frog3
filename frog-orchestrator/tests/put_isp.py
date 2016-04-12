'''
Created on Nov 4, 2015

@author: fabiomignini
'''
import logging
from orchestrator_core.userAuthentication import UserData
from orchestrator_core.controller import UpperLayerOrchestratorController
from nffg_library.nffg import NF_FG
from nffg_library.validator import ValidateNF_FG


nffg_dict = {"forwarding-graph":{"VNFs":[{"ports":[{"id":"L2Port:0","name":"data-lan"},{"id":"L2Port:1","name":"data-lan"},{"id":"L2Port:2","name":"data-lan"}],"vnf_template":"switch.json","id":"00000001","name":"switch-data"},{"ports":[{"id":"inout:0","name":"data-port"}],"vnf_template":"isp_dhcp.json","id":"00000002","name":"dhcp-isp"},{"ports":[{"id":"inout:0"},{"id":"inout:1"},{"id":"control:0","name":"Control port"}],"vnf_template":"iptraf.json","id":"00000003","name":"iptraf-isp"},{"ports":[{"id":"User:0","name":"data-port"},{"id":"WAN:0","name":"data-port"}],"vnf_template":"isp_nat.json","id":"00000004","name":"nat-isp"},{"ports":[{"id":"L2Port:0","name":"auto-generated-port"},{"id":"L2Port:1","name":"auto-generated-port"},{"id":"L2Port:2","name":"auto-generated-port"}],"vnf_template":"switch.json","id":"b66276124280488193d5efbb9aadfb36","name":"Control_Switch"}],"end-points":[{"type":"internal","id":"00000001","name":"ISP_INGRESS"},{"interface-out":{"node":"130.192.225.193","interface":"em1"},"type":"interface-out","id":"00000002","name":"EGRESS"},{"interface-out":{"node":"130.192.225.193","interface":"em1"},"type":"interface-out","id":"810fc3dc88774973aa80c2d00639431a","name":"EGRESS"},{"type":"internal","id":"9941e6c1ac134dae9113ac93b8d613b2","name":"USER_CONTROL_INGRESS"}],"big-switch":{"flow-rules":[{"priority":1,"actions":[{"output":"vnf:00000001:L2Port:0"}],"id":"000000001","match":{"port_in":"endpoint:00000001"}},{"priority":1,"actions":[{"output":"endpoint:00000001"}],"id":"000000002","match":{"port_in":"vnf:00000001:L2Port:0"}},{"priority":1,"actions":[{"output":"vnf:00000004:WAN:0"}],"id":"000000003","match":{"port_in":"endpoint:00000002"}},{"priority":1,"actions":[{"output":"endpoint:00000002"}],"id":"000000004","match":{"port_in":"vnf:00000004:WAN:0"}},{"priority":1,"actions":[{"output":"vnf:00000002:inout:0"}],"id":"000000005","match":{"port_in":"vnf:00000001:L2Port:1"}},{"priority":1,"actions":[{"output":"vnf:00000001:L2Port:1"}],"id":"000000006","match":{"port_in":"vnf:00000002:inout:0"}},{"priority":1,"actions":[{"output":"vnf:00000003:inout:0"}],"id":"000000007","match":{"port_in":"vnf:00000001:L2Port:2"}},{"priority":1,"actions":[{"output":"vnf:00000001:L2Port:2"}],"id":"000000008","match":{"port_in":"vnf:00000003:inout:0"}},{"priority":1,"actions":[{"output":"vnf:00000004:User:0"}],"id":"000000009","match":{"port_in":"vnf:00000003:inout:1"}},{"priority":1,"actions":[{"output":"vnf:00000003:inout:1"}],"id":"000000010","match":{"port_in":"vnf:00000004:User:0"}},{"priority":200,"actions":[{"output":"vnf:b66276124280488193d5efbb9aadfb36:L2Port:0"}],"id":"9c37f6e7ff8c457aae1f6f0cedc85911","match":{"port_in":"endpoint:810fc3dc88774973aa80c2d00639431a"}},{"priority":200,"actions":[{"output":"endpoint:810fc3dc88774973aa80c2d00639431a"}],"id":"c4b4f43a862940878863f2b719d6d2a2","match":{"port_in":"vnf:b66276124280488193d5efbb9aadfb36:L2Port:0"}},{"priority":200,"actions":[{"output":"vnf:b66276124280488193d5efbb9aadfb36:L2Port:1"}],"id":"178746d675d94b9cbd1bd9186e6a9b0b","match":{"port_in":"vnf:00000003:control:0"}},{"priority":200,"actions":[{"output":"vnf:00000003:control:0"}],"id":"0e63b3aba8e24e02b4092f627a3db21f","match":{"port_in":"vnf:b66276124280488193d5efbb9aadfb36:L2Port:1"}},{"priority":200,"actions":[{"output":"vnf:b66276124280488193d5efbb9aadfb36:L2Port:2"}],"id":"503bc4eeb57b40e3a4d1d7a07463b655","match":{"port_in":"endpoint:9941e6c1ac134dae9113ac93b8d613b2"}},{"priority":200,"actions":[{"output":"endpoint:9941e6c1ac134dae9113ac93b8d613b2"}],"id":"13b506ad2c5d49c8a02c765fa2eed557","match":{"port_in":"vnf:b66276124280488193d5efbb9aadfb36:L2Port:2"}}]},"id":"isp-00000001","name":"ISP_graph"}}
username = 'isp'
password = 'stack'
tenant = 'isp'

logging.basicConfig(level=logging.DEBUG)
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)
sqlalchemy_log = logging.getLogger('sqlalchemy.engine')
sqlalchemy_log.setLevel(logging.WARNING)

ValidateNF_FG().validate(nffg_dict)
nffg = NF_FG()
nffg.parseDict(nffg_dict)

controller = UpperLayerOrchestratorController(user_data=UserData(username, password, tenant))
controller.put(nffg)

print 'Job completed'
exit()