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
    def getStatus(self, session_id, node_endpoint):
        '''
        Returns the status of the nffg resources
        '''
        pass
    
    @abstractmethod
    def updateProfile(self, nf_fg_id, new_profile, old_profile):
        pass
    
    @abstractmethod
    def deinstantiateProfile(self, nffg, node_endpoint):
        '''
        Method used to de-instantiate the User Profile Graph
        Args:
            nffg:
                Object of the Class Common.NF_FG.nf_fg.NF_FG
            node_endpoint:
                End point used to contact the infrastructure layer
            Exceptions:
                Raise some exception to be captured
        '''
        pass
    
        
    @abstractmethod
    def instantiateProfile(self,  nffg, node_endpoint):
        '''
        Method to use to instantiate the User Profile Graph
        Args:
            nffg:
                Object of the Class Common.NF_FG.nf_fg.NF_FG
            node_endpoint:
                End point used to contact the infrastructure layer
            Exceptions:
                Raise some exception to be captured
        '''
        pass

