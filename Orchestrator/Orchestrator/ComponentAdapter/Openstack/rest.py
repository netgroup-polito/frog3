'''
Created on Oct 1, 2014

@author: fabiomignini
'''

import requests
import json
import logging

from Common.config import Configuration
ODL_ENDPOINT = Configuration().ODL_ENDPOINT


class ODL(object):
    
    endpoint = ODL_ENDPOINT
    odl_controllerPath="/controller/nb/v2"
    odl_connectionManagerPath="/connectionmanager"
    odl_flowProgrammerPath="/flowprogrammer"
    odl_getNodes="/nodes"
    odl_ovsdbPath="/ovsdb/nb/v2/node/OVS/%s:%s/tables"
    odl_getBridgePath="/bridge/rows"
    odl_createBridgPath="/bridge/rows"
    odl_deleteBridgPath="/bridge/rows/%s"
    odl_getPortPath="/port/rows"
    odl_createPortPath="/port/rows"
    odl_deletePortPath="/port/rows/%s"
    odl_getInterfacesPath="/interface/rows/"
    odl_updateInterfacesPath="/interface/rows/%s"
    odl_createFlowmodPath="/default/node/OF/%s/staticFlow/%s"
    odl_username = "admin"
    odl_password = "SDN@Edge_Polito"
    timeout = Configuration().TIMEOUT_ODL
    
    def createFlowmod(self, flowmod, name, node_dpid):   
        
        data = json.dumps(flowmod)
        
        headers = {'Content-Type': 'application/json', "cache-control": "no-cache"}
        url = self.endpoint+self.odl_controllerPath+self.odl_flowProgrammerPath+(self.odl_createFlowmodPath % (node_dpid, name))
        resp = requests.put(url, headers=headers, data=data, auth=(self.odl_username, self.odl_password), timeout=self.timeout)
        resp.raise_for_status()
        return resp.text
    
    def getFlowmod(self, flowmod, name, node_dpid):   
        
        data = json.dumps(flowmod)
        
        headers = {'Content-Type': 'application/json', "cache-control": "no-cache"}
        url = self.endpoint+self.odl_controllerPath+self.odl_flowProgrammerPath+(self.odl_createFlowmodPath % (node_dpid, name))
        resp = requests.get(url, headers=headers, data=data, auth=(self.odl_username, self.odl_password), timeout=self.timeout)
        resp.raise_for_status()
        return resp.text
    
    def deleteFlowmod(self, flowmod, name, node_dpid):   
        
        data = json.dumps(flowmod)
        
        headers = {'Content-Type': 'application/json', "cache-control": "no-cache"}
        url = self.endpoint+self.odl_controllerPath+self.odl_flowProgrammerPath+(self.odl_createFlowmodPath % (node_dpid, name))
        resp = requests.delete(url, headers=headers, data=data, auth=(self.odl_username, self.odl_password), timeout=self.timeout)
        resp.raise_for_status()
        return resp.text
    
    def getNodes(self):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        resp = requests.get(self.endpoint+self.odl_controllerPath+self.odl_connectionManagerPath+self.odl_getNodes, headers=headers, auth=(self.odl_username, self.odl_password), timeout=self.timeout)
        resp.raise_for_status()
        return resp.text
    
    def getBridges(self, node_ip, node_port):
        '''
        Args:
            node_ip:
                The endpoint to the node where the bridges are
            node_port:
                Port, where the socket in the node, speaking with the controller
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        resp = requests.get(self.endpoint+(self.odl_ovsdbPath % (node_ip, node_port))+self.odl_getBridgePath, headers=headers, auth=(self.odl_username, self.odl_password), timeout=self.timeout)
        resp.raise_for_status()
        return resp.text
        
    def getInterfaces(self, port_id, node_ip, node_port):
        '''
        Args:
            port_id:
                uuid of the ports that the interface belongs to 
            node_ip:
                The endpoint to the node where the bridges are
            node_port:
                Port, where the socket in the node, speaking with the controller
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        path = self.endpoint+(self.odl_ovsdbPath % (node_ip, node_port))+self.odl_getInterfacesPath
        resp = requests.get(path, headers=headers, auth=(self.odl_username, self.odl_password), timeout=self.timeout)
        resp.raise_for_status()
        return resp.text
    
    def getPorts(self, node_ip, node_port):
        '''
        Args:
            node_ip:
                The endpoint to the node where the bridges are
            node_port:
                Port, where the socket in the node, speaking with the controller
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        resp = requests.get(self.endpoint+(self.odl_ovsdbPath % (node_ip, node_port))+self.odl_getPortPath, headers=headers, auth=(self.odl_username, self.odl_password), timeout=self.timeout)
        resp.raise_for_status()
        return resp.text
    
    def createPort(self, name, bridge_id, node_ip, node_port):
        '''
        Args:
            name:
                name of the port
            bridge_id:
                uuid of the parent bridge of the port
            node_ip:
                The endpoint to the node where the bridges are
            node_port:
                Port, where the socket in the node, speaking with the controller
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        body = {"parent_uuid": bridge_id,
                "row": {"Port": {"name": name}}}
        resp = requests.post(self.endpoint+(self.odl_ovsdbPath % (node_ip, node_port))+self.odl_createPortPath, data=json.dumps(body), headers=headers, auth=(self.odl_username, self.odl_password), timeout=self.timeout)
        resp.raise_for_status()
        return resp.text
    
    def deletePort(self, port_id, node_ip, node_port):
        '''
        Args:
            name:
                uuid of the port
            bridge_id:
                uuid of the parent bridge of the port
            node_ip:
                The endpoint to the node where the bridges are
            node_port:
                Port, where the socket in the node, speaking with the controller
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        resp = requests.delete(self.endpoint+(self.odl_ovsdbPath % (node_ip, node_port))+(self.odl_deletePortPath % (port_id)), headers=headers, auth=(self.odl_username, self.odl_password), timeout=self.timeout)
        resp.raise_for_status()
        return resp.text
        
    def createBridge(self, name, node_ip, node_port):
        '''
        Args:
            name:
                name of the bridge
            node_ip:
                The endpoint to the node where the bridges are
            node_port:
                Port, where the socket in the node, speaking with the controller
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        body = {"row": {"Bridge": {"name": name}}}
        resp = requests.post(self.endpoint+(self.odl_ovsdbPath % (node_ip, node_port))+self.odl_createBridgPath, data=json.dumps(body), headers=headers, auth=(self.odl_username, self.odl_password), timeout=self.timeout)
        resp.raise_for_status()
        return resp.text 
    
    def deleteBridge(self, bridge_id, node_ip, node_port):  
        '''
        Args:
            bridge_id:
                uuid of the bridge
            node_ip:
                The endpoint to the node where the bridges are
            node_port:
                Port, where the socket in the node, speaking with the controller
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        resp = requests.delete(self.endpoint+(self.odl_ovsdbPath % (node_ip, node_port))+(self.odl_deleteBridgPath % (bridge_id)), headers=headers, auth=(self.odl_username, self.odl_password), timeout=self.timeout)
        resp.raise_for_status()
        return resp.text
        
    def setPatchPort(self, interface_id, remote_port_name, bridge_id, node_ip, node_port):
        '''
        Args:
            interface_id: 
                uuid of the interface
            remote_port_name:
                name of the peer interface
            bridge_id:
                uuid of the bridge that the interface belongs to
            node_ip:
                The endpoint to the node where the bridges are
            node_port:
                Port, where the socket in the node, speaking with the controller
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        body = { "row": { "Interface": { "type": "patch","options": 
                [ "map", [ [ "peer", remote_port_name ] ] ] } } }
        resp = requests.put(self.endpoint+(self.odl_ovsdbPath % (node_ip, node_port))+self.odl_updateInterfacesPath % (interface_id), data=json.dumps(body), headers=headers, auth=(self.odl_username, self.odl_password), timeout=self.timeout)
        resp.raise_for_status()
        return resp.text

