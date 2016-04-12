'''
Created on 18 set 2015

@author: Andrea
'''

from sql.user import User
from service_layer_application_core.exception import UnauthorizedRequest

class UserData(object):
    
    def __init__(self, usr, pwd, tnt):
        self.username = usr
        self.password = pwd
        self.tenant = tnt
    
    def getUserID(self):
        return User().getUser(self.username).id

class UserAuthentication(object):
    
    def authenticateUserFromRESTRequest(self, request):
        
        username = request.get_header("X-Auth-User")
        password = request.get_header("X-Auth-Pass")
        tenant = request.get_header("X-Auth-Tenant")  
        
        return self.authenticateUserFromCredentials(username, password, tenant)
    
    def authenticateUserFromCredentials(self, username, password, tenant):
        if username is None or password is None or tenant is None:
                raise UnauthorizedRequest('Authentication credentials required')
        
        user = User().getUser(username)
        if user.password == password:
            tenantName = User().getTenantName(user.tenant_id)
            if tenantName == tenant:
                userobj = UserData(username, password, tenant)
                return userobj
        raise UnauthorizedRequest('Invalid authentication credentials')
    