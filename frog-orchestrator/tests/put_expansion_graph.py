'''
Created on Oct 23, 2015

@author: fabiomignini
'''
import requests, json, logging
from orchestrator_core.userAuthentication import UserData
from orchestrator_core.controller import UpperLayerOrchestratorController
from nffg_library.nffg import NF_FG
from nffg_library.validator import ValidateNF_FG

nffg_dict = {"forwarding-graph":{"VNFs":[{"ports":[{"id":"WAN:0"},{"id":"User:0"},{"id":"control:0","name":"Control port"}],"vnf_template":"firewall-web.json","id":"00000002","name":"firewall"},{"ports":[{"id":"inout:0"}],"vnf_template":"dhcp.json","id":"ingress-00000002","name":"DHCP server"},{"ports":[{"id":"WAN:0","name":"data-lan"},{"id":"User:0","name":"data-lan"}],"vnf_template":"nat.json","id":"egress-00000001","name":"isp-nat"},{"ports":[{"id":"L2Port:0","name":"auto-generated-port"},{"id":"L2Port:1","name":"auto-generated-port"}],"vnf_template":"switch.json","id":"50b50202247e43699e3d79916de711fb","name":"Control_Switch"},{"ports":[{"id":"L2Port:0","name":"auto-generated-port"},{"id":"L2Port:1","name":"auto-generated-port"},{"id":"L2Port:2","name":"auto-generated-port"}],"vnf_template":"switch.json","id":"c776f519aec7486fbf86cb1885af5caf","name":"Switch"}],"end-points":[{"interface":{"node":"130.192.225.193","interface":"to-br-usr"},"type":"interface","id":"00000001","name":"INGRESS"},{"type":"internal","id":"00000002","name":"ISP_CONNECTION"},{"interface-out":{"node":"130.192.225.193","interface":"em1"},"type":"interface-out","id":"dde8196f8c254faa9d24fbbce6ffd55d","name":"EGRESS"}],"big-switch":{"flow-rules":[{"priority":1,"actions":[{"output":"vnf:c776f519aec7486fbf86cb1885af5caf:L2Port:2"}],"id":"000000003","match":{"port_in":"vnf:00000002:User:0"}},{"priority":1,"actions":[{"output":"vnf:00000002:User:0"}],"id":"000000004","match":{"port_in":"vnf:c776f519aec7486fbf86cb1885af5caf:L2Port:2"}},{"priority":1,"actions":[{"output":"vnf:c776f519aec7486fbf86cb1885af5caf:L2Port:0"}],"id":"40639513af0f4a668532dabfeafb26d1","match":{"port_in":"endpoint:00000001"}},{"priority":1,"actions":[{"output":"endpoint:00000001"}],"id":"a0a7a784668943ff8310acf8db0d9818","match":{"port_in":"vnf:c776f519aec7486fbf86cb1885af5caf:L2Port:0"}},{"priority":1,"actions":[{"output":"vnf:c776f519aec7486fbf86cb1885af5caf:L2Port:1"}],"id":"906abbcdb66b44d0accf92115da881c0","match":{"port_in":"vnf:ingress-00000002:inout:0"}},{"priority":1,"actions":[{"output":"vnf:ingress-00000002:inout:0"}],"id":"8cedde94980247c19704525a5e1288eb","match":{"port_in":"vnf:c776f519aec7486fbf86cb1885af5caf:L2Port:1"}},{"priority":1,"actions":[{"output":"vnf:00000002:WAN:0"}],"id":"80806c297cca4f7e8ffe9d28c5a801eb","match":{"port_in":"vnf:egress-00000001:User:0"}},{"priority":1,"actions":[{"output":"vnf:egress-00000001:User:0"}],"id":"8aa1c881f4a44417849eb468ec07f372","match":{"port_in":"vnf:00000002:WAN:0"}},{"priority":1,"actions":[{"output":"vnf:egress-00000001:WAN:0"}],"id":"9e9a3a8197dd4ab79d13cceeb96ec755","match":{"port_in":"endpoint:00000002"}},{"priority":1,"actions":[{"output":"endpoint:00000002"}],"id":"e602ecf0bc7c4842b1bbf40ff41d7825","match":{"port_in":"vnf:egress-00000001:WAN:0"}},{"priority":200,"actions":[{"output":"vnf:50b50202247e43699e3d79916de711fb:L2Port:0"}],"id":"f3f165e0ca974582a7d25a0a3027d6d8","match":{"port_in":"endpoint:dde8196f8c254faa9d24fbbce6ffd55d"}},{"priority":200,"actions":[{"output":"endpoint:dde8196f8c254faa9d24fbbce6ffd55d"}],"id":"15554ec4a6434ff7a11b087c93e45be2","match":{"port_in":"vnf:50b50202247e43699e3d79916de711fb:L2Port:0"}},{"priority":200,"actions":[{"output":"vnf:50b50202247e43699e3d79916de711fb:L2Port:1"}],"id":"e13dd352cea9442a92c268a1420cfdd3","match":{"port_in":"vnf:00000002:control:0"}},{"priority":200,"actions":[{"output":"vnf:00000002:control:0"}],"id":"6b840f3d638440d49cdb6cc62e105004","match":{"port_in":"vnf:50b50202247e43699e3d79916de711fb:L2Port:1"}}]},"id":"00000001","name":"Protected access to the internet"}}
username = 'demo'
password = 'stack'
tenant = 'demo'

logging.basicConfig(level=logging.DEBUG)

ValidateNF_FG().validate(nffg_dict)
nffg = NF_FG()
nffg.parseDict(nffg_dict)

controller = UpperLayerOrchestratorController(user_data=UserData(username, password, tenant))
controller.put(nffg)

print 'Job completed'
exit()


orchestrator_endpoint = "http://127.0.0.1:9000/NF-FG"
headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 
           'X-Auth-User': username, 'X-Auth-Pass': password, 'X-Auth-Tenant': tenant}
requests.put(orchestrator_endpoint, json.dumps(nffg_dict), headers=headers)
print 'Job completed'