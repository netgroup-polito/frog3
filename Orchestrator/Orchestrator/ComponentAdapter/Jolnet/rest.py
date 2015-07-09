'''
Created on 13/apr/2015

@author: vida
'''
import requests
import json
from Common.config import Configuration

ODL_ENDPOINT = Configuration().ODL_ENDPOINT
ODL_ENDPOINT2 = Configuration().ODL_ENDPOINT2
ODL_USER = Configuration().ODL_USER
ODL_PASS = Configuration().ODL_PASSWORD

class ODL(object):
    endpoint8080 = ODL_ENDPOINT
    endpoint8181 = ODL_ENDPOINT2
    odl_nodes_path = "/restconf/operational/opendaylight-inventory:nodes"
    odl_topology_path = "/restconf/operational/network-topology:network-topology/"
    odl_flows_path = "/restconf/config/opendaylight-inventory:nodes"
    odl_node="/node"
    odl_flow="/table/0/flow/"
    
    #Credential for authentication on Opendaylight controller
    odl_user = ODL_USER
    odl_pass = ODL_PASS
    
    def getNodes(self):
        '''
        Deprecated with Cisco 3850 switches because response is not a valid JSON
        '''
        headers = {'Accept': 'application/json'}
        url = self.endpoint8080+self.odl_nodes_path
        resp = requests.get(url, headers=headers, auth=(self.odl_user, self.odl_pass))
        resp.raise_for_status()
        return resp.text
    
    def getTopology(self):
        '''
        Gets the entire topology comprensive of hosts, switches and links
        '''
        headers = {'Accept': 'application/json'}
        url = self.endpoint8080+self.odl_topology_path
        resp = requests.get(url, headers=headers, auth=(self.odl_user, self.odl_pass))
        resp.raise_for_status()
        return resp.text
    
    def createFlow(self, jsonFlow, switch_id, flow_id):
        '''
        Creates a flow (described by the json passed) on the switch passed
        '''
        headers = {'Accept': 'application/json', 'Content-type':'application/json'}
        url = self.endpoint8181+self.odl_flows_path+self.odl_node+"/"+str(switch_id)+self.odl_flow+str(flow_id)
        resp = requests.put(url,jsonFlow,headers=headers, auth=(self.odl_user, self.odl_pass))
        resp.raise_for_status()
        return resp.text
    
    def deleteFlow(self, switch_id, flow_id):
        '''
        Deletes a flow identified by the switch and the id
        '''
        headers = {'Accept': 'application/json', 'Content-type':'application/json'}
        url = self.endpoint8181+self.odl_flows_path+self.odl_node+"/"+switch_id+self.odl_flow+str(flow_id)
        resp = requests.delete(url,headers=headers, auth=(self.odl_user, self.odl_pass))
        resp.raise_for_status()
        return resp.text
    
    #TODO: aggiungere chiamate AD-SAL per host tracking???

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
        resp = requests.get(heatEndpoint+self.getStackPath, headers=headers)
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
        resp = requests.post(heatEndpoint+self.createStackPath, data=json.dumps(stack_data), headers=headers)
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
        resp = requests.put(heatEndpoint+(self.updateStackPath % (stackName, stackID)), data=json.dumps(stack_data), headers=headers)
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
        resp = requests.delete(heatEndpoint+(self.deleteStackPath % (stackName, stackID)), headers=headers)
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
        resp = requests.get(heatEndpoint+(self.getStackIDPath % stackName), headers=headers)
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
        resp = requests.get(heatEndpoint+(self.getStackIDPath % stackName), headers=headers)
        resp.raise_for_status()
        data = json.loads(resp.text)
        return data['stack']['stack_status']

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
        resp = requests.get(heatEndpoint+(self.stackResourcesPath % (stackName, stackID)), headers=headers)
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
    
    def getAvailabilityZones(self, novaEndpoint, token):
        """
        Call usable only for Openstack admin users
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
        resp = requests.get(novaEndpoint+self.getAvailabilityZonesPath, headers=headers)
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
        resp = requests.get(novaEndpoint+self.getFlavorsDetail, params=data, headers=headers)
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
        resp.raise_for_status()
        return resp
       
class Glance(object):
    '''
    Class used for Glance API
    '''   
    def getImage(self, imageURI, token):
        '''
        Return the name of an image from the URI
        '''         
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.get(imageURI, headers=headers)
        resp.raise_for_status()
        data = json.loads(resp.text)
        return data

class Neutron(object):
    '''
    Class used for Neutron API
    '''
    get_networks = "v2.0/networks"
    get_ports = "v2.0/ports"
    
    def getNetworks(self, neutronEndpoint, token):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.get(neutronEndpoint + self.get_networks, headers=headers)
        resp.raise_for_status()
        return resp.text
    
    def createNetwork(self, neutronEndpoint, token, network_data):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
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
