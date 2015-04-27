'''
Created on May 15, 2014

@author: fmignini
'''

from keystone.common import wsgi
from keystone.contrib.user_profile import controllers
from keystone.openstack.common import log


LOG = log.getLogger(__name__)



class CrudExtension(wsgi.ExtensionRouter):
    """

    Provides a bunch of CRUD operations for internal data types.

    """

    def add_routes(self, mapper):
        userprofile_controller = controllers.UserProfileController()
        
        mapper.connect(
            '/OS-UPROF/profile/users/{user_id}',
            controller=userprofile_controller,
            action='create_user_profile',
            conditions=dict(method=['POST']))
            
        mapper.connect(
            '/OS-UPROF/profile/users/{user_id}',
            controller=userprofile_controller,
            action='get_user_profile',
            conditions=dict(method=['GET']))
        
        mapper.connect(
            '/OS-UPROF/profile/users/{user_id}',
            controller=userprofile_controller,
            action='delete_user_profile',
            conditions=dict(method=['DELETE']))
        """
        mapper.connect(
            '/OS-UPROF/profile/users/{user_id}',
            controller=userprofile_controller,
            action='update_user_profile',
            conditions=dict(method=['PUT']))
        """