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

'''
######################################################################################################
############################    OpenDaylight Helium REST calls        ################################
######################################################################################################
'''
class ODL(object):
    endpoint8080 = ODL_ENDPOINT
    endpoint8181 = ODL_ENDPOINT2
    odl_nodes_path = "/restconf/operational/opendaylight-inventory:nodes"
    odl_topology_path = "/restconf/operational/network-topology:network-topology/"
    odl_flows_path = "/restconf/config/opendaylight-inventory:nodes"
    odl_node="/node"
    odl_flow="/table/0/flow/"
    
    #Credential for authentication on OpenDaylight controller
    odl_user = ODL_USER
    odl_pass = ODL_PASS
    
    def getNodes(self):
        '''
        Deprecated with Cisco switches because response is not a valid JSON
        '''
        headers = {'Accept': 'application/json'}
        url = self.endpoint8080+self.odl_nodes_path
        resp = requests.get(url, headers=headers, auth=(self.odl_user, self.odl_pass))
        resp.raise_for_status()
        return resp.text
    
    def getTopology(self):
        '''
        Get the entire topology comprensive of hosts, switches and links (JSON)
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error
        '''
        headers = {'Accept': 'application/json'}
        url = self.endpoint8080+self.odl_topology_path
        resp = requests.get(url, headers=headers, auth=(self.odl_user, self.odl_pass))
        resp.raise_for_status()
        return resp.text
    
    def createFlow(self, jsonFlow, switch_id, flow_id):
        '''
        Create a flow on the switch selected (Currently using OF1.0)
        Args:
            jsonFlow:
                JSON structure which describes the flow specifications
            switch_id:
                OpenDaylight id of the switch (example: openflow:1234567890)
            flow_id:
                OpenFlow id of the flow
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error
        '''
        headers = {'Accept': 'application/json', 'Content-type':'application/json'}
        url = self.endpoint8181+self.odl_flows_path+self.odl_node+"/"+str(switch_id)+self.odl_flow+str(flow_id)
        resp = requests.put(url,jsonFlow,headers=headers, auth=(self.odl_user, self.odl_pass))
        resp.raise_for_status()
        return resp.text
    
    def deleteFlow(self, switch_id, flow_id):
        '''
        Delete a flow
        Args:
            switch_id:
                OpenDaylight id of the switch (example: openflow:1234567890)
            flow_id:
                OpenFlow id of the flow
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error
        '''
        headers = {'Accept': 'application/json', 'Content-type':'application/json'}
        url = self.endpoint8181+self.odl_flows_path+self.odl_node+"/"+switch_id+self.odl_flow+str(flow_id)
        resp = requests.delete(url,headers=headers, auth=(self.odl_user, self.odl_pass))
        resp.raise_for_status()
        return resp.text

'''
######################################################################################################
###############################   OpenStack Heat REST calls        ###################################
######################################################################################################
'''
class Heat(object):
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
                Keystone token for the authentication
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
                Keystone token for the authentication
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
                Keystone token for the authentication
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
                Keystone token for the authentication
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
                Keystone token for the authentication
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
                Keystone token for the authentication
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
                Keystone token for the authentication
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

'''
######################################################################################################
##############################    OpenStack Nova REST calls        ###################################
######################################################################################################
'''
class Nova(object):   
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
                Keystone token for the authentication
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
        '''
        Create and instantiate a server and return details
        Args:
            novaEndpoint:
                The endpoint to the nova server (example: http://serverAddr:novaport/v2/<tenant-ID>)
            token:
                Keystone token for the authentication
            server_data:
                JSON structure which describes the server (see http://developer.openstack.org/api-ref-compute-v2.html)
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error or the token is expired
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.post(novaEndpoint + self.addServer, data=json.dumps(server_data), headers=headers)
        resp.raise_for_status()
        return json.loads(resp.text)
    
    def getServerStatus(self, novaEndpoint, token, server_id):
        '''
        Get the status of a specific server (RUNNING, ERROR, etc..)
        Args:
            novaEndpoint:
                The endpoint to the nova server (example: http://serverAddr:novaport/v2/<tenant-ID>)
            token:
                Keystone token for the authentication
            server_id:
                OpenStack internal id of the server
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error or the token is expired
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.get(novaEndpoint + self.addServer + "/" + server_id, headers=headers)
        resp.raise_for_status()
        data = json.loads(resp.text)
        return data['server']['status']
    
    def deleteServer(self, novaEndpoint, token, server_id):
        '''
        Delete a specific server
        Args:
            novaEndpoint:
                The endpoint to the nova server (example: http://serverAddr:novaport/v2/<tenant-ID>)
            token:
                Keystone token for the authentication
            server_id:
                OpenStack internal id of the server
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error or the token is expired
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.delete(novaEndpoint + self.addServer + "/" + server_id, headers=headers)
        resp.raise_for_status()
        return resp

'''
######################################################################################################
##############################    OpenStack Glance REST calls        #################################
######################################################################################################
'''       
class Glance(object):

    def getImage(self, imageURI, token):
        '''
        Get the image JSON description from the OpenStack URI
        Args:
            imageURI:
                Glance URI of the image (example: "http://server:9292/v2/images/16e08440-5235-4d94-94bf-7a57866b58eb")
            token:
                Keystone token for the authentication
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error or the token is expired
        '''         
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.get(imageURI, headers=headers)
        resp.raise_for_status()
        data = json.loads(resp.text)
        return data

'''
######################################################################################################
##############################    OpenStack Neutron REST calls        ################################
######################################################################################################
'''
class Neutron(object):
    get_networks = "v2.0/networks"
    get_ports = "v2.0/ports"
    
    def getNetworks(self, neutronEndpoint, token):
        '''
        Get a JSON list of Neutron networks
        Args:
            neutronEndpoint:
                The endpoint to the neutron server (example: http://serverAddr:neutronport)
            token:
                Keystone token for the authentication
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error or the token is expired
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.get(neutronEndpoint + self.get_networks, headers=headers)
        resp.raise_for_status()
        return resp.text
    
    def getPorts(self, neutronEndpoint, token):
        '''
        Get a JSON list of Neutron ports
        Args:
            neutronEndpoint:
                The endpoint to the neutron server (example: http://serverAddr:neutronport)
            token:
                Keystone token for the authentication
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error or the token is expired
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.get(neutronEndpoint + self.get_ports, headers=headers)
        resp.raise_for_status()
        return resp.text
    
    def createPort(self, neutronEndpoint, token, port_data):
        '''
        Create a Neutron port and return details (JSON)
        Args:
            neutronEndpoint:
                The endpoint to the neutron server (example: http://serverAddr:neutronport)
            token:
                Keystone token for the authentication
            port_data:
                JSON structure which represents the port and its parameters (http://developer.openstack.org/api-ref-networking-v2.html)
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error or the token is expired
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.post(neutronEndpoint + self.get_ports, data=json.dumps(port_data), headers=headers)
        resp.raise_for_status()
        return json.loads(resp.text)
    
    def deletePort(self, neutronEndpoint, token, port_id):
        '''
        Delete a Neutron port
        Args:
            neutronEndpoint:
                The endpoint to the neutron server (example: http://serverAddr:neutronport)
            token:
                Keystone token for the authentication
            port_id:
                OpenStack internal id of the port
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error or the token is expired
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        resp = requests.delete(neutronEndpoint + self.get_ports + "/" + port_id, headers=headers)
        resp.raise_for_status()
        return resp
    
    #TODO: API v2 calls for Networks creation and deletion 