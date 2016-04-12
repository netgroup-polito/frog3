'''
Created on Oct 23, 2015

@author: fabiomignini
'''
import requests, json

nffg_dict_updated = {"forwarding-graph":{"VNFs":[{"ports":[{"id":"L2Port:0","name":"data-lan"},{"id":"L2Port:1","name":"data-lan"},{"id":"L2Port:2","name":"data-lan"},{"id":"L2Port:3","name":"data-lan"}],"vnf_template":"switch.json","id":"00000001","groups":["isp-function"],"name":"switch-data"},{"ports":[{"id":"inout:0","name":"data-port"}],"vnf_template":"dhcp.json","id":"00000002","groups":["isp-function"],"name":"dhcp"},{"ports":[{"id":"inout:0","name":"data-port"}],"vnf_template":"dhcp.json","id":"00000005","groups":["isp-function"],"name":"dhcp"},{"ports":[{"id":"L2Port:0"},{"id":"L2Port:1"}],"vnf_template":"switch.json","id":"00000006","name":"firewall"},{"ports":[{"id":"User:0"}],"vnf_template":"nat.json","id":"00000004","groups":["isp-function"],"name":"router-nat"}],"end-points":[{"interface":{"node":"130.192.225.193","interface":"to-br-usr"},"type":"interface","id":"00000001","name":"ingress"}],"big-switch":{"flow-rules":[{"priority":1,"actions":[{"output":"vnf:00000001:L2Port:0"}],"id":"000000001","match":{"port_in":"endpoint:00000001"}},{"priority":1,"actions":[{"output":"endpoint:00000001"}],"id":"000000002","match":{"port_in":"vnf:00000001:L2Port:0"}},{"priority":1,"actions":[{"output":"vnf:00000001:L2Port:1"}],"id":"000000003","match":{"port_in":"vnf:00000002:inout:0"}},{"priority":1,"actions":[{"output":"vnf:00000002:inout:0"}],"id":"000000004","match":{"port_in":"vnf:00000001:L2Port:1"}},{"priority":1,"actions":[{"output":"vnf:00000001:L2Port:2"}],"id":"000000005","match":{"port_in":"vnf:00000006:L2Port:0"}},{"priority":1,"actions":[{"output":"vnf:00000006:L2Port:0"}],"id":"000000006","match":{"port_in":"vnf:00000001:L2Port:2"}},{"priority":1,"actions":[{"output":"vnf:00000004:User:0"}],"id":"000000007","match":{"port_in":"vnf:00000006:L2Port:1"}},{"priority":1,"actions":[{"output":"vnf:00000006:L2Port:1"}],"id":"000000008","match":{"port_in":"vnf:00000004:User:0"}},{"priority":1,"actions":[{"output":"vnf:00000001:L2Port:3"}],"id":"000000011","match":{"port_in":"vnf:00000005:inout:0"}},{"priority":1,"actions":[{"output":"vnf:00000005:inout:0"}],"id":"000000012","match":{"port_in":"vnf:00000001:L2Port:3"}}]},"id":"00000001","name":"Protected access to the internet"}}
orchestrator_endpoint = "http://127.0.0.1:9000/NF-FG"
username = 'demo'
password = 'stack'
tenant = 'demo'
headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 
           'X-Auth-User': username, 'X-Auth-Pass': password, 'X-Auth-Tenant': tenant}
requests.put(orchestrator_endpoint, json.dumps(nffg_dict_updated), headers=headers)
print 'Job completed'