class Heat(object):
    ''' 
    Class used to call the Heat Openstack API
    '''
    
    getStackPath="/stacks"
    createStackPath="/stacks"
    updateStackPath="/stacks/%s/%s"
    deleteStackPath="/stacks/%s/%s"
    getStackIDPath="/stacks/%s"
    stackResourcesPath="/stacks/%s/%s/resources"
    connectSwitchesPath="/connect_switches"
    createPortPath="/create_port"
    createBridgePath="/create_bridge"
    createFlowPath="/create_flow"
    getPortIDPath="/get_port_id"
    timeout = Configuration().TIMEOUT_HEAT
    

    
    def getStackList(self, heatEndpoint, token):
        '''
        Return the JSON with the list of the user stacks
        Args:
            heatEndpoint:
                The endpoint to the heat server that should instantiate the stack (example: http://serverAddr:heatport/v1/<tenant-ID>)
            token:
                Keysone token for the authentication
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error or the token is expired
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.get(heatEndpoint+self.getStackPath, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.text
        
    def instantiateStack(self, heatEndpoint, token, stackName, jsonStackTemplate, jsonParameters={}):
        '''
        Instantiate the user profile stack from a JSON template in Heat
        Args:
            heatEndpoint:
                The endpoint to the heat server that should instantiate the stack (example: http://serverAddr:heatport/v1/<tenant-ID>)
            stackName:
                Name of the stack to instantiate
            jsonStackTemplate:
                The template in a json format that represents the stack to be instantiated (not the string)
            jsonParameters:
                The JSON data that identify the parameters to input in the stack with the format <param_name>:<param_value> (not the string)
            token:
                Keysone token for the authentication
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error or the token is expired
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        stack_data = {'stack_name': stackName, 'template': jsonStackTemplate, 'parameters': jsonParameters, 'timeout_mins': 60}
        resp = requests.post(heatEndpoint+self.createStackPath, data=json.dumps(stack_data), headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.text
    
    def updateStack(self, heatEndpoint, token, stackName, stackID, jsonStackTemplate, jsonParameters={}):
        '''
        Update the user profile stack from a json template in Heat
        Args:
            heatEndpoint:
                The endpoint to the heat server that should instantiate the stack (example: http://serverAddr:heatport/v1/<tenant-ID>)
            stackName:
                Name of the stack to update
            stackID:
                ID of the stack to update
            jsonStack:
                The template in a JSON format that represents the stack to be instantiated (not the string)
            jsonParameters:
                The JSON data that identify the parameters to input in the stack with the format <param_name>:<param_value> (not the string)
            token:
                Keysone token for the authentication
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error or the token is expired
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        stack_data = {'template': jsonStackTemplate, 'parameters': jsonParameters, 'timeout_mins': 1}
        resp = requests.put(heatEndpoint+(self.updateStackPath % (stackName, stackID)), data=json.dumps(stack_data), headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp
    
    def deleteStack(self, heatEndpoint, token, stackName, stackID):
        '''
        Delete the user profile stack
        Args:
            heatEndpoint:
                The endpoint to the heat server that should instantiate the stack (example: http://serverAddr:heatport/v1/<tenant-ID>)
            stackName:
                Name of the stack to update
            stackID:
                ID of the stack to update
            token:
                Keysone token for the authentication
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error or the token is expired
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.delete(heatEndpoint+(self.deleteStackPath % (stackName, stackID)), headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp
    
    def getStackID(self, heatEndpoint, token, stackName):
        '''
        Return the ID of the searched stack
        Args:
            heatEndpoint:
                The endpoint to the heat server that should instantiate the stack (example: http://serverAddr:heatport/v1/<tenant-ID>)
            stackName:
                Name of the stack to find
            token:
                Keysone token for the authentication
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error or the token is expired
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.get(heatEndpoint+(self.getStackIDPath % stackName), headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        data = json.loads(resp.text)
        return data['stack']['id']
    
    def getStackStatus(self, heatEndpoint, token, stackName):
        '''
        Return the stack information
        Args:
            heatEndpoint:
                The endpoint to the heat server that should instantiate the stack (example: http://serverAddr:heatport/v1/<tenant-ID>)
            stackName:
                Name of the stack to find
            token:
                Keysone token for the authentication
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error or the token is expired
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.get(heatEndpoint+(self.getStackIDPath % stackName), headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        data = json.loads(resp.text)
        return data['stack']['stack_status']

    def checkStackStatus(self, heatEndpoint, token, stackName):
        '''
        Return the stack information
        Args:
            heatEndpoint:
                The endpoint to the heat server that should instantiate the stack (example: http://serverAddr:heatport/v1/<tenant-ID>)
            stackName:
                Name of the stack to find
            token:
                Keysone token for the authentication
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error or the token is expired
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.get(heatEndpoint+(self.getStackIDPath % stackName), headers=headers, timeout=self.timeout)
        return resp.status_code
    
    def getStackResourcesStatus(self, heatEndpoint, token, stackName, stackID):
        '''
        Return the stack's resources information
        Args:
            heatEndpoint:
                The endpoint to the heat server that should instantiate the stack (example: http://serverAddr:heatport/v1/<tenant-ID>)
            stackName:
                Name of the stack to find
            token:
                Keysone token for the authentication
            stackID:
                ID of the stack 
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error or the token is expired
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.get(heatEndpoint+(self.stackResourcesPath % (stackName, stackID)), headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        data = json.loads(resp.text)
        return data

class Nova(object):
    '''
    Class used to call the Nova Openstack API
    '''
    
    getFlavorsDetail = "/flavors/detail"
    getHypervisorsPath="/os-hypervisors"
    getHypervisorsInfoPath="/os-hypervisors/detail"
    getAvailabilityZonesPath="/os-availability-zone/detail"
    getHostAggregateListPath="/os-aggregates"
    addComputeNodeToHostAggregatePath = "/os-aggregates/%s/action"
    addServer = "/servers"
    timeout = Configuration().TIMEOUT_NOVA
    
    
    def addComputeNodeToHostAggregate(self, novaEndpoint, token, host_aggregate_id, hostname):
        '''
        {"add_host": {"host": "computebender"}}
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        data = {"add_host": {"host": hostname}}
        data = json.dumps(data)
        
        path = novaEndpoint+(self.addComputeNodeToHostAggregatePath % host_aggregate_id)
        print "\n\n\n"+data+"\n"+path+"\n\n" 
        resp = requests.post(path, 
                             data = data,
                             headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.text
        
    def getHostAggregateList(self, novaEndpoint, token):
        '''
        {
          "aggregates": [
            {
              "name": "aggregate-test",
              "availability_zone": "test",
              "deleted": false,
              "created_at": "2015-03-30T07:50:57.000000",
              "updated_at": null,
              "hosts": [
                "openstack-compute"
              ],
              "deleted_at": null,
              "id": 1,
              "metadata": {
                "availability_zone": "test"
              }
            }
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.get(novaEndpoint+self.getHostAggregateListPath, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.text
    
    def getAvailabilityZones(self, novaEndpoint, token):
        """
        {
          "availabilityZoneInfo": [
            {
              "zoneState": {
                "available": true
              },
              "hosts": {
                "openstack-controller": {
                  "nova-conductor": {
                    "available": true,
                    "active": true,
                    "updated_at": "2015-04-17T09:41:37.000000"
                  },
                  "nova-consoleauth": {
                    "available": true,
                    "active": true,
                    "updated_at": "2015-04-17T09:41:29.000000"
                  },
                  "nova-cert": {
                    "available": true,
                    "active": true,
                    "updated_at": "2015-04-17T09:41:28.000000"
                  },
                  "nova-scheduler": {
                    "available": true,
                    "active": true,
                    "updated_at": "2015-04-17T09:41:33.000000"
                  }
                }
              },
              "zoneName": "internal"
            }
        """
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.get(novaEndpoint+self.getAvailabilityZonesPath, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.text
        
    def getHypervisorsInfo(self, novaEndpoint, token):
        """
        {
           "hypervisors":
           [
               {
                   "service":
                   {
                       "host": "openstack-compute",
                       "id": 5
                   },
                   "vcpus_used": 3,
                   "hypervisor_type": "QEMU",
                   "local_gb_used": 120,
                   "host_ip": "130.192.225.233",
                   "hypervisor_hostname": "openstack-compute",
                   "memory_mb_used": 6656,
                   "memory_mb": 15977,
                   "current_workload": 0,
                   "vcpus": 4,
                   "cpu_info": "{"vendor": "Intel", "model": "SandyBridge", "arch": "x86_64", "features": ["ssse3", "pge", "avx", "clflush", "sep", "syscall", "vme", "dtes64", "invpcid", "msr", "sse", "xsave", "vmx", "erms", "xtpr", "cmov", "tsc", "smep", "pbe", "est", "pat", "monitor", "lm", "abm", "nx", "fxsr", "tm", "sse4.1", "pae", "sse4.2", "pclmuldq", "acpi", "fma", "tsc-deadline", "popcnt", "mmx", "osxsave", "cx8", "mce", "mtrr", "rdtscp", "ht", "pse", "lahf_lm", "pdcm", "mca", "pdpe1gb", "apic", "fsgsbase", "f16c", "ds", "pni", "tm2", "avx2", "aes", "sse2", "ss", "bmi1", "bmi2", "pcid", "de", "fpu", "cx16", "pse36", "ds_cpl", "movbe", "rdrand", "x2apic"], "topology": {"cores": 2, "threads": 2, "sockets": 1}}",
                   "running_vms": 3,
                   "free_disk_gb": -19,
                   "hypervisor_version": 2000000,
                   "disk_available_least": -31,
                   "local_gb": 101,
                   "free_ram_mb": 9321,
                   "id": 1
               }
            ]
        }
        """
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.get(novaEndpoint+self.getHypervisorsInfoPath, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.text
    
    def get_hypervisors(self, novaEndpoint, token):
        """
        {
          "hypervisors": [
            {
              "id": 1,
              "hypervisor_hostname": "openstack-compute"
            }
          ]
        }
        """
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.get(novaEndpoint+self.getHypervisorsPath, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.text
    
    def get_flavors(self, novaEndpoint, token, minRam=None, minDisk=None):
        '''
        Return the flavors data
        Args:
            novaEndpoint:
                The endpoint to the nova server (example: http://serverAddr:novaport/v2/<tenant-ID>)
            token:
                Keysone token for the authentication
            minRam:
                The minimum Ram size of the returned flavors (Optional)
            minDisk:
                The minimum Disk size of the returned flavors (Optional)
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error or the token is expired
        '''
        data = {}
        data['minRam'] = int(minRam or 0)
        data['minDisk'] = int(minDisk or 0)
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.get(novaEndpoint+self.getFlavorsDetail, params=data, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        flavor = json.loads(resp.text)
        return flavor
    
    def createServer(self, novaEndpoint, token, server_data):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.post(novaEndpoint + self.addServer, data=json.dumps(server_data), headers=headers)
        resp.raise_for_status()
        return json.loads(resp.text)
    
    def getServerStatus(self, novaEndpoint, token, server_id):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.get(novaEndpoint + self.addServer + "/" + server_id, headers=headers)
        resp.raise_for_status()
        data = json.loads(resp.text)
        return data['server']['status']
    
    def deleteServer(self, novaEndpoint, token, server_id):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.delete(novaEndpoint + self.addServer + "/" + server_id, headers=headers)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp
          
class Glance(object):
    '''
    Class used for Glance API
    '''
    timeout = Configuration().TIMEOUT_GLANCE
    
    def get_image(self, imageURI, token):
        '''
        Return the name of an image from the URI
        '''         
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.get(imageURI, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        data = json.loads(resp.text)
        return data
        
class Neutron(object):
    '''
    Class used for Neutron API
    '''
    get_networks = "/v2.0/networks"
    create_network = "/v2.0/networks"
    get_ports = "/v2.0/ports"
    create_subnet = "/v2.0/subnets"
    create_flowrule = "/v2.0/flowrules"
    delete_flowrule = "/v2.0/flowrules/%s"
    delete_network = "/v2.0/networks/%s"
    delete_subnet = "/v2.0/subnets/%s"
    get_network_status = "/v2.0/networks/%s"
    get_subnet_status = "/v2.0/subnets/%s"
    get_port_status = "/v2.0/ports/%s"
    get_flowrule_status = "/v2.0/flowrules/%s"
    
    def getFlowruleStatus(self, neutronEndpoint, token, flowrule_id):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.get(neutronEndpoint + (self.get_flowrule_status % flowrule_id), headers=headers)
        if resp.status_code == 404 or resp.status_code == 500:
            return 'not_found'
        resp.raise_for_status()
        return 'ACTIVE'
    
    def createFlowrule(self, neutronEndpoint, token, flowroute_data):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.post(neutronEndpoint + self.create_flowrule, data=json.dumps(flowroute_data), headers=headers)
        resp.raise_for_status()
        return json.loads(resp.text)
    
    def deleteFlowrule(self, neutronEndpoint, token, flowrule_id):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        path = neutronEndpoint + (self.delete_flowrule % flowrule_id)
        logging.debug(path)
        resp = requests.delete(path, headers=headers)
        return resp

    def createNetwork(self, neutronEndpoint, token, network_data):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        logging.debug(neutronEndpoint + self.create_network)
        resp = requests.post(neutronEndpoint + self.create_network, data=json.dumps(network_data), headers=headers)
        resp.raise_for_status()
        return json.loads(resp.text)
    
    def deleteNetwork(self, neutronEndpoint, token, network_id):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.delete(neutronEndpoint + (self.delete_network % network_id), headers=headers)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp
    
    def getNetworkStatus(self, neutronEndpoint, token, network_id):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.get(neutronEndpoint + (self.get_network_status % network_id), headers=headers)
        if resp.status_code == 404:
            return 'not_found'
        resp.raise_for_status()
        data = json.loads(resp.text)
        return data['network']['status']
    
    def createSubNet(self, neutronEndpoint, token, subnet_data):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.post(neutronEndpoint + self.create_subnet, data=json.dumps(subnet_data), headers=headers)
        resp.raise_for_status()
        return json.loads(resp.text)
    
    def deleteSubNet(self, neutronEndpoint, token, subnet_id):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.delete(neutronEndpoint + (self.delete_subnet %  subnet_id), headers=headers)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp
    
    def getSubNetStatus(self, neutronEndpoint, token, subnet_id):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.get(neutronEndpoint + (self.get_subnet_status % subnet_id), headers=headers)
        if resp.status_code == 404:
            return 'not_found'
        resp.raise_for_status()
        return 'ACTIVE'
    
    def getNetworks(self, neutronEndpoint, token):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.get(neutronEndpoint + self.get_networks, headers=headers)
        resp.raise_for_status()
        return resp.text
    
    def getPorts(self, neutronEndpoint, token):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.get(neutronEndpoint + self.get_ports, headers=headers)
        resp.raise_for_status()
        return resp.text
    
    def createPort(self, neutronEndpoint, token, port_data):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.post(neutronEndpoint + self.get_ports, data=json.dumps(port_data), headers=headers)
        resp.raise_for_status()
        return json.loads(resp.text)
    
    def deletePort(self, neutronEndpoint, token, port_id):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.delete(neutronEndpoint + self.get_ports + "/" + port_id, headers=headers)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp
    
    def getPortStatus(self, neutronEndpoint, token, port_id):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.get(neutronEndpoint + (self.get_port_status % port_id), headers=headers)
        if resp.status_code == 404:
            return 'not_found'
        resp.raise_for_status()
        data = json.loads(resp.text)
        return data['port']['status']