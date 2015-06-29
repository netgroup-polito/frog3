'''
Created on Oct 1, 2014

@author: fabiomignini
'''

from abc import ABCMeta, abstractmethod, abstractproperty

class OrchestratorInterface:
    '''
    Abstract class that defines the interface to be implemented on the other orchestrator
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
    def deinstantiateProfile(self, token, session_id):
        '''
        Method used to de-instantiate the User Profile Graph
        Args:
            profile:
                JSON Object for the User Profile (it should be a map that follow the User Profile Graph Schema
            token:
                The authentication token to use for the REST call
            Exceptions:
                Raise some exception to be captured
        '''
        pass
    
        
    @abstractmethod
    def instantiateProfile(self, profile_id, profile = None):
        '''
        Method to use to instantiate the User Profile Graph
        Args:
            profile:
                JSON Object for the User Profile (it should be a map that follow the User Profile Graph Schema
            token:
                The authentication token to use for the REST call
            Exceptions:
                Raise some exception to be captured
        '''
        pass

