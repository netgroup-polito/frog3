import urllib
import httplib2
import json
import string
import random
import time

def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def getToken(url, tenant, user, password):    
    #authentication and get token
    h = httplib2.Http(".cache")
    headers = {'Content-type': 'application/json'}
    body = '{"auth":{"tenantName":"'+tenant+'","passwordCredentials":{"username":"'+user+'","password":"'+password+'"}}}'
    resp, content = h.request(url, "POST", headers=headers, body=body)
    
    print 'keystone getToken-->'+str(resp.status)
    if resp.status!= 200:
        print "ERROR: keystone looks down from here"
        print body
        quit()
    responseContent = json.loads(content)
    authTokenId = responseContent['access']['token']['id']
    user_id = responseContent['access']['token']['tenant']['id']
    if DEBUG:
        print 'user: '+user+' --> id:'+user_id
        print 'got the token' + authTokenId
    return authTokenId, user_id

def createGroup(novaUrl, token, user_id):
    #group creation and id retrival
    h = httplib2.Http(".cache")
    url = novaUrl+''+user_id+'/os-server-groups'
    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': token, 'User-Agent':'python-novaclient'}
    body = '{"server_group":{"name":"GRAFOTEST","policies":["graph"],"metadata":{"contraints":"0","vms":"5"}}}'
    if DEBUG:
        print "calling POST "+url
        print "\t headers:"+str(headers)
    resp, content = h.request(url, "POST", headers=headers, body=body)
    
    print 'nova POST /os-group-->'+str(resp.status)
    if resp.status!= 200:
        print "ERROR: nova post os-group \n\t"+body
        quit()
    responseContent =  json.loads(content)
    group_id = responseContent['server_group']['id']
    if DEBUG:
        print 'group_id: '+group_id
    return group_id

def deleteGroup(novaUrl, token, user_id, group_id):
    #group deletion
    h = httplib2.Http(".cache")
    url = novaUrl+''+user_id+'/os-server-groups/'+group_id
    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': token, 'User-Agent':'python-novaclient'}
    body = ''
    if DEBUG:
        print "calling DELETE "+url
        print "\t headers:"+str(headers)
    resp, content = h.request(url, "DELETE", headers=headers, body=body)
    
    print 'nova DELETE /os-groups-->'+str(resp.status)
    if resp.status!= 204:
        print "ERROR: nova delete os-groups \n"
        quit()
    return

def launchVM(novaUrl, token, user_id, vm_name, group_id, networks):
    #vm creation
    h = httplib2.Http(".cache")
    url = novaUrl+''+user_id+'/servers'
    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': token, 'User-Agent':'python-novaclient'}
    if (group_id != None):
        body = '{"os:scheduler_hints":{"group":"'+group_id+'"},"server":{"name":"'+vm_name+'","metadata":{"graph_id":"'+group_id+'"}, "imageRef":"a99ee5b8-7fe5-4c08-8fbf-f27c666d890c","flavorRef": 1, "min_count":1, "max_count":1, "networks":'+networks+'}}'
    else:
        body = '{"server":{"name":"'+vm_name+'", "imageRef":"a99ee5b8-7fe5-4c08-8fbf-f27c666d890c","flavorRef": 1, "min_count":1, "max_count":1, "networks":'+networks+'}}'
    if DEBUG:
        print "calling POST "+url
        print "\t headers:"+str(headers)
    resp, content = h.request(url, "POST", headers=headers, body=body)
    
    print 'nova POST /servers-->'+str(resp.status)
    if resp.status!= 202:
        print "ERROR: nova post servers \n\t"+body
        print 'nova resp'+str(content)
        quit()
    responseContent =  json.loads(content)
    vm_id = responseContent['server']['id']
    if DEBUG:
        print 'vm_id: '+vm_id
    return vm_id

def deleteVM(novaUrl, token, user_id, vm_id):
    #vm creation
    h = httplib2.Http(".cache")
    url = novaUrl+''+user_id+'/servers/'+vm_id
    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': token, 'User-Agent':'python-novaclient'}
    body = ''
    if DEBUG:
        print "calling POST "+url
        print "\t headers:"+str(headers)
    resp, content = h.request(url, "DELETE", headers=headers, body=body)
    print 'nova DELETE /server-->'+str(resp.status)
    if resp.status!= 204:
        print "ERROR: nova post servers \n\t"+body
        print 'nova resp'+str(content)
        quit()
    return

