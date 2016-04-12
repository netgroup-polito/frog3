'''
Created on Oct 1, 2014

@author: fabiomignini
'''
import json
import requests
import logging

class Unify(object):
    '''
    class used to send REST call to the Unify node
    '''
    
    deleteFlowPath="/graph/%s/%s"
    createGraphPath="/graph/%s"
    getInterfacesPath="/interfaces"

    def checkGraph(self, unifyEndpoint, graphID, unifyJSON=""):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        resp = requests.get(unifyEndpoint+(self.createGraphPath % graphID), headers=headers)
        resp.raise_for_status()
        logging.debug(str(resp.content))

    def instantiateGraph(self, unifyEndpoint, graphID, unifyJSON):
        '''
        Instantiate the user graph on a Unify node
        Args:
            unifyEndpoint:
                The address of the Unify node to contact
            graphID:
                The ID of the graps to instatiate
            unifyJSON:
                The JSON of the graph in the Unify format
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        resp = requests.put(unifyEndpoint+(self.createGraphPath % graphID), data=json.dumps(unifyJSON), headers=headers)
        resp.raise_for_status()
        logging.debug(str(resp.content))
        return resp
    
    def deinstantiateGraph(self, unifyEndpoint, graphID):
        '''
        Deinstantiate the user graph on a Unify node
        Args:
            unifyEndpoint:
                The address of the Unify node to contact
            graphID:
                The ID of the graps to instatiate
            unifyJSON:
                The JSON of the graph in the Unify format
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        resp = requests.delete(unifyEndpoint+(self.createGraphPath % graphID), headers=headers)
        resp.raise_for_status()
        return resp
    
    def deleteFlow(self, unifyEndpoint, graphID,ruleID):
        '''
        Delete only a specific rule in the graph
        Args:
            ruleID:
                The ID of the rule
            unifyEndpoint:
                The address of the Unify node to contact
            graphID:
                The ID of the graps to instatiate
            
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        path = unifyEndpoint+"/graph/"+graphID+"/"+ruleID
        logging.debug("path: "+str(path))
        resp = requests.delete(path, headers=headers)
        resp.raise_for_status()
        return resp
    
    def updateGraph(self, unifyEndpoint, graphID, unifyJSON):
        '''
        Deinstantiate the user graph on a Unify node
        Args:
            unifyEndpoint:
                The address of the Unify node to contact
            graphID:
                The ID of the graps to instatiate
            unifyJSON:
                The JSON of the graph in the Unify format
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        resp = requests.put(unifyEndpoint+(self.createGraphPath % graphID), data=json.dumps(unifyJSON), headers=headers)
        resp.raise_for_status()
        return resp
    
    def getInterfaces(self, unifyEndpoint):
        '''
        Obtain the interfaces list of the unify node
        Args:
            unifyEndpoint:
                The address of the Unify node to contact
        '''
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        resp = requests.get(unifyEndpoint+self.getInterfacesPath, headers=headers)
        resp.raise_for_status()
        return json.loads(resp.text())
        #return {"interfaces": [{"type": "edge", "name": "eth0"}, {"type": "edge", "name": "eth1"}]}