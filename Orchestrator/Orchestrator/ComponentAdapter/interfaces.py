'''
Created on Oct 1, 2014

@author: fabiomignini
'''

from abc import ABCMeta, abstractmethod, abstractproperty

class OrchestratorInterface:
    '''
    Abstract class that defines the interface to be implemented on the component adapters
    '''
    __metaclass__ = ABCMeta
    
    @abstractproperty
    def URI(self):
        pass
    
    @abstractmethod
    def getStatus(self, session_id, node):
        '''
        Returns the status of the nffg resources
        '''
        pass
    
    @abstractmethod
    def updateProfile(self, new_nf_fg, old_nf_fg, node):
        '''
        Method to use to update a User Profile Graph
        Args:
            new_nffg:
                Object of the Class Common.NF_FG.nf_fg.NF_FG
            old_nffg:
                Object of the Class Common.NF_FG.nf_fg.NF_FG
            node:
                Object of the class Common.SQL.node.NodeModel
            Exceptions:
                Raise some exception to be captured
        '''
        pass
    
    @abstractmethod
    def deinstantiateProfile(self, nffg, node):
        '''
        Method used to de-instantiate the User Profile Graph
        Args:
            nffg:
                Object of the Class Common.NF_FG.nf_fg.NF_FG
            node_endpoint:
                Object of the class Common.SQL.node.NodeModel
            Exceptions:
                Raise some exception to be captured
        '''
        pass
    
        
    @abstractmethod
    def instantiateProfile(self,  nffg, node):
        '''
        Method to use to instantiate the User Profile Graph
        Args:
            nffg:
                Object of the Class Common.NF_FG.nf_fg.NF_FG
            node:
                Object of the class Common.SQL.node.NodeModel
            Exceptions:
                Raise some exception to be captured
        '''
        pass

