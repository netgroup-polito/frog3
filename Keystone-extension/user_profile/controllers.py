'''
Created on May 15, 2014

@author: fmignini
'''


from validator import UserProfileValidator
from keystone.openstack.common import log



from keystone import identity
from keystone import exception

LOG = log.getLogger(__name__)

from keystone.common import controller
from keystone.common import dependency
     
 
@dependency.requires('user_profile_api','policy_api')       
class UserProfileController(controller.V3Controller,identity.controllers.User): 
    
   
    def delete_user_profile(self, context, user_id):
        """ user-token pair control """
        token_id = context.get('token_id')
        
        token_ref = self.token_api.get_token(token_id)
        user_id_from_token = token_ref['user']['id']

        if not self._is_admin(context):
            if user_id_from_token != user_id:
                raise exception.Forbidden('Token belongs to another user')
        
        self.user_profile_api.delete_last_user_profile(user_id)
        
        return {"user_profile":"deleted"}
        
    """
    def update_user_profile(self, context, user_id, profile):
        token_id = context.get('token_id')
        
        token_ref = self.token_api.get_token(token_id)
        user_id_from_token = token_ref['user']['id']

        if not self._is_admin(context):
            if user_id_from_token != user_id:
                raise exception.Forbidden('Token belongs to another user')
        
        v = UserProfileValidator()
        v.validate_user_profile(profile)
        
        user_profile = self.user_profile_api.update_last_user_profile(user_id,profile)
        
        return {'profile': user_profile}
    """
   
    def get_user_profile(self, context, user_id):
        
        """ user-token pair control """
        token_id = context.get('token_id')
        
        token_ref = self.token_api.get_token(token_id)
        user_id_from_token = token_ref['user']['id']
        
        if not self._is_admin(context):
            if user_id_from_token != user_id:
                raise exception.Forbidden('Token belongs to another user')
        
        
        user_profile = self.user_profile_api.get_last_user_profile(user_id)
        
        
        return {'profile': user_profile}
    
    
    def create_user_profile(self, context, user_id, profile):
        """ user-token pair control """
        token_id = context.get('token_id')
        
        token_ref = self.token_api.get_token(token_id)
        user_id_from_token = token_ref['user']['id']

        if not self._is_admin(context):
            if user_id_from_token != user_id:
                raise exception.Forbidden('Token belongs to another user')
        
        v = UserProfileValidator()
        v.validate_user_profile(profile)
        

        user_profile = self.user_profile_api.create_user_profile(context, user_id, profile)
        return {'profile': user_profile}
    
    def _is_admin(self, context):
        """Wrap admin assertion error return statement.

        :param context: standard context
        :returns: bool: success

        """
        try:
            # NOTE(morganfainberg): policy_api is required for assert_admin
            # to properly perform policy enforcement.
            self.assert_admin(context)
            return True
        except exception.Forbidden:
            return False

