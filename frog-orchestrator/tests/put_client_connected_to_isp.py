'''
Created on Nov 4, 2015

@author: fabiomignini
'''
import logging
from orchestrator_core.userAuthentication import UserData
from orchestrator_core.controller import UpperLayerOrchestratorController
from nffg_library.nffg import NF_FG
from nffg_library.validator import ValidateNF_FG


nffg_dict = {"forwarding-graph":{"VNFs":[{"ports":[{"id":"WAN:0"},{"id":"User:0"},{"id":"control:0","name":"Control port"}],"vnf_template":"firewall-web.json","id":"00000002","name":"firewall"},{"ports":[{"id":"inout:0"}],"vnf_template":"dhcp.json","id":"ingress-00000002","name":"DHCP server"},{"ports":[{"id":"WAN:0","name":"data-lan"},{"id":"User:0","name":"data-lan"}],"vnf_template":"nat.json","id":"egress-00000001","name":"isp-nat"},{"ports":[{"id":"L2Port:0","name":"auto-generated-port"},{"id":"L2Port:1","name":"auto-generated-port"}],"vnf_template":"switch.json","id":"524ecb7cccd441cc87546afc07e6bb3e","name":"Control_Switch"},{"ports":[{"id":"L2Port:0","name":"auto-generated-port"},{"id":"L2Port:1","name":"auto-generated-port"},{"id":"L2Port:2","name":"auto-generated-port"}],"vnf_template":"switch.json","id":"f82a748fa9004084a0cb052707b692d3","name":"Switch"}],"end-points":[{"interface":{"node":"130.192.225.193","interface":"to-br-usr"},"type":"interface","id":"00000001","name":"INGRESS"},{"remote_endpoint_id":"isp-00000001:00000001","type":"internal","id":"00000002","name":"ISP_CONNECTION"},{"remote_endpoint_id":"isp-00000001:9941e6c1ac134dae9113ac93b8d613b2","type":"internal","id":"c29d730b2f49432e82b5d6cbae14923b","name":"USER_CONTROL_EGRESS"}],"big-switch":{"flow-rules":[{"priority":1,"actions":[{"output":"vnf:f82a748fa9004084a0cb052707b692d3:L2Port:2"}],"id":"000000003","match":{"port_in":"vnf:00000002:User:0"}},{"priority":1,"actions":[{"output":"vnf:00000002:User:0"}],"id":"000000004","match":{"port_in":"vnf:f82a748fa9004084a0cb052707b692d3:L2Port:2"}},{"priority":1,"actions":[{"output":"vnf:f82a748fa9004084a0cb052707b692d3:L2Port:0"}],"id":"3bca88b673f64d5ba4013e2091c1890a","match":{"port_in":"endpoint:00000001"}},{"priority":1,"actions":[{"output":"endpoint:00000001"}],"id":"a083f9361dea40128e59d955f77faf58","match":{"port_in":"vnf:f82a748fa9004084a0cb052707b692d3:L2Port:0"}},{"priority":1,"actions":[{"output":"vnf:f82a748fa9004084a0cb052707b692d3:L2Port:1"}],"id":"83a3a89fcf674d14b63047cb6c1f7396","match":{"port_in":"vnf:ingress-00000002:inout:0"}},{"priority":1,"actions":[{"output":"vnf:ingress-00000002:inout:0"}],"id":"d76f978f6f934437b959982ec6ca7a03","match":{"port_in":"vnf:f82a748fa9004084a0cb052707b692d3:L2Port:1"}},{"priority":1,"actions":[{"output":"vnf:00000002:WAN:0"}],"id":"31259c06b6a2434993add836751c2246","match":{"port_in":"vnf:egress-00000001:User:0"}},{"priority":1,"actions":[{"output":"vnf:egress-00000001:User:0"}],"id":"88ea94d3afdc4f81a80aca4c618be2d9","match":{"port_in":"vnf:00000002:WAN:0"}},{"priority":1,"actions":[{"output":"vnf:egress-00000001:WAN:0"}],"id":"a234b7c167ba47b9b26ec7b78f67ba10","match":{"port_in":"endpoint:00000002"}},{"priority":1,"actions":[{"output":"endpoint:00000002"}],"id":"90f372fcdeba40acadd40f85b69eefd8","match":{"port_in":"vnf:egress-00000001:WAN:0"}},{"priority":200,"actions":[{"output":"vnf:524ecb7cccd441cc87546afc07e6bb3e:L2Port:0"}],"id":"b2ff3dbddb724561b46a43733eddfa62","match":{"port_in":"endpoint:c29d730b2f49432e82b5d6cbae14923b"}},{"priority":200,"actions":[{"output":"endpoint:c29d730b2f49432e82b5d6cbae14923b"}],"id":"1d7173b189b64c1d841bce0bdc76a05c","match":{"port_in":"vnf:524ecb7cccd441cc87546afc07e6bb3e:L2Port:0"}},{"priority":200,"actions":[{"output":"vnf:524ecb7cccd441cc87546afc07e6bb3e:L2Port:1"}],"id":"c3501d4a67ad49ffa839898b6e061ab3","match":{"port_in":"vnf:00000002:control:0"}},{"priority":200,"actions":[{"output":"vnf:00000002:control:0"}],"id":"1e7a09b9faef49959cd992cb588cea23","match":{"port_in":"vnf:524ecb7cccd441cc87546afc07e6bb3e:L2Port:1"}}]},"id":"00000001","name":"Protected access to the internet"}}
username = 'demo2'
password = 'stack'
tenant = 'demo2'

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