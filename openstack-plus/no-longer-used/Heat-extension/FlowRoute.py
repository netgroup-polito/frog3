'''
Created on 22/mag/2014

@author: rbonafiglia
'''
from heat.engine import constraints
from heat.engine import properties
from heat.engine import clients
from heat.openstack.common.gettextutils import _
from heat.openstack.common import log as logging
from heat.engine.resources.neutron import neutron
import json

if clients.neutronclient is not None:
    import neutronclient.common.exceptions as neutron_exp
    from neutronclient.neutron import v2_0 as neutronV20
    
_logger = logging.getLogger(__name__)

class FlowRoute(neutron.NeutronResource):
    '''
    Class that specifies the flow route resource as an heat plug-in
    Requires the flowRoute neutron mod
    '''

    properties_schema = {
        "id": properties.Schema(
            properties.Schema.STRING,
            description=_('Name to identify the flow'),
            required=True),
        "hardTimeout": properties.Schema(
            properties.Schema.INTEGER,
            description=_('timer to remove the rule')),
        "priority": properties.Schema(
            properties.Schema.INTEGER,
            description=_('the higher, the better'),
            default=1,
            constraints=[
                constraints.Range(1, 65535)
            ]),
        "VNFDependencies" : properties.Schema(
            properties.Schema.MAP,
            description=_('List of machine ID depends on'),
            schema={
                    "VNF1": properties.Schema(
                            properties.Schema.STRING,
                            description=_('First VNF')),
                    "VNF2": properties.Schema(
                            properties.Schema.STRING,
                            description=_('Second VNF'))}),
        "ingressPort": properties.Schema(
            properties.Schema.STRING,
            description=_('ID of the ingress port')),
        "etherType": properties.Schema(
            properties.Schema.STRING,
            description=_('ethertype')),
        "vlanId": properties.Schema(
            properties.Schema.INTEGER,
            description=_('VlanID'),
            constraints=[
                constraints.Range(0, 4095)
            ]),
        "vlanPriority": properties.Schema(
            properties.Schema.INTEGER,
            description=_('service class'),
            constraints=[
                constraints.Range(0, 7)
            ]),
        "dlSrc": properties.Schema(
            properties.Schema.STRING,
            description=_('MAC source'),
            constraints=[
                constraints.AllowedPattern('^([0-9A-F]{2}[:-]){5}([0-9A-F]{2})$')
            ]),
        "dlDst": properties.Schema(
            properties.Schema.STRING,
            description=_('MAC destination'),
            constraints=[
                constraints.AllowedPattern('^([0-9A-F]{2}[:-]){5}([0-9A-F]{2})$')
            ]),
        "nwSrc": properties.Schema(
            properties.Schema.STRING,
            description=_('IP source'),
            constraints=[
                constraints.AllowedPattern('^(((2[0-4][0-9])|(25[0-5])|(1[0-9][0-9])|([1-9][0-9])|([0-9]))\\.){3}(((2[0-4][0-9])|(25[0-5])|(1[0-9][0-9])|([1-9][0-9])|([0-9])))$')
            ]),
        "nwDst": properties.Schema(
            properties.Schema.STRING,
            description=_('IP destination'),
            constraints=[
                constraints.AllowedPattern('^(((2[0-4][0-9])|(25[0-5])|(1[0-9][0-9])|([1-9][0-9])|([0-9]))\\.){3}(((2[0-4][0-9])|(25[0-5])|(1[0-9][0-9])|([1-9][0-9])|([0-9])))$')
            ]),
        "tosBits": properties.Schema(
            properties.Schema.INTEGER,
            description=_('type of service'),
            constraints=[
                constraints.Range(0, 63)
            ]),
        "tpSrc": properties.Schema(
            properties.Schema.INTEGER,
            description=_('Port source'),
            constraints=[
                constraints.Range(0, 65535)
            ]),
        "tpDst": properties.Schema(
            properties.Schema.INTEGER,
            description=_('Port destination'),
            constraints=[
                constraints.Range(0, 65535)
            ]),
        "protocol": properties.Schema(
            properties.Schema.STRING,
            description=_('')),
        "actions": properties.Schema(
            properties.Schema.MAP,
            description=_('list of actions to be performed'),
            schema={
                    "type": properties.Schema(
                            properties.Schema.STRING,
                            description=_('Type of action to be done')),
                    "outputPort": properties.Schema(
                            properties.Schema.STRING,
                            description=_('ID of the port in case of OUTPUT action'))})
    }
    
    

        
    def handle_create(self):
        params = self.generate_params()
        try:
            _logger.debug("Creating flowrule")
            result = self.neutron().create_flowrule({"flowrule": params})
            _logger.debug("Flowrule created")
        except (Exception) as e:
            return e
        finally:
            self.resource_id_set(params['id'])
        return result
            
    def check_create_complete(self, result):
        if isinstance(result, Exception):
            raise result
        return True
    
    def generate_params(self):
        params = {}
        for (key, item) in self.properties.iteritems():
            if item == None:
                continue
            if( key == 'VNFDependencies'):
                continue
            if( key!='actions'):
                params[key] = str(item)
        params['id'] = self.context.tenant + params['id']
        #params['actions'] = []
        action = self.properties['actions']
        if action['type']=='OUTPUT':
            params['actions']='OUTPUT='+str(action['outputPort'])
        else:
            params['actions']=action['type']
        _logger.debug(params['actions'])
        return params
    
    def handle_update(self, json_snippet, tmpl_diff, prop_diff):
        pass
    
    def handle_delete(self):
        try:
            self.neutron().delete_flowrule(self.resource_id)
        except (neutron_exp.NeutronClientException):
            pass
        
def resource_mapping():
    return {'OS::Neutron::FlowRoute': FlowRoute}
        