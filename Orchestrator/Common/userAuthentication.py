'''
Created on 18 set 2015

@author: Andrea
'''
import falcon

from Common.SQL.user import User

class UserData(object):
    
    def __init__(self, usr, pwd, tnt):
        self.username = usr
        self.password = pwd
        self.tenant = tnt

class UserAuthentication(object):
    
    def authenticateUserFromRESTRequest(self, request):
        
        username = request.get_header("X-Auth-User")
        password = request.get_header("X-Auth-Pass")
        tenant = request.get_header("X-Auth-Tenant")  
        
        return self.authenticateUserFromCredentials(username, password, tenant)
        
    
    def authenticateUserFromCredentials(self, username, password, tenant):
        
        if username is None or password is None or tenant is None:
                description = "{\"error\":{\"message\":\"Please provide auth credentials\",\"code\":\"401\",\"title\":\"Unauthorized\"}}"            
                raise falcon.HTTPUnauthorized('Authentication credentials required',
                                              description,
                                              href='http://docs.example.com/auth')
        
        user = User().getUser(username)
        if user.password == password:
            tenantName = User().getTenantName(user.tenant)
            if tenantName == tenant:
                userobj = UserData(username, password, tenant)
                return userobj
        
        description = "{\"error\":{\"message\":\"Invalid auth credentials\",\"code\":\"401\",\"title\":\"Unauthorized\"}}"            
        raise falcon.HTTPUnauthorized('Invalid authentication credentials',
                                        description,
                                        href='http://docs.example.com/auth')
    