def createNet(neuUrl, token, net_name):
    url = neuUrl+'networks'
    h = httplib2.Http(".cache")
    headers = {'Content-type': 'application/json', 'X-Auth-Token':token}
    body = '{"network":{"name":"'+net_name+'","admin_state_up": true}}'
    if DEBUG:
        print "calling POST "+url
        print "\t headers:"+str(headers)
    resp, content = h.request(url, 'POST', headers=headers, body=body)
    print 'neutron POST /network-->'+str(resp.status)
    if resp.status!= 201:
        print "ERROR: neutron post network \n\t"+body
        quit()
    responseContent =  json.loads(content)
    net_id = responseContent['network']['id']
    if DEBUG:
        print 'net_name: '+net_name+'-->net_id: '+net_id
    return net_id

def deleteNet(neuUrl, token, net_id):
    #net deletion
    h = httplib2.Http(".cache")
    url = neuUrl+'networks/'+net_id
    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': token}
    body = ''
    if DEBUG:
        print "calling DELETE "+url
        print "\t headers:"+str(headers)
    resp, content = h.request(url, "DELETE", headers=headers, body=body)
    
    print 'neutron DELETE /network-->'+str(resp.status)
    if resp.status!= 204:
        print "ERROR: neutron delete network \n"
        quit()
    return

def createSubNet(neuUrl, token, net_id, sub_name, cidr):
    url = neuUrl+'subnets'
    h = httplib2.Http(".cache")
    headers = {'Content-type': 'application/json', 'X-Auth-Token':token}
    body = '{"subnet":{"network_id":"'+net_id+'","ip_version": 4, "cidr":"'+cidr+'", "name":"'+sub_name+'","enable_dhcp": false}}'
    if DEBUG:
        print "calling POST "+url
        print "\t headers:"+str(headers)
    resp, content = h.request(url, 'POST', headers=headers, body=body)
    print 'neutron POST /subnetwork-->'+str(resp.status)
    if resp.status!= 201:
        print "ERROR: neutron post subnetwork \n\t"+body
        quit()
    responseContent =  json.loads(content)
    subnet_id = responseContent['subnet']['id']
    if DEBUG:
        print 'subnet: '+sub_name+'-->subnet_id: '+subnet_id
    return subnet_id

def deleteSubNet(neuUrl, token, subnet_id):
    #subnet deletion
    h = httplib2.Http(".cache")
    url = neuUrl+'subnets/'+subnet_id
    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': token}
    body = ''
    if DEBUG:
        print "calling DELETE "+url
        print "\t headers:"+str(headers)
    resp, content = h.request(url, "DELETE", headers=headers, body=body)
    
    print 'neutron DELETE /subnetwork-->'+str(resp.status)
    if resp.status!= 204:
        print "ERROR: neutron delete subnetwork \n"
        quit()
    return

def createPort(neuUrl, token, net_id, port_name):
    url = neuUrl+'ports'
    h = httplib2.Http(".cache")
    headers = {'Content-type': 'application/json', 'X-Auth-Token':token}
    body = '{"port":{"network_id":"'+net_id+'", "admin_state_up":true}}'
    if DEBUG:
        print "calling POST "+url
        print "\t headers:"+str(headers)
    resp, content = h.request(url, 'POST', headers=headers, body=body)
    print 'neutron POST /port-->'+str(resp.status)
    if resp.status!= 201:
        print "ERROR: neutron post port \n\t"+body
        quit()
    responseContent =  json.loads(content)
    port_id = responseContent['port']['id']
    if DEBUG:
        print 'port: '+port_name+'-->port_id: '+port_id
    return port_id

def deletePort(neuUrl, token, port_id):
    #port deletion
    h = httplib2.Http(".cache")
    url = neuUrl+'ports/'+port_id
    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': token}
    body = ''
    if DEBUG:
        print "calling DELETE "+url
        print "\t headers:"+str(headers)
    resp, content = h.request(url, "DELETE", headers=headers, body=body)
    
    print 'neutron DELETE /ports-->'+str(resp.status)
    if resp.status!= 204:
        print "ERROR: neutron delete port \n"
        quit()
    return

