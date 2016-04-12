class ISPNotDeployed(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(ISPNotDeployed, self).__init__(message)
    
    def get_mess(self):
        return self.message
    
class ControllerNotFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(ControllerNotFound, self).__init__(message)
        
    def get_mess(self):
        return self.message
    
class NodeNotFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(NodeNotFound, self).__init__(message)
        
    def get_mess(self):
        return self.message

class RequestValidationError(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(RequestValidationError, self).__init__(message)
        
    def get_mess(self):
        return self.message
    
class UnauthorizedRequest(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(UnauthorizedRequest, self).__init__(message)
        
    def get_mess(self):
        return self.message
    
class TenantNotFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(TenantNotFound, self).__init__(message)
        
    def get_mess(self):
        return self.message

class UserNotFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(UserNotFound, self).__init__(message)
        
    def get_mess(self):
        return self.message

class UserLocationNotFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(UserLocationNotFound, self).__init__(message)
        
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

class SessionNotFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(SessionNotFound, self).__init__(message)
        
    def get_mess(self):
        return self.message
