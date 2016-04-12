'''
Created on Oct 1, 2014

@author: fabiomignini
'''


import requests
import json
import logging
import falcon

from orchestrator_core.component_adapter.openstack_common.authentication import KeystoneAuthentication
from orchestrator_core.config import Configuration

ORCH_PASSWORD = Configuration().ORCH_PASSWORD
ORCH_TENANT = Configuration().ORCH_TENANT
ORCH_USERNAME = Configuration().ORCH_USERNAME

class User(object):
    def __init__(self, keystone_server=None, username=None, password=None, tenant_name=None, email=None, description=None, role_name=None):
        '''
        Constructor
        '''
        if keystone_server is not None:
            self.keystone_server = keystone_server
            self.username = username
            self.password = password
            self.tenant_name = tenant_name
            self.email = email
            self.description = description
            self.role_name = role_name
            self.admin_token = self.get_admin_token()
        
    def controlUser(self):
        
        tenant_id = self.get_tenant_id()
        users = self.list_users_for_tenant(tenant_id)
        logging.debug("Control User - "+json.dumps(users));
        for user in users['users']:
            logging.debug("Control User  in tenant \""+str(tenant_id)+"\" - "+user['name']);
            if user['name'] == self.username:
                return True
        return False
        
    
    def controlTenant(self):
        
        tenants = self.list_tenants()
        for tenant in tenants['tenants']:
            if tenant['name'] == self.username:
                return True
        return False
            
    def createAndLinkUserTenatRole(self):        
        self.createUser()
        self.linkUserTenantRole()
        
    
    def createUser(self):
        """
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error or unauthorized credentials
        
        """
        user_path = self.keystone_server+"/v2.0/users"
        
        # Make request to keystone, to create user
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': self.admin_token}
        body_request = {"user":{"name": self.username, "email":self.email,"enabled": True, "OS-KSADM:password": self.password }}
        resp = requests.post(user_path, data=json.dumps(body_request), headers=headers)
        resp.raise_for_status()
        self.user = json.loads(resp.text)
        
    def linkUserTenantRole(self):
        """
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error or unauthorized credentials
        
        """
        tenant_id = self.get_tenant_id()
        role_id = self.get_role_id()
        user_id = self.get_user_id()
        if tenant_id is None:
            logging.debug("tenant_id is None")
        else:
            logging.debug("tenant_id : "+tenant_id)
        if role_id is None: 
            logging.debug("role_id is None")
        else:
            logging.debug("role_id : "+role_id)
        if user_id is None:
            logging.debug("user_id is None")
        else:
            logging.debug("user_id : "+user_id)
   
        # Create the link for the request
        link_path = self.keystone_server+"/v2.0/tenants/"+tenant_id+"/users/"+user_id+"/roles/OS-KSADM/"+role_id
        
        # Make request to keystone, to create user
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': self.admin_token}
        resp = requests.put(link_path, headers=headers)
        logging.debug(resp.status_code)
        resp.raise_for_status()
        self.user = json.loads(resp.text)
    
    def creatTenant(self):
        """
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error or unauthorized credentials
        
        """
        tenant_path = self.keystone_server+"/v2.0/tenants"
        
        # Make request to keystone, to create tenant
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': self.admin_token}
        body_request = {"tenant":{"name": self.tenant_name, "description": self.description,"enabled": True}}
        resp = requests.post(tenant_path, data=json.dumps(body_request), headers=headers)
        resp.raise_for_status()
        self.profile = json.loads(resp.text)
        
         
    def list_users_for_tenant(self, tenant_id):
        """
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error or unauthorized credentials
        
        """
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': self.admin_token}
        resp = requests.get(self.keystone_server+"/v2.0/tenants/"+tenant_id+"/users", headers=headers)
        resp.raise_for_status()
        return json.loads(resp.text)
    
    def list_users(self):
        """
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error or unauthorized credentials
        
        """
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': self.admin_token}
        resp = requests.get(self.keystone_server+"/v2.0/users", headers=headers)
        resp.raise_for_status()
        return json.loads(resp.text)
    
    def list_tenants(self):
        """
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error or unauthorized credentials
        
        """
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': self.admin_token}
        resp = requests.get(self.keystone_server+"/v2.0/tenants", headers=headers)
        resp.raise_for_status()
        return json.loads(resp.text)
    
    def list_role(self):
        """
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error or unauthorized credentials
        
        """
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': self.admin_token}
        resp = requests.get(self.keystone_server+"/v2.0/OS-KSADM/roles/", headers=headers)
        resp.raise_for_status()
        return json.loads(resp.text)
    
    def get_tenant_id(self):
        """
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error or unauthorized credentials
        
        """
        tenants = self.list_tenants()
        for tenant in tenants['tenants']:
            if tenant['name'] == self.tenant_name:
                return tenant['id']
    
    def get_role_id(self):
        """
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error or unauthorized credentials
        
        """
        roles = self.list_role()
        for role in roles['roles']:
            if role['name'] == self.role_name:
                return role['id']
    
    def get_user_id(self):
        """
        Exceptions:
            raise the requests.HTTPError exception connected to the REST call in case of HTTP error or unauthorized credentials
        
        """
        users = self.list_users()
        for user in users['users']:
            if user['name'] == self.username:
                return user['id']
    
    def get_admin_token(self):
        # Obtain the orchestrator_core token for user creation
        auth = KeystoneAuthentication(self.keystone_server, ORCH_TENANT, ORCH_USERNAME, ORCH_PASSWORD)
        return auth.get_token()
    
    def updateUser(self, token, user_id, timestamp, keystone_server):
        '''
         Update the field last_login in the keystone user table
        '''
         
        # Obtain the orchestrator_core token for update information about user
        auth = KeystoneAuthentication(keystone_server, ORCH_TENANT, ORCH_USERNAME, ORCH_PASSWORD)
        admin_token = auth.get_token()
        
        # Control the validity of user token (admin can perform this operation?)
        logged_user = auth.get_userID_by_token(token, admin_token)
        if logged_user != user_id:
            raise falcon.HTTPUnauthorized("Unauthorized", "You can't update data of another user")
        
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': admin_token}
        # data=json.dumps(self.authenticationData)
        resp = requests.put(keystone_server + "/v2.0/users/" + user_id, data=json.dumps({"user": {"id": user_id, "last_login": timestamp}}), headers=headers)
        resp.raise_for_status()
        
        