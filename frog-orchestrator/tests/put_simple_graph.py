'''
Created on Oct 23, 2015

@author: fabiomignini
'''
import requests, json

nffg_dict = {"forwarding-graph":{"id":"00000001","name":"Protected access to the internet","VNFs":[{"vnf_template":"switch.json","id":"00000001","name":"switch-data","ports":[{"id":"L2Port:0","name":"data-lan"},{"id":"L2Port:1","name":"data-lan"},{"id":"L2Port:2","name":"data-lan"}],"groups":["isp-function"]},{"vnf_template":"dhcp.json","ports":[{"id":"inout:0","name":"data-port"}],"name":"dhcp","id":"00000002","groups":["isp-function"]},{"vnf_template":"cisco_firewall.json","ports":[{"id":"WAN:0"},{"id":"User:0"}],"name":"firewall","id":"00000003"},{"vnf_template":"nat.json","ports":[{"id":"WAN:0"},{"id":"User:0"}],"name":"router-nat","id":"00000004","groups":["isp-function"]}],"end-points":[{"id":"00000001","name":"ingress","type":"interface","interface":{"node":"130.192.225.193","interface":"to-br-usr"}},{"id":"00000002","name":"egress","type":"interface-out","interface-out":{"node":"130.192.225.193","interface":"eth2"}}],"big-switch":{"flow-rules":[{"id":"000000001","priority":1,"match":{"port_in":"endpoint:00000001"},"actions":[{"output":"vnf:00000001:L2Port:0"}]},{"id":"000000002","priority":1,"match":{"port_in":"vnf:00000001:L2Port:0"},"actions":[{"output":"endpoint:00000001"}]},{"id":"000000003","priority":1,"match":{"port_in":"vnf:00000002:inout:0"},"actions":[{"output":"vnf:00000001:L2Port:1"}]},{"id":"000000004","priority":1,"match":{"port_in":"vnf:00000001:L2Port:1"},"actions":[{"output":"vnf:00000002:inout:0"}]},{"id":"000000005","priority":1,"match":{"port_in":"vnf:00000003:User:0"},"actions":[{"output":"vnf:00000001:L2Port:2"}]},{"id":"000000006","priority":1,"match":{"port_in":"vnf:00000001:L2Port:2"},"actions":[{"output":"vnf:00000003:User:0"}]},{"id":"000000007","priority":1,"match":{"port_in":"vnf:00000003:WAN:0"},"actions":[{"output":"vnf:00000004:User:0"}]},{"id":"000000008","priority":1,"match":{"port_in":"vnf:00000004:User:0"},"actions":[{"output":"vnf:00000003:WAN:0"}]},{"id":"000000009","priority":1,"match":{"port_in":"endpoint:00000002"},"actions":[{"output":"vnf:00000004:WAN:0"}]},{"id":"000000010","priority":1,"match":{"port_in":"vnf:00000004:WAN:0"},"actions":[{"output":"endpoint:00000002"}]}]}}}
orchestrator_endpoint = "http://127.0.0.1:9000/NF-FG"
username = 'demo'
password = 'stack'
tenant = 'demo'
headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 
           'X-Auth-User': username, 'X-Auth-Pass': password, 'X-Auth-Tenant': tenant}
requests.put(orchestrator_endpoint, json.dumps(nffg_dict), headers=headers)
print 'Job completed'