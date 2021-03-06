#from abc import abstractmethod
from neutron.api import extensions
#from neutron.openstack.common import jsonutils
#from neutron import wsgi
from neutron import manager
from neutron.api.v2 import base
from neutron.api.v2 import attributes

ATTR_NOT_SPECIFIED = None

RESOURCE_ATTRIBUTE_MAP = {
    attributes.FLOWRULES: {
        'id': {'allow_post': True, 'allow_put': False,
               'validate': {'type:string': None},
               'is_visible': True,
               'primary_key': True},
        'hardTimeout': {'allow_post': True, 'allow_put': True,
               'default': ATTR_NOT_SPECIFIED,
               'validate': {'type:string_or_none': None},
               'is_visible': True},
        'priority': {'allow_post': True, 'allow_put': True,
               'default': "0",
               'validate': {'type:string_or_none': None},
               'is_visible': True},
        'ingressPort': {'allow_post': True, 'allow_put': True,
               'default': None,
               'validate': {'type:string_or_none': None},
               'is_visible': True},
        'etherType': {'allow_post': True, 'allow_put': True,
               'default': ATTR_NOT_SPECIFIED,
               'validate': {'type:string_or_none': None},
               'is_visible': True},
        'vlanId': {'allow_post': True, 'allow_put': True,
               'default': ATTR_NOT_SPECIFIED,
               'validate': {'type:string_or_none': None},
               'is_visible': True},
        'vlanPriority': {'allow_post': True, 'allow_put': True,
               'default': ATTR_NOT_SPECIFIED,
               'validate': {'type:string_or_none': None},
               'is_visible': True},
        'dlSrc': {'allow_post': True, 'allow_put': True,
               'default': ATTR_NOT_SPECIFIED,
               'validate': {'type:string_or_none': None},
               'is_visible': True},
        'dlDst': {'allow_post': True, 'allow_put': True,
               'default': ATTR_NOT_SPECIFIED,
               'validate': {'type:string_or_none': None},
               'is_visible': True},
        'nwSrc': {'allow_post': True, 'allow_put': True,
               'default': ATTR_NOT_SPECIFIED,
               'validate': {'type:string_or_none': None},
               'is_visible': True},
        'nwDst': {'allow_post': True, 'allow_put': True,
               'default': ATTR_NOT_SPECIFIED,
               'validate': {'type:string_or_none': None},
               'is_visible': True},
        'tosBits': {'allow_post': True, 'allow_put': True,
               'default': ATTR_NOT_SPECIFIED,
               'validate': {'type:string_or_none': None},
               'is_visible': True},
        'tpSrc': {'allow_post': True, 'allow_put': True,
               'default': ATTR_NOT_SPECIFIED,
               'validate': {'type:string_or_none': None},
               'is_visible': True},
        'tpDst': {'allow_post': True, 'allow_put': True,
               'default': ATTR_NOT_SPECIFIED,
               'validate': {'type:string_or_none': None},
               'is_visible': True},
        'protocol': {'allow_post': True, 'allow_put': True,
               'default': ATTR_NOT_SPECIFIED,
               'validate': {'type:string_or_none': None},
               'is_visible': True},
        'actions': {'allow_post': True, 'allow_put': True,
               'validate': {'type:not_empty_string': None},
               'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
               'validate': {'type:string': None},
               'required_by_policy': True,
               'is_visible': True}
    }
}


class Flowrule(extensions.ExtensionDescriptor):
    """Extension class to extend neutron API"""
    @classmethod
    def get_name(self):
        return "flowrules manager"
    @classmethod
    def get_alias(self):
        return "flowrule"
    @classmethod
    def get_description(self):
        return "a neutron extension that allows to set flows in switches"
    @classmethod
    def get_namespace(self):
        return "http://www.polito.it/frog3.0"
    @classmethod
    def get_updated(self):
        return "2014-05-09T14:25:27+01:00"
    @classmethod
    def get_resources(self):
        exts = list()
        plugin = manager.NeutronManager.get_plugin()
        params = RESOURCE_ATTRIBUTE_MAP.get(attributes.FLOWRULES, dict())
        controller = base.create_resource(attributes.FLOWRULES, attributes.FLOWRULE, plugin, params, allow_bulk=False)
        ex = extensions.ResourceExtension(attributes.FLOWRULES, controller)
        exts.append(ex)
        return exts
