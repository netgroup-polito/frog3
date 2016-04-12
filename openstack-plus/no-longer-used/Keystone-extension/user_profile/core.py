'''
Created on May 13, 2014

@author: fmignini
'''

import abc
import six





from keystone.common import extension
from keystone.openstack.common import log


from keystone.common import dependency
from keystone.common import manager
from keystone import config

from keystone import exception

CONF = config.CONF
LOG = log.getLogger(__name__)

EXTENSION_DATA = {
        'name': 'OpenStack Keystone User Profile',
        'namespace': 'http://docs.openstack.org/identity/api/ext/'
                     'userprofile',
        'alias': 'OS-UPROF',
        'updated': '2014-13-11T17:14:00-00:00',
        'description': 'OpenStack extensions to Keystone v2.0 API '
                       'create a user profile.',
        'links': [
            {
                'rel': 'describedby',
                # TODO(dolph): link needs to be revised after
                #              bug 928059 merges
                'type': 'text/html',
                'href': 'svn...',
            }
        ]}
extension.register_admin_extension(EXTENSION_DATA['alias'], EXTENSION_DATA)
extension.register_public_extension(EXTENSION_DATA['alias'], EXTENSION_DATA)

@dependency.provider('user_profile_api')
class Manager(manager.Manager):
    """Example Manager.

    See :mod:`keystone.common.manager.Manager` for more details on
    how this dynamically calls the backend.

    """
    
    def __init__(self):
        super(Manager, self).__init__(CONF.user_profile.driver)
        """super(Manager, self).__init__('keystone.contrib.user_profile.core.Driver')"""
        
    def create_user_profile(self, context, user_id, profile):
        return self.driver.create_user_profile(context, user_id, profile)
        
    def get_last_user_profile(self, user_id):
        return self.driver.get_last_user_profile(user_id)
    
    def delete_last_user_profile(self, user_id):
        return self.driver.delete_last_user_profile(user_id)
    """
    def update_last_user_profile(self, user_id, profile):
        return self.driver.update_last_user_profile(user_id, profile)
    """
    
    

@six.add_metaclass(abc.ABCMeta)
class Driver(object):
    """Interface description for Example driver."""

    @abc.abstractmethod
    def create_user_profile(self,context, user_id, profile):
        raise exception.NotImplemented()

    @abc.abstractmethod
    def get_last_user_profile(self, user_id):   
        raise exception.NotImplemented()
    
    @abc.abstractmethod
    def delete_last_user_profile(self, user_id):
        raise exception.NotImplemented()
    """
    @abc.abstractmethod
    def update_last_user_profile(self, user_id, profile):
        raise exception.NotImplemented()
    """
