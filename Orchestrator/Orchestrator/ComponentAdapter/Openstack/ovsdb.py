'''
Created on Jul 9, 2015

@author: fabiomignini
'''
from Orchestrator.ComponentAdapter.Openstack.rest import ODL
from Common.exception import NodeNotFound
from Common.config import Configuration
import json, logging

INTEGRATION_BRIDGE = Configuration().INTEGRATION_BRIDGE

class OVSDB(object):
    def __init__(self, ip_address = None):
        nodes = json.loads(ODL().getNodes())['node']
        node_id = None
        for node in nodes:
            if node['type'] == "OVS":
                if ip_address is not None and ip_address == node['id'].split(':')[0]:
                    node_id = node['id']
        if node_id is None:
            raise NodeNotFound("Node "+str(ip_address)+" not found.")
        self.node_ip = node_id.split(":")[0]
        self.ovsdb_port = node_id.split(":")[1]
    
    def getBridgeDatapath_id(self, port_name):
        logging.debug("datapath id - portname - "+str(port_name))
        portUUID = self.getPortUUID(port_name)
        logging.debug("datapath id - portUUID - "+str(portUUID))
        datapath_id = self._getBridgeDatapath_id(portUUID)
        logging.debug("datapath id - datapath_id - "+str(datapath_id))
        return datapath_id
        
    def _getBridgeDatapath_id(self, portUUID):
        bridges = ODL().getBridges(self.node_ip, self.ovsdb_port)
        json_object = json.loads(bridges)['rows']
        for attribute, value in json_object.iteritems():
            for ports in value['ports'][1]:
                if ports[1] == portUUID:               
                    return value['datapath_id'][1][0]
            
    def getBridgeUUID(self, bridge_name):
        bridges = ODL().getBridges(self.node_ip, self.ovsdb_port)
        json_object = json.loads(bridges)['rows']
        for attribute, value in json_object.iteritems():
            if value['name'] == bridge_name:
                return attribute     
            
    def getBridgeDPID(self, bridge_name):
        bridges = ODL().getBridges(self.node_ip, self.ovsdb_port)
        json_object = json.loads(bridges)['rows']
        for attribute, value in json_object.iteritems():
            if value['name'] == bridge_name:
                return value['datapath_id'][1][0]  
        
    def getPortUUID(self, port_name): 
        ports = ODL().getPorts(self.node_ip, self.ovsdb_port)
        ports = json.loads(ports)['rows']
        for attribute, value in ports.iteritems():    
            if value['name'] == port_name:
                return attribute

    def getInterfaceUUID(self, port_id, port_name):
        interfaces = ODL().getInterfaces(port_id, self.node_ip, self.ovsdb_port)
        interfaces = json.loads(interfaces)['rows']
        for attribute, value in interfaces.iteritems():  
            if value['name'] == port_name:
                return attribute
            
    def createPort(self, port_name, bridge_id):
        if self.getPortUUID(port_name) is None:
            ODL().createPort(port_name, bridge_id, self.node_ip, self.ovsdb_port)
    
    def createBridge(self, bridge_name):
        if self.getBridgeUUID(bridge_name) is None:
            ODL().createBridge(bridge_name, self.node_ip, self.ovsdb_port)
        
    def deletePort(self, port_name):
        port_id = self.getPortUUID(port_name)
        if port_id is not None:
            ODL().deletePort(port_id, self.node_ip, self.ovsdb_port)
            
    def deleteBridge(self, bridge_name):
        bridge_id = self.getBridgeUUID(bridge_name)
        if bridge_id is not None:
            ODL().deleteBridge(bridge_id, self.node_ip, self.ovsdb_port)