def createFlow(neuUrl, token, graph_id, p1, p2):
    url = neuUrl+'flowrules'
    h = httplib2.Http(".cache")
    headers = {'Content-type': 'application/json', 'X-Auth-Token':token}
    body = '{"flowrule":{"id":"'+p1+'_'+p2+'", "graph_id":"'+graph_id+'", "ingressPort":"'+p1+'", "actions":"OUTPUT='+p2+'"}}'
    if DEBUG:
        print "calling POST "+url
        print "\t headers:"+str(headers)
    
    resp, content = h.request(url, 'POST', headers=headers, body=body)
    print "flow: " +json.dumps(body)
    #return
    
    print 'neutron POST /flowrules-->'+str(resp.status)
    if resp.status!= 201:
        print "ERROR: neutron post flowrule \n\t"+body
        quit()
    responseContent =  json.loads(content)
    flow_id = responseContent['flowrule']['id']
    if DEBUG:
        print 'flow_id: '+flow_id
    return flow_id

def deleteFlow(neuUrl, token, f_id):
    #port deletion
    h = httplib2.Http(".cache")
    url = neuUrl+'flowrules/'+f_id
    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': token}
    body = ''
    if DEBUG:
        print "calling DELETE "+url
        print "\t headers:"+str(headers)
    resp, content = h.request(url, "DELETE", headers=headers, body=body)
    
    print 'neutron DELETE /flowrules-->'+str(resp.status)
    if resp.status!= 204:
        print "ERROR: neutron delete flowrule \n"
        quit()
    return


def test5VmsInChain(kUrl, neuUrl, novaUrl, tenant, user, password):
    #5 vms in line, two ports per vm, linked via a net
    print 'testing 5 vms in chain'
    
    print 'start test as '+user
    token, user_id = getToken(kUrl, tenant, user, password)
    group_id = createGroup(novaUrl, token, user_id)
    net_ids = []
    sub_ids = []
    port_ids = []
    flow_ids = []
    for i in range(0, 5):
        net_name = "n"+str(i)
        net_ids.append(createNet(neuUrl, token, net_name))
        sub_name = "s"+str(i)
        sub_ids.append(createSubNet(neuUrl, token, net_ids[i], sub_name, "192.168."+str(i)+".0/24"))
        p = []
        p_name = "p"+str(i)+"_1"
        p.append(createPort(neuUrl, token, net_ids[i], p_name))
        p_name = "p"+str(i)+"_2"
        p.append(createPort(neuUrl, token, net_ids[i], p_name))
        port_ids.append(p)
        time.sleep(1)
        #flows
        flow_ids.append(createFlow(neuUrl, token,group_id, port_ids[i][0], port_ids[i][1]))
    
    networks = '[{"uuid":"'+net_ids[0]+'", "port":"'+port_ids[0][0]+'"}]'
    vm1 = launchVM(novaUrl, token, user_id, "vm1", group_id, networks)
    networks = '[{"uuid":"'+net_ids[0]+'", "port":"'+port_ids[0][1]+'"},{"uuid":"'+net_ids[1]+'", "port":"'+port_ids[1][0]+'"}]'
    vm2 = launchVM(novaUrl, token, user_id, "vm2", group_id, networks)
    networks = '[{"uuid":"'+net_ids[1]+'", "port":"'+port_ids[1][1]+'"},{"uuid":"'+net_ids[2]+'", "port":"'+port_ids[2][0]+'"}]'
    vm3 = launchVM(novaUrl, token, user_id, "vm3", group_id, networks)
    networks = '[{"uuid":"'+net_ids[2]+'", "port":"'+port_ids[2][1]+'"},{"uuid":"'+net_ids[3]+'", "port":"'+port_ids[3][0]+'"}]'
    vm4 = launchVM(novaUrl, token, user_id, "vm4", group_id, networks)
    networks = '[{"uuid":"'+net_ids[3]+'", "port":"'+port_ids[3][1]+'"}]'
    vm5 = launchVM(novaUrl, token, user_id, "vm5", group_id, networks)
    
    #deleteVM(novaUrl, token, user_id, vm1)
    #deleteVM(novaUrl, token, user_id, vm2)
    #deleteVM(novaUrl, token, user_id, vm3)
    #deleteVM(novaUrl, token, user_id, vm4)
    #deleteVM(novaUrl, token, user_id, vm5)
    
    print "\n\n"
    return

def testFunctions(kUrl, neuUrl, novaUrl, tenant, user, password):
    print 'start test as '+user
#get a token
    print 'calling keystone to get the token'
    token, user_id = getToken(kUrl, tenant, user, password)
    print '------------------------------------------'
    print 'group creation'
#create group
    print '\t creating an instance group'
    group_id = createGroup(novaUrl, token, user_id)
    print '\t passed'
    print '------------------------------------------'

#create nets
    print '/t creating net'
    net_name = "n1"
    net_id = createNet(neuUrl, token, net_name)
    print '------------------------------------------'
    
#create subnets
    print '/t creating subnet'
    sub_name = "s1"
    subnet_id = createSubNet(neuUrl, token, net_id, sub_name)
    print '------------------------------------------'
#create ports
    print '/t creating port'
    port_name = "p1"
    port_id = createPort(neuUrl, token, net_id, port_name)
    print '------------------------------------------'
    #create flows
    #send constraints
    #instanciate vms

    print '------------------------------------------'
    print 'all tests passed'
    time.sleep(3)
#done testing, now cleanup
    #delete vms
    #delete constraints
    print '/t neutron cleaning'
    #delete ports (flows will be automatically cancelled)
    print '/t deleting port'
    deletePort(neuUrl, token, port_id)
    print '------------------------------------------'
    #delete subnets
    print '/t deleting subnet'
    deleteSubNet(neuUrl, token, subnet_id)
    print '------------------------------------------'
    #delete nets
    print '/t deleting net'
    deleteNet(neuUrl, token, net_id)
    print '------------------------------------------'
    print 'group deletion'
    #delete group
    print '\t creating an instance group'
    deleteGroup(novaUrl, token, user_id, group_id)
    print '------------------------------------------'
    print 'done cleaning'
    

def test2VMs(keystoneUrl, neuUrl, novaUrl, tenant, user, password):
    token, user_id = getToken(keystoneUrl, tenant, user, password)
    #net_id = createNet(neuUrl, token, "test2VMs")
    #net_id = 'b1911de4-75d3-43fc-ae8f-aa013b63f1a8'
    #graph_id = '4aa0d530-ae03-4786-888a-604688c714b6'
    
    
    
    #graph_id = createGroup(novaUrl, token, user_id)
    
    graph_id = None
    net_id = createNet(neuUrl, token, "a")
    subnet_id = createSubNet(neuUrl, token, net_id, "s", "192.168.108.0/24")
    
    p1 = createPort(neuUrl, token, net_id, "p1")
    p2 = createPort(neuUrl, token, net_id, "p2")
    print 'porte create'
    #time.sleep(3)
    flow = createFlow(neuUrl, token, "1", p1, p2)
    
    flow = createFlow(neuUrl, token, "1b", p2, p1)
    print 'flusso creato'
    #time.sleep(3)
    vm1 = launchVM(novaUrl, token, user_id, "vm1", graph_id, '[{"uuid":"'+net_id+'", "port":"'+p1+'"}]')
    print 'vm1 creata'
    #time.sleep(5)
    #aaaaaaaaaaaaa = raw_input('in attesa di un tasto')
    
    vm2 = launchVM(novaUrl, token, user_id, "vm2", graph_id, '[{"uuid":"'+net_id+'", "port":"'+p2+'"}]')
    print 'vm2 creata'
    print 'done'

