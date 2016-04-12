'''
Created on Jun 22, 2015

@author: fabiomignini
'''
from nffg_library.nffg import NF_FG
from orchestrator_core.sql.graph import Graph
from orchestrator_core.sql.session import Session


#nffg_dict = {"forwarding-graph":{"id":"00000001","name":"Protected access to the internet","VNFs":[{"vnf_template":"switch.json","id":"00000001","name":"switch-data","ports":[{"id":"L2Port:0","name":"data-lan"},{"id":"L2Port:1","name":"data-lan"},{"id":"L2Port:2","name":"data-lan"}],"groups":["isp-function"]},{"vnf_template":"dhcp.json","ports":[{"id":"inout:0","name":"data-port"}],"name":"dhcp","id":"00000002","groups":["isp-function"]},{"vnf_template":"firewall.json","ports":[{"id":"WAN:0"},{"id":"User:0"}],"name":"firewall","id":"00000003"},{"vnf_template":"nat.json","ports":[{"id":"WAN:0"},{"id":"User:0"}],"name":"router-nat","id":"00000004","groups":["isp-function"]}],"end-points":[{"id":"00000001","name":"ingress","type":"internal","remote_endpoint_id":"remote_graph0001:remote_endpoint_001","internal":{}},{"id":"00000002","name":"egress","type":"interface-out","interface-out":{"node":"79.56.71.237","interface":"to-br-ex"}}],"big-switch":{"flow-rules":[{"id":"000000001","priority":1,"match":{"port_in":"endpoint:00000001"},"actions":[{"output":"vnf:00000001:L2Port:0"}]},{"id":"000000002","priority":1,"match":{"port_in":"vnf:00000001:L2Port:0"},"actions":[{"output":"endpoint:00000001"}]},{"id":"000000003","priority":1,"match":{"port_in":"vnf:00000002:inout:0"},"actions":[{"output":"vnf:00000001:L2Port:1"}]},{"id":"000000004","priority":1,"match":{"port_in":"vnf:00000001:L2Port:1"},"actions":[{"output":"vnf:00000002:inout:0"}]},{"id":"000000005","priority":1,"match":{"port_in":"vnf:00000003:User:0"},"actions":[{"output":"vnf:00000001:L2Port:2"}]},{"id":"000000006","priority":1,"match":{"port_in":"vnf:00000001:L2Port:2"},"actions":[{"output":"vnf:00000003:User:0"}]},{"id":"000000007","priority":1,"match":{"port_in":"vnf:00000003:WAN:0"},"actions":[{"output":"vnf:00000004:User:0"}]},{"id":"000000008","priority":1,"match":{"port_in":"vnf:00000004:User:0"},"actions":[{"output":"vnf:00000003:WAN:0"}]},{"id":"000000009","priority":1,"match":{"port_in":"endpoint:00000002"},"actions":[{"output":"vnf:00000004:WAN:0"}]},{"id":"000000010","priority":1,"match":{"port_in":"vnf:00000004:WAN:0"},"actions":[{"output":"endpoint:00000002"}]}]}}}

#Session().inizializeSession(1, 'pippo', 'test_id', 'test_name')
'''
Session().add_session(1, 'supercazzola',
                      'nuc1', 'Demo-Turin-2015-day2',
                      'Protected_access_to_the_internet',
                      'nuc1', 'scheduling')
'''
#nffg = NF_FG()
#nffg.parseDict(nffg_dict)
#Graph().addNFFG(nffg, 1)
print Graph().get_nffg(0).getJSON()

