class UserLocationNotFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(UserLocationNotFound, self).__init__(message)
        
    def get_mess(self):
        return self.message
    
class DeletionTimeout(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(DeletionTimeout, self).__init__(message)
        
    def get_mess(self):
        return self.message
    
class NoUserNodeDefined(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(NoUserNodeDefined, self).__init__(message)
        
    def get_mess(self):
        return self.message

class EndpointConnectionError(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(EndpointConnectionError, self).__init__(message)
        
    def get_mess(self):
        return self.message
    
class NodeNotFound(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super(NodeNotFound, self).__init__(message)

        self.message = message
        
    def get_mess(self):
        return self.message

class StackError(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(StackError, self).__init__(message)
        
    def get_mess(self):
        return self.message


class ResourceAlreadyExistsOnNode(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(ResourceAlreadyExistsOnNode, self).__init__(message)
        
    def get_mess(self):
        return self.message
    
class WrongConfigurationFile(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(WrongConfigurationFile, self).__init__(message)
        
    def get_mess(self):
        return self.message
    
class NoHeatPortTranslationFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(NoHeatPortTranslationFound, self).__init__(message)
        
    def get_mess(self):
        return self.message

class NoMacAddress(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(NoMacAddress, self).__init__(message)
        
    def get_mess(self):
        return self.message
    
class NoPreviousDeviceFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(NoPreviousDeviceFound, self).__init__(message)
        
    def get_mess(self):
        return self.message
    
class InfoNotFound(Exception): 
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(InfoNotFound, self).__init__(message)
        
    def get_mess(self):
        return self.message   
    
class sessionNotFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(sessionNotFound, self).__init__(message)
        
    def get_mess(self):
        return self.message

class ingoingFlowruleMissing(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(ingoingFlowruleMissing, self).__init__(message)
    
    def get_mess(self):
        return self.message

class maximumNumberOfVNFInGraph(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(maximumNumberOfVNFInGraph, self).__init__(message)
    
    def get_mess(self):
        return self.message

class wrongRequest(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(wrongRequest, self).__init__(message)
    
    def get_mess(self):
        return self.message
    
class unauthorizedRequest(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(unauthorizedRequest, self).__init__(message)
    
    def get_mess(self):
        return self.message
    
class wrongConnectionBetweenEndpoints(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(wrongConnectionBetweenEndpoints, self).__init__(message)
    
    def get_mess(self):
        return self.message
    
class   ManifestValidationError(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(ManifestValidationError, self).__init__(message)
    
    def get_mess(self):
        return self.message
    
class    NF_FGValidationError(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(NF_FGValidationError, self).__init__(message)
    
    def get_mess(self):
        return self.message
    
class WrongNumberOfPorts(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(WrongNumberOfPorts, self).__init__(message)
    
    def get_mess(self):
        return self.message
    
class WrongPortID(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(WrongPortID, self).__init__(message)
    
    def get_mess(self):
        return self.message
    
class PortLabelNotFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(PortLabelNotFound, self).__init__(message)
    
    def get_mess(self):
        return self.message
    
class Wrong_ISP_Graph(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(Wrong_ISP_Graph, self).__init__(message)
    
    def get_mess(self):
        return self.message
    
class ISPNotDeployed(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(ISPNotDeployed, self).__init__(message)
    
    def get_mess(self):
        return self.message

class GraphError(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(GraphError, self).__init__(message)
    
    def get_mess(self):
        return self.message

class GraphNotFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(GraphNotFound, self).__init__(message)
    
    def get_mess(self):
        return self.message

class PortNotFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(PortNotFound, self).__init__(message)
    
    def get_mess(self):
        return self.message

class EndpointNotFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(EndpointNotFound, self).__init__(message)
    
    def get_mess(self):
        return self.message

class connectionsError(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(connectionsError, self).__init__(message)
    
    def get_mess(self):
        return self.message