def test3VMs(keystoneUrl, neuUrl, novaUrl, tenant, user, password):
    token, user_id = getToken(keystoneUrl, tenant, user, password)
    #net_id = createNet(neuUrl, token, "test2VMs")
    #net_id = 'b1911de4-75d3-43fc-ae8f-aa013b63f1a8'
    #graph_id = '4aa0d530-ae03-4786-888a-604688c714b6'
    
    
    
    #graph_id = createGroup(novaUrl, token, user_id)
    
    graph_id = None
    net_id = createNet(neuUrl, token, "a")
    subnet_id = createSubNet(neuUrl, token, net_id, "s", "192.168.112.0/24")
    
    p1 = createPort(neuUrl, token, net_id, "p1")
    p2 = createPort(neuUrl, token, net_id, "p2")
    p3 = createPort(neuUrl, token, net_id, "p3")
    print 'porte create'
    #time.sleep(3)
    flow = createFlow(neuUrl, token, "1", p1, p2)
    flow = createFlow(neuUrl, token, "1b", p2, p1)
    flow = createFlow(neuUrl, token, "2", p1, p3)
    flow = createFlow(neuUrl, token, "2b", p3, p1)
    flow = createFlow(neuUrl, token, "3", p2, p3)
    flow = createFlow(neuUrl, token, "3b", p3, p2)
    print 'flusso creato'
    #time.sleep(3)
    vm1 = launchVM(novaUrl, token, user_id, "vm1", graph_id, '[{"uuid":"'+net_id+'", "port":"'+p1+'"}]')
    print 'vm1 creata'
    #time.sleep(5)
    #aaaaaaaaaaaaa = raw_input('in attesa di un tasto')
    
    vm2 = launchVM(novaUrl, token, user_id, "vm2", graph_id, '[{"uuid":"'+net_id+'", "port":"'+p2+'"}]')
    print 'vm2 creata'
    vm3 = launchVM(novaUrl, token, user_id, "vm3", graph_id, '[{"uuid":"'+net_id+'", "port":"'+p3+'"}]')
    print 'vm3 creata'
    print 'done'


def testNVMs(keystoneUrl, neuUrl, novaUrl, tenant, user, password):
    token, user_id = getToken(keystoneUrl, tenant, user, password)
    #net_id = createNet(neuUrl, token, "test2VMs")
    net_id = 'b1911de4-75d3-43fc-ae8f-aa013b63f1a8'
    graph_id = '4aa0d530-ae03-4786-888a-604688c714b6'
    
    
    '''
    graph_id = createGroup(novaUrl, token, user_id)
    net_id = createNet(neuUrl, token, "a")
    subnet_id = createSubNet(neuUrl, token, net_id, "s", "192.168.100.0/24")
    '''
    N = 1
    for i in range (1, N+1):
        p = createPort(neuUrl, token, net_id, "p"+str(i))
        time.sleep(2)
        vm = launchVM(novaUrl, token, user_id, "vm"+str(i), graph_id, '[{"uuid":"'+net_id+'", "port":"'+p+'"}]')
        
    print 'done'



def createNNetworks(keystoneUrl, neuUrl, tenant, user, password, N):
    token, user_id = getToken(keystoneUrl, tenant, user, password)
    #net_id = createNet(neuUrl, token, "test2VMs")
    #net_id = 'b1911de4-75d3-43fc-ae8f-aa013b63f1a8'
    #graph_id = '4aa0d530-ae03-4786-888a-604688c714b6'
    
    
    
    #graph_id = createGroup(novaUrl, token, user_id)
    for i in range(0,N):
        net_id = createNet(neuUrl, token, "n"+str(i))
        subnet_id = createSubNet(neuUrl, token, net_id, "s"+str(i), "192.168."+str(i)+".0/24")
#call the main function

DEBUG=True
controllerIP = "130.192.225.193"
keystoneUrl = 'http://'+controllerIP+':35357/v2.0/tokens'
neutronBaseUrl = 'http://'+controllerIP+':9696/v2.0/'
novaBaseUrl = 'http://'+controllerIP+':8774/v2/'
'''
#test 1
tenant='admin'
user='admin'
password='stack'
#testFunctions(keystoneUrl, neutronBaseUrl, tenant, user, password)
time.sleep(3)
'''
#test 2
tenant='admin'
user=tenant
password='stack'
#test3VMs(keystoneUrl, neutronBaseUrl, novaBaseUrl, tenant, user, password)
#testFunctions(keystoneUrl, neutronBaseUrl, novaBaseUrl, tenant, user, password)
N = 20
createNNetworks(keystoneUrl, neutronBaseUrl, tenant, user, password, N)

#test5VmsInChain(keystoneUrl, neutronBaseUrl, novaBaseUrl, tenant, user, password)

print 'fine'
