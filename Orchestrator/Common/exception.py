class NoUserNodeDefined(Exception):
    def __init__(self, message):
        self.message = message
        
    def get_mess(self):
        return self.message

class EndpointConnectionError(Exception):
    def __init__(self, message):
        self.message = message
        
    def get_mess(self):
        return self.message
    
class NodeNotFound(Exception):
    def __init__(self, message):
        self.message = message
        
    def get_mess(self):
        return self.message

class StackError(Exception):
    def __init__(self, message):
        self.message = message
        
    def get_mess(self):
        return self.message


class ResourceAlreadyExistsOnNode(Exception):
    def __init__(self, message):
        self.message = message
        
    def get_mess(self):
        return self.message
    
class WrongConfigurationFile(Exception):
    def __init__(self, message):
        self.message = message
        
    def get_mess(self):
        return self.message
    
class NoHeatPortTranslationFound(Exception):
    def __init__(self, message):
        self.message = message
        
    def get_mess(self):
        return self.message

class NoMacAddress(Exception):
    def __init__(self, message):
        self.message = message
        
    def get_mess(self):
        return self.message
    
class NoPreviousDeviceFound(Exception):
    def __init__(self, message):
        self.message = message
        
    def get_mess(self):
        return self.message
    
class InfoNotFound(Exception): 
    def __init__(self, message):
        self.message = message
        
    def get_mess(self):
        return self.message   
    
class sessionNotFound(Exception):
    def __init__(self, message):
        self.message = message
        
    def get_mess(self):
        return self.message

class ingoingFlowruleMissing(Exception):
    def __init__(self, message):
        self.message = message
    
    def get_mess(self):
        return self.message

class maximumNumberOfVNFInGraph(Exception):
    def __init__(self, message):
        self.message = message
    
    def get_mess(self):
        return self.message

class wrongRequest(Exception):
    def __init__(self, message):
        self.message = message
    
    def get_mess(self):
        return self.message
    
class unauthorizedRequest(Exception):
    def __init__(self, message):
        self.message = message
    
    def get_mess(self):
        return self.message
    
class wrongConnectionBetweenEndpoints(Exception):
    def __init__(self, message):
        self.message = message
    
    def get_mess(self):
        return self.message
    
class    ManifestValidationError(Exception):
    def __init__(self, message):
        self.message = message
    
    def get_mess(self):
        return self.message
    
class    NF_FGValidationError(Exception):
    def __init__(self, message):
        self.message = message
    
    def get_mess(self):
        return self.message
    
class WrongNumberOfPorts(Exception):
    def __init__(self, message):
        self.message = message
    
    def get_mess(self):
        return self.message
    
class WrongPortID(Exception):
    def __init__(self, message):
        self.message = message
    
    def get_mess(self):
        return self.message
    
class PortLabelNotFound(Exception):
    def __init__(self, message):
        self.message = message
    
    def get_mess(self):
        return self.message
    
class Wrong_ISP_Graph(Exception):
    def __init__(self, message):
        self.message = message
    
    def get_mess(self):
        return self.message
    
class ISPNotDeployed(Exception):
    def __init__(self, message):
        self.message = message
    
    def get_mess(self):
        return self.message

class connectionsError(Exception):
    def __init__(self, message):
        self.message = message
    
    def get_mess(self):
        return self.message
