# Copyright (c) 2013-2014 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
# @author: Kyle Mestery, Cisco Systems, Inc.
# @author: Dave Tucker, Hewlett-Packard Development Company L.P.

import time

from oslo.config import cfg
import requests

from neutron.common import constants as n_const
from neutron.common import exceptions as n_exc
from neutron.common import utils
from neutron.extensions import portbindings
from neutron.openstack.common import excutils
from neutron.openstack.common import jsonutils
from neutron.openstack.common import log
from neutron.plugins.common import constants
from neutron.plugins.ml2 import driver_api as api
from neutron.plugins.ml2.common import exceptions as ml2_exc
from sqlalchemy.orm import exc as sqlExceptions
import time

#more import
import networkx as nx
from networkx.readwrite import json_graph
from neutron.db import db_base_plugin_v2 as db_func_file
import matplotlib
from time import sleep
from django.conf.locale import ml
from neutron.plugins import ml2
matplotlib.use('Agg')
import matplotlib.pyplot as plt

LOG = log.getLogger(__name__)

ODL_NETWORK = 'network'
ODL_NETWORKS = 'networks'
ODL_SUBNET = 'subnet'
ODL_SUBNETS = 'subnets'
ODL_PORT = 'port'
ODL_PORTS = 'ports'

not_found_exception_map = {ODL_NETWORKS: n_exc.NetworkNotFound,
                           ODL_SUBNETS: n_exc.SubnetNotFound,
                           ODL_PORTS: n_exc.PortNotFound}

odl_opts = [
    cfg.StrOpt('url',
               help=_("HTTP URL of OpenDaylight REST interface.")),
    cfg.StrOpt('username',
               help=_("HTTP username for authentication")),
    cfg.StrOpt('password', secret=True,
               help=_("HTTP password for authentication")),
    cfg.IntOpt('timeout', default=10,
               help=_("HTTP timeout in seconds.")),
    cfg.IntOpt('session_timeout', default=30,
               help=_("Tomcat session timeout in minutes.")),
]

cfg.CONF.register_opts(odl_opts, "ml2_odl")


def try_del(d, keys):
    """Ignore key errors when deleting from a dictionary."""
    for key in keys:
        try:
            del d[key]
        except KeyError:
            pass


class JsessionId(requests.auth.AuthBase):

    """Attaches the JSESSIONID and JSESSIONIDSSO cookies to an HTTP Request.

    If the cookies are not available or when the session expires, a new
    set of cookies are obtained.
    """

    def __init__(self, url, username, password):
        """Initialization function for JsessionId."""

        # NOTE(kmestery) The 'limit' paramater is intended to limit how much
        # data is returned from ODL. This is not implemented in the Hydrogen
        # release of OpenDaylight, but will be implemented in the Helium
        # timeframe. Hydrogen will silently ignore this value.
        self.url = str(url) + '/' + ODL_NETWORKS + '?limit=1'
        self.username = username
        self.password = password
        self.auth_cookies = None
        self.last_request = None
        self.expired = None
        self.session_timeout = cfg.CONF.ml2_odl.session_timeout * 60
        self.session_deadline = 0

    def obtain_auth_cookies(self):
        """Make a REST call to obtain cookies for ODL authenticiation."""

        r = requests.get(self.url, auth=(self.username, self.password))
        r.raise_for_status()
        jsessionid = r.cookies.get('JSESSIONID')
        jsessionidsso = r.cookies.get('JSESSIONIDSSO')
        if jsessionid and jsessionidsso:
            self.auth_cookies = dict(JSESSIONID=jsessionid,
                                     JSESSIONIDSSO=jsessionidsso)

    def __call__(self, r):
        """Verify timestamp for Tomcat session timeout."""

        if time.time() > self.session_deadline:
            self.obtain_auth_cookies()
        self.session_deadline = time.time() + self.session_timeout
        r.prepare_cookies(self.auth_cookies)
        return r


class OpenDaylightMechanismDriver(api.MechanismDriver):

    """Mechanism Driver for OpenDaylight.

    This driver was a port from the Tail-F NCS MechanismDriver.  The API
    exposed by ODL is slightly different from the API exposed by NCS,
    but the general concepts are the same.
    """
    auth = None
    out_of_sync = True
    #variables declared by Matteo
    topology = nx.Graph();
    WEIGHT_PROPERTY_NAME = 'weight'
    ACTIONS_SEPARATOR_CHARACTER = ','
    VLAN_BUSY_CODE = 1
    VLAN_FREE_CODE = 0
    #end of custom variable declaration
    
    def initialize(self):
        self.url = cfg.CONF.ml2_odl.url
        self.timeout = cfg.CONF.ml2_odl.timeout
        self.username = cfg.CONF.ml2_odl.username
        self.password = cfg.CONF.ml2_odl.password
        self.auth = JsessionId(self.url, self.username, self.password)
        self.vif_type = portbindings.VIF_TYPE_OVS
        self.vif_details = {portbindings.CAP_PORT_FILTER: True}

    # Postcommit hooks are used to trigger synchronization.

    def create_network_postcommit(self, context):
        #self.synchronize('create', ODL_NETWORKS, context)
        pass
    
    def update_network_postcommit(self, context):
        #self.synchronize('update', ODL_NETWORKS, context)
        pass
    
    def delete_network_postcommit(self, context):
        #self.synchronize('delete', ODL_NETWORKS, context)
        pass
    
    def create_subnet_postcommit(self, context):
        #self.synchronize('create', ODL_SUBNETS, context)
        pass
    
    def update_subnet_postcommit(self, context):
        #self.synchronize('update', ODL_SUBNETS, context)
        pass
    
    def delete_subnet_postcommit(self, context):
        #self.synchronize('delete', ODL_SUBNETS, context)
        pass
    
    def create_port_postcommit(self, context):
        #self.synchronize('create', ODL_PORTS, context)
        pass
    
    def update_port_postcommit(self, context):
        #self.synchronize('update', ODL_PORTS, context)
        pass
    
    def delete_port_postcommit(self, context):
        #self.synchronize('delete', ODL_PORTS, context)
        pass
    
    def synchronize(self, operation, object_type, context):
        """Synchronize ODL with Neutron following a configuration change."""
        """
        # legacy
        if self.out_of_sync:
            self.sync_full(context)
        else:
            self.sync_object(operation, object_type, context)
        """
        self.sync_object(operation, object_type, context)
        
    def filter_create_network_attributes(self, network, context, dbcontext):
        """Filter out network attributes not required for a create."""
        try_del(network, ['status', 'subnets'])

    def filter_create_subnet_attributes(self, subnet, context, dbcontext):
        """Filter out subnet attributes not required for a create."""
        pass

    def filter_create_port_attributes(self, port, context, dbcontext):
        """Filter out port attributes not required for a create."""
        self.add_security_groups(context, dbcontext, port)
        # TODO(kmestery): Converting to uppercase due to ODL bug
        # https://bugs.opendaylight.org/show_bug.cgi?id=477
        port['mac_address'] = port['mac_address'].upper()
        try_del(port, ['status'])

    def sync_resources(self, resource_name, collection_name, resources,
                       context, dbcontext, attr_filter):
        """Sync objects from Neutron over to OpenDaylight.

        This will handle syncing networks, subnets, and ports from Neutron to
        OpenDaylight. It also filters out the requisite items which are not
        valid for create API operations.
        """
        to_be_synced = []
        for resource in resources:
            try:
                urlpath = collection_name + '/' + resource['id']
                self.sendjson('get', urlpath, None)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    attr_filter(resource, context, dbcontext)
                    to_be_synced.append(resource)

        key = resource_name if len(to_be_synced) == 1 else collection_name

        # 400 errors are returned if an object exists, which we ignore.
        self.sendjson('post', collection_name, {key: to_be_synced}, [400])

    @utils.synchronized('odl-sync-full')
    def sync_full(self, context):
        """Resync the entire database to ODL.

        Transition to the in-sync state on success.
        Note: we only allow a single thead in here at a time.
        """
        if not self.out_of_sync:
            return
        dbcontext = context._plugin_context
        networks = context._plugin.get_networks(dbcontext)
        subnets = context._plugin.get_subnets(dbcontext)
        ports = context._plugin.get_ports(dbcontext)

        self.sync_resources(ODL_NETWORK, ODL_NETWORKS, networks,
                            context, dbcontext,
                            self.filter_create_network_attributes)
        self.sync_resources(ODL_SUBNET, ODL_SUBNETS, subnets,
                            context, dbcontext,
                            self.filter_create_subnet_attributes)
        self.sync_resources(ODL_PORT, ODL_PORTS, ports,
                            context, dbcontext,
                            self.filter_create_port_attributes)
        #added sync for flowmods
        self.sync_flowmods(context)
        self.out_of_sync = False

    def filter_update_network_attributes(self, network, context, dbcontext):
        """Filter out network attributes for an update operation."""
        try_del(network, ['id', 'status', 'subnets', 'tenant_id'])

    def filter_update_subnet_attributes(self, subnet, context, dbcontext):
        """Filter out subnet attributes for an update operation."""
        try_del(subnet, ['id', 'network_id', 'ip_version', 'cidr',
                         'allocation_pools', 'tenant_id'])

    def filter_update_port_attributes(self, port, context, dbcontext):
        """Filter out port attributes for an update operation."""
        self.add_security_groups(context, dbcontext, port)
        try_del(port, ['network_id', 'id', 'status', 'mac_address',
                       'tenant_id', 'fixed_ips'])

    create_object_map = {ODL_NETWORKS: filter_create_network_attributes,
                         ODL_SUBNETS: filter_create_subnet_attributes,
                         ODL_PORTS: filter_create_port_attributes}

    update_object_map = {ODL_NETWORKS: filter_update_network_attributes,
                         ODL_SUBNETS: filter_update_subnet_attributes,
                         ODL_PORTS: filter_update_port_attributes}

    def sync_single_resource(self, operation, object_type, obj_id,
                             context, attr_filter_create, attr_filter_update):
        """Sync over a single resource from Neutron to OpenDaylight.

        Handle syncing a single operation over to OpenDaylight, and correctly
        filter attributes out which are not required for the requisite
        operation (create or update) being handled.
        """
        dbcontext = context._plugin_context
        if operation == 'create':
            urlpath = object_type
            method = 'post'
        else:
            urlpath = object_type + '/' + obj_id
            method = 'put'

        try:
            obj_getter = getattr(context._plugin, 'get_%s' % object_type[:-1])
            resource = obj_getter(dbcontext, obj_id)
        except not_found_exception_map[object_type]:
            LOG.debug(_('%(object_type)s not found (%(obj_id)s)'),
                      {'object_type': object_type.capitalize(),
                      'obj_id': obj_id})
        else:
            if operation == 'create':
                attr_filter_create(self, resource, context, dbcontext)
            elif operation == 'update':
                attr_filter_update(self, resource, context, dbcontext)
            try:
                # 400 errors are returned if an object exists, which we ignore.
                self.sendjson(method, urlpath, {object_type[:-1]: resource},
                              [400])
            except Exception:
                with excutils.save_and_reraise_exception():
                    LOG.debug(_("got 400"))
                    self.out_of_sync = True

    def sync_object(self, operation, object_type, context):
        """Synchronize the single modified record to ODL."""
        obj_id = context.current['id']

        self.sync_single_resource(operation, object_type, obj_id, context,
                                  self.create_object_map[object_type],
                                  self.update_object_map[object_type])

    def add_security_groups(self, context, dbcontext, port):
        """Populate the 'security_groups' field with entire records."""
        groups = [context._plugin.get_security_group(dbcontext, sg)
                  for sg in port['security_groups']]
        port['security_groups'] = groups

    def sendjson(self, method, urlpath, obj, ignorecodes=[]):
        """Send json to the OpenDaylight controller."""

        headers = {'Content-Type': 'application/json'}
        data = jsonutils.dumps(obj, indent=2) if obj else None
        if self.url:
            url = '/'.join([self.url, urlpath])
            LOG.debug(_('ODL-----> sending URL (%s) <-----ODL') % url)
            LOG.debug(_('ODL-----> sending JSON (%s) <-----ODL') % obj)

            LOG.debug(_("faccio una"+str(method)))
            LOG.debug(_("a"+str(url)))
            r = requests.request(method, url=url,
                                 headers=headers, data=data,
                                 auth=self.auth, timeout=self.timeout)

            # ignorecodes contains a list of HTTP error codes to ignore.
            if r.status_code in ignorecodes:
                return
            r.raise_for_status()

    def bind_port(self, context):
        LOG.debug(_("Attempting to bind port %(port)s on "
                    "network %(network)s"),
                  {'port': context.current['id'],
                   'network': context.network.current['id']})
        for segment in context.network.network_segments:
            if self.check_segment(segment):
                context.set_binding(segment[api.ID],
                                    self.vif_type,
                                    self.vif_details,
                                    status=n_const.PORT_STATUS_ACTIVE)
                LOG.debug(_("Bound using segment: %s"), segment)
                return
            else:
                LOG.debug(_("Refusing to bind port for segment ID %(id)s, "
                            "segment %(seg)s, phys net %(physnet)s, and "
                            "network type %(nettype)s"),
                          {'id': segment[api.ID],
                           'seg': segment[api.SEGMENTATION_ID],
                           'physnet': segment[api.PHYSICAL_NETWORK],
                           'nettype': segment[api.NETWORK_TYPE]})

    def check_segment(self, segment):
        """Verify a segment is valid for the OpenDaylight MechanismDriver.

        Verify the requested segment is supported by ODL and return True or
        False to indicate this to callers.
        """
        network_type = segment[api.NETWORK_TYPE]
        return network_type in [constants.TYPE_LOCAL, constants.TYPE_GRE,
                                constants.TYPE_VXLAN]

#from here to the bottom, the code was added by Matteo
    """
    def create_flowrule_precommit(self, context):
        '''
        a topology refresh is performed,
        also is checked if the port(s) exist and are linkable
        '''
        LOG.debug(_("create_flowrule_pre"))
        self.out_of_sync = True
        self.sync_full(context)
        #updating topology
        self.topology = self.get_up_to_date_topology_from_odl(context)
        flowrule = context.current['flowrule']
        in_p = flowrule['ingressPort']
        self.port_active_or_raise_exception(context, in_p)
        actionList = self.splitActions(flowrule['actions'])
        for action in actionList:
            if "OUTPUT=" in action:
                out_p = action[7:] #getting rid of the "OUTPUT=" part
                self.port_active_or_raise_exception(context, out_p)
                LOG.debug(_("AZIONE output"))
                self.check_create_flowrule_condition_validity(context, in_p, out_p)
            elif "DROP" in action:
                try:
                    LOG.debug(_("AZIONE drop"))
                    swSource = self.locate_port(context, in_p)
                except Exception:
                    raise n_exc.PortTranslationNotPossible(port_id=in_p)
            else:
                raise n_exc.UnknownAction(action=action)
        return
    
    def create_flowrule_postcommit(self,context):
        '''
        flow path calculation
        vlan incapsulation
        flowmods creation
        flowmods POST to ODL
        '''
        LOG.debug(_("create_flowrule_post"))
        #self.topology = self.get_up_to_date_topology_from_odl(context)#no need to redo this
        flowrule = context.current['flowrule']
        in_p = flowrule['ingressPort']
        actionList = self.splitActions(flowrule['actions'])
        
        if len(actionList) > 1:#TBD manage more actions
            raise n_exc.NotYetImplemented

        for action in sorted(actionList):#TBD manage more actions
            if "OUTPUT=" in action:
                LOG.debug(_("OUTPUT action"))
                out_p = action[7:] #getting rid of the "OUTPUT=" part
                LOG.debug(_("str cutting"+action+" becomes "+out_p))
                path = self.check_create_flowrule_condition_validity(context, in_p, out_p)
                if len(path) == 1:#same switch, no need for vlans
                    p = path[0]
                    port_in = self.locate_port(context, in_p)
                    port_in = port_in['odl_port_id']
                    port_out = self.locate_port(context, out_p)
                    port_out = port_out['odl_port_id']
                    #writeToDb and retrieve unique id (used as flowmod_random_name)
                    flowmod_random_name = self.store_flowmod(context, p, context.current['flowrule'], port_in, ["OUTPUT="+port_out])
                    LOG.debug(_("flowmod in "+p+ "in:"+port_in+" out:"+port_out))
                    j = self.create_json_flowmod(flowmod_random_name, p, context.current['flowrule'], port_in, ["OUTPUT="+port_out])
                    LOG.debug(_("sending to ODL flowmod"+str(j)))
                    self.my_sendjson('PUT', 'flowprogrammer/default/node/OF/'+p+'/staticFlow/'+flowmod_random_name, j)
                    self.my_sendjson("POST",'flowprogrammer/default/node/OF/'+p+'/staticFlow/'+flowmod_random_name)
                    self.my_sendjson("POST",'flowprogrammer/default/node/OF/'+p+'/staticFlow/'+flowmod_random_name)
                else:
                    #multiple switch to traverse, VLAN needed
                    #get a free VLAN id
                    freeVlanId = self.getFreeAndSetAsUsed(context)
                    LOG.debug(_("got vlan #"+str(freeVlanId)))
                    LOG.debug(_("path: "+str(path)))
                    
                    #need to be sure that all the flowmods are instanciated, rollback otherwise
                    instanciatedFlowmods = list()
                    for i in range(0, len(path)):
                        hop = path[i]
                        if i==0:
                            #first switch
                            LOG.debug(_(str(hop)+" content --> "+str(self.topology[hop])))
                            original_vlan_tag = flowrule['vlanId']
                            port_in = self.locate_port(context, in_p)
                            port_in = port_in['odl_port_id'] 
                            port_out = self.topology[hop][path[i+1]]['from_port']
                            actions = ["SET_VLAN_ID="+str(freeVlanId),"OUTPUT="+port_out]
                        elif i==len(path)-1:
                            #last switch
                            port_in = self.topology[path[i-1]][hop]['to_port']
                            port_out = self.locate_port(context, out_p)
                            port_out = port_out['odl_port_id']
                            actions = ["POP_VLAN","OUTPUT="+port_out]
                            #flowrule['vlanId'] = original_vlan_tag
                        else:
                            #middleway hop
                            flowrule['vlanId'] = freeVlanId
                            port_in = self.topology[path[i-1]][hop]['to_port']
                            port_out = self.topology[hop][path[i+1]]['from_port']
                            actions = ["OUTPUT="+port_out]
                            
                        #writeToDb and retrieve unique id (used as flowmod_random_name)
                        flowmod_random_name = self.store_flowmod(context, hop, flowrule, port_in, actions, freeVlanId)
                        LOG.debug(_("flowmod in "+hop+ "in:"+port_in+" out:"+port_out))
                        j = self.create_json_flowmod(flowmod_random_name, hop, flowrule, port_in, actions)
                        LOG.debug(_("sending to ODL flowmod"+str(j)))
                        try:
                            self.my_sendjson('PUT', 'flowprogrammer/default/node/OF/'+hop+'/staticFlow/'+flowmod_random_name, j)
                            self.my_sendjson('POST', 'flowprogrammer/default/node/OF/'+hop+'/staticFlow/'+flowmod_random_name)
                            self.my_sendjson('POST', 'flowprogrammer/default/node/OF/'+hop+'/staticFlow/'+flowmod_random_name)
                            instanciatedFlowmods.append({'sw_id':hop, 'flow_id':flowmod_random_name})
                        except Exception:
                            #rollback of the previously posted flowmods
                            for instance in instanciatedFlowmods:
                                #critical, if this fails the error is unrecoverable
                                try:
                                    self.my_sendjson('DELETE', 'flowprogrammer/default/node/OF/'+instance['sw_id']+'/staticFlow/'+instance['flow_id'])
                                except Exception:
                                    LOG.debug(_("UNRECOVERABLE ERROR WHILE DELETING A POSTED FLOWMODS"))
                                    raise ml2_exc.MechanismDriverError
                            raise ml2_exc.MechanismDriverError
                            
                    #endfor
                #end OUTPUT action
            elif "DROP" in action:
                self.manage_drop_action(context, in_p)
            else:
                raise n_exc.UnknownAction(action=action)
        
        return

    """
    '''new create functions, to manage things properly'''
    def create_flowrule_precommit(self, context):
        LOG.debug(_("create_flowrule_pre"))
        '''
        Commented by fmignini
        self.sync_full(context)
        '''
        self.topology = self.get_up_to_date_topology_from_odl(context)
        flowrule = context.current['flowrule']
        in_p = flowrule['ingressPort']
        actionList = self.splitActions(flowrule['actions'])
        if len(actionList) > 1:#TBD manage more actions
            raise n_exc.NotYetImplemented
        
        for action in sorted(actionList):#TBD manage more actions
            if "OUTPUT=" in action:
                LOG.debug(_("OUTPUT action"))
                out_p = action[7:] #getting rid of the "OUTPUT=" part
                LOG.debug(_("str cutting"+action+" becomes "+out_p))
                path = self.check_create_flowrule_condition_validity(context, in_p, out_p)
                if len(path) == 1:#same switch, no need for vlans
                    p = path[0]
                    port_in = self.locate_port(context, in_p)
                    port_in = port_in['odl_port_id']
                    port_out = self.locate_port(context, out_p)
                    port_out = port_out['odl_port_id']
                    #writeToDb and retrieve unique id (used as flowmod_random_name)
                    flowmod_random_name = self.store_flowmod(context, p, context.current['flowrule'], port_in, 'OUTPUT='+port_out)
                      
                else:
                    #multiple switch to traverse, VLAN needed
                    #get a free VLAN id
                    freeVlanId = self.getFreeAndSetAsUsed(context)
                    LOG.debug(_("got vlan #"+str(freeVlanId)))
                    LOG.debug(_("path: "+str(path)))
                    
                    #need to be sure that all the flowmods are instanciated, rollback otherwise
                    instanciatedFlowmods = list()
                    for i in range(0, len(path)):
                        hop = path[i]
                        if i==0:
                            #first switch
                            LOG.debug(_(str(hop)+" content --> "+str(self.topology[hop])))
                            original_vlan_tag = flowrule['vlanId']
                            port_in = self.locate_port(context, in_p)
                            port_in = port_in['odl_port_id'] 
                            port_out = self.topology[hop][path[i+1]]['from_port']
                            actions = 'SET_VLAN_ID='+str(freeVlanId)+',OUTPUT='+port_out
                        elif i==len(path)-1:
                            #last switch
                            port_in = self.topology[path[i-1]][hop]['to_port']
                            port_out = self.locate_port(context, out_p)
                            port_out = port_out['odl_port_id']
                            actions = 'POP_VLAN,OUTPUT='+port_out
                            #flowrule['vlanId'] = original_vlan_tag
                        else:
                            #middleway hop
                            flowrule['vlanId'] = freeVlanId
                            port_in = self.topology[path[i-1]][hop]['to_port']
                            port_out = self.topology[hop][path[i+1]]['from_port']
                            actions = 'OUTPUT='+port_out
                        #writeToDb and retrieve unique id (used as flowmod_random_name)
                        flowmod_random_name = self.store_flowmod(context, hop, flowrule, port_in, actions, freeVlanId)
                    #endfor
                #end OUTPUT action
            elif "DROP" in action:
                LOG.debug(_("DROP action"))
                try:
                    swSource = self.locate_port(context, in_p)
                except Exception:
                    raise n_exc.PortTranslationNotPossible(port_id=in_p)
                flowmod_random_name = self.store_flowmod(context, swSource["sw_id"], context.current['flowrule'], swSource["odl_port_id"], "DROP")
            else:
                raise n_exc.UnknownAction(action=action)
        return
    
    def create_flowrule_postcommit(self, context):
        LOG.debug(_("create_flowrule_post"))
        '''
        Commented by fmignini
        self.sync_full(context)
        '''
        
        '''not really efficient, should only send the flowmods associated with this flowrule id but it will work for now'''
        self.sync_flowmods(context)
        return
        
    def update_flowrule_precommit(self, context):
        LOG.debug(_("update_flowrule_pre"))
        raise n_exc.NotYetImplemented
        return
    
    def update_flowrule_postcommit(self, context):
        LOG.debug(_("update_flowrule_post"))
        raise n_exc.NotYetImplemented
        return

    def delete_flowrule_precommit(self, context):
        LOG.debug(_("delete_flowrule_pre"))
        '''
        Commented by fmignini
        self.sync_full(context)
        '''
        flowrule_id = context.current['id']
        flowmods = self.getFlowmodsByFlowruleid(context, flowrule_id)
        vlans_to_set_free = list()
        for flowmod in flowmods:
            if flowmod['incapsulation_vlan'] != None:
                vlans_to_set_free.append(flowmod['incapsulation_vlan'])
            self.deleteFlowmodById(context, flowmod['id'])
        #set free vlans
        for vlanid in set(vlans_to_set_free):
            self.setVlanStatus(context, vlanid, self.VLAN_FREE_CODE)
        return

    def delete_flowrule_postcommit(self, context):
        LOG.debug(_("delete_flowrule_post"))
        '''
        Commented by fmignini
        self.sync_full(context)
        '''
        
        '''not the most efficient way to do it'''
        self.sync_flowmods(context)
        return

    def port_active_or_raise_exception(self, context, ML2_port_id):
        try:
           dbcontext = context._plugin_context
           obj_getter = getattr(context._plugin, 'is_this_port_active')
           obj_getter(dbcontext, ML2_port_id)
        except sqlExceptions.NoResultFound:
            raise n_exc.PortNotActive(port_id = ML2_port_id)
    
    def sync_flowmods(self, context):
        LOG.debug(_("entered sync_flowmods"))
        try:
            #get all flowmods from db ordered by switch_id
            odlSwitches = self.get_switch_list()
            for sw in odlSwitches:
                sw_id = sw['node_id']
                flowmods = self.getFlowmodsBySwitchId(context, sw_id)
                rulesInOdlSwitch = self.getAllSwitchRulesFromODL(sw_id)
                LOG.debug(_("in switch "+sw_id+" rules are:"+str(rulesInOdlSwitch)))
                #for asd in flowmods:
                #    LOG.debug(_("on database rules are:"+str(asd['id'])))
                for flowmod in flowmods:
                    if flowmod['id'] in rulesInOdlSwitch:
                        #TBD check update??
                        LOG.debug(_("in switch "+sw_id+" flow "+flowmod['id']+" was found"))
                        rulesInOdlSwitch.remove(flowmod['id'])
                    else:
                        #means a create did not succeded, repushing
                        LOG.debug(_("in switch "+sw_id+" flow "+flowmod['id']+" was not found-->adding it to ODL"))
                        j = self.create_json_flowmod(flowmod['id'], sw_id, flowmod, flowmod['ingressPort'], flowmod['actions'])
                        LOG.debug(_("sending to ODL flowmod"+str(j)))
                        for i in range(1,11):
                            self.my_sendjson('PUT', 'flowprogrammer/default/node/OF/'+sw_id+'/staticFlow/'+flowmod['id'], j)
                            try:
                                self.my_sendjson('GET', 'flowprogrammer/default/node/OF/'+sw_id+'/staticFlow/'+flowmod['id'])
                                LOG.debug(_("mission accomplished "+flowmod['id']))
                                break
                            except Exception as e:
                                LOG.debug(_("retry iteration#"+str(i)+"-->"+str(type(e))))
                                pass
                        #self.my_sendjson('POST', 'flowprogrammer/default/node/OF/'+sw_id+'/staticFlow/'+flowmod['id'])
                        #self.my_sendjson('POST', 'flowprogrammer/default/node/OF/'+sw_id+'/staticFlow/'+flowmod['id'])
                    
                    LOG.debug(_("in switch "+sw_id+" flow remaining are: "+str(rulesInOdlSwitch)))
                for idToDelete in rulesInOdlSwitch:
                    if idToDelete!="NORMAL" and idToDelete != "PuntLLDP" and idToDelete[:7] != 'STATIC_':
                        #ALSO flows with the 'STATIC_' prefix will be ignored
                        #delete rule from switch if is not a standard rule (HWpath or LLDP, necessary to keep normal OS networks working)
                        LOG.debug(_("in switch "+sw_id+" deleting flow: "+idToDelete))
                        self.my_sendjson('DELETE', 'flowprogrammer/default/node/OF/'+sw_id+'/staticFlow/'+idToDelete)
        except Exception:
            LOG.debug(_("M_WARNING out of sync, the rules will be synched on the next call"))
            LOG.debug(_("exception in syncflowmods, probably due to bad communication with ODL, setting out_of_sync = true"))
            self.out_of_sync = True
        return

    def getFlowmodById(self, context, flowmod_id):
        dbcontext = context._plugin_context
        obj_getter = getattr(context._plugin, 'get_flowmod_by_id')
        return obj_getter(dbcontext, flowmod_id)

    def getFlowmodsBySwitchId(self, context, sw_id):
        dbcontext = context._plugin_context
        obj_getter = getattr(context._plugin, 'get_all_flowmods_by_switch_id')
        return obj_getter(dbcontext, sw_id)
    
    def locate_port(self, context, ml2_port_id):#returns {sw_id,odl_port_id}
        LOG.debug(_("entered_locate_port"))
        dbcontext = context._plugin_context
        obj_getter = getattr(context._plugin, 'get_switch_and_port_by_ML2_port_id')
        found = False
        max_retry = 5
        while(not found):
            try:
                res = obj_getter(dbcontext, ml2_port_id)
                found = True
            except Exception as e:
                LOG.debug(_("translation of "+str(ml2_port_id)+" not possible on try "+str(6-max_retry)))
                max_retry = max_retry-1
                if(max_retry == 0):
                    LOG.debug(_("translation of "+str(ml2_port_id)+" not possible, tired of retrying"))
                    raise e
                else:
                    LOG.debug(_("reupdating the switch DB"))
                    time.sleep(1)
                    self.topology = self.get_up_to_date_topology_from_odl(context)
        return res
        '''
        #this was used when we thought that ODL needed time to respond correctly
        for i in range(1,11):
            #get switch list
            swList = self.get_switch_list()
            #update port list
            self.update_switches_port_list(context, swList)
            LOG.debug(_("iter#"+str(i)))
            try:
                dbcontext = context._plugin_context
                obj_getter = getattr(context._plugin, 'get_switch_and_port_by_ML2_port_id')
                a = obj_getter(dbcontext, ml2_port_id)
                return a
            except sqlExceptions.NoResultFound:
                a = None
            
            except sqlExceptions.MultipleResultsFound:
                raise "multiple matches found"
            LOG.debug(_("dormo un po prima di provare"))
            """try:
                time.sleep(1)
            except Exception:
                LOG.debug(_("sleep ERROR"))
            """
        LOG.debug(_("non trovata"))
        if a is None:
            raise sqlExceptions.NoResultFound
        '''

    def getAllSwitchRulesFromODL(self, sw_id):
        '''
        ODL call to get a list of rules instanciated on a switch
        '''
        idList = list()
        j = self.my_sendjson('GET', 'flowprogrammer/default/node/OF/'+sw_id)
        for f in j['flowConfig']:
            idList.append(f['name'])
        return idList
        
    def manage_drop_action(self, context, port):
        '''
        single port action managed and sent to ODL
        '''
        LOG.debug(_("DROP action"))
        try:
            swSource = self.locate_port(context, port)
        except Exception:
            raise n_exc.PortTranslationNotPossible(port_id=port)
        flowmod_random_name = self.store_flowmod(context, swSource["sw_id"], context.current['flowrule'], swSource["odl_port_id"], "DROP")
        LOG.debug(_("flowmod in "+swSource["sw_id"]+ "in:"+port))
        j = self.create_json_flowmod(flowmod_random_name, swSource["sw_id"], context.current['flowrule'], swSource["odl_port_id"], "DROP")
        LOG.debug(_("sending to ODL flowmod"+str(j)))
        for i in range(1,16):
            self.my_sendjson('PUT', 'flowprogrammer/default/node/OF/'+swSource["sw_id"]+'/staticFlow/'+flowmod_random_name, j)
            try:
                self.my_sendjson('GET', 'flowprogrammer/default/node/OF/'+swSource["sw_id"]+'/staticFlow/'+flowmod_random_name)
                LOG.debug(_("mission accomplished "+flowmod_random_name))
                #break
            except Exception:
                LOG.debug(_("retry iteration#"+str(i)+"-->"+str(type(e))))
                pass
        #self.my_sendjson('PUT', 'flowprogrammer/default/node/OF/'+swSource["sw_id"]+'/staticFlow/'+flowmod_random_name, j)
        #self.my_sendjson('PUT', 'flowprogrammer/default/node/OF/'+swSource["sw_id"]+'/staticFlow/'+flowmod_random_name, j)
        
        #self.my_sendjson('POST', 'flowprogrammer/default/node/OF/'+swSource["sw_id"]+'/staticFlow/'+flowmod_random_name)
        #self.my_sendjson('POST', 'flowprogrammer/default/node/OF/'+swSource["sw_id"]+'/staticFlow/'+flowmod_random_name)

    def create_json_flowmod(self, flowmod_rand_name, sw, flowrule, port_in, actions):
        return {"installInHw": True,
                #"installInHw": False,#TODO: change to True
                "name":flowmod_rand_name,
                "node":{"id":sw,"type":"OF"},
                "ingressPort":port_in,
                "hardTimeout": flowrule["hardTimeout"],
                "priority": flowrule["priority"],
                "etherType": flowrule["etherType"],
                "vlanId": flowrule["vlanId"],
                "vlanPriority": flowrule["vlanPriority"],
                "dlSrc": flowrule["dlSrc"],
                "dlDst": flowrule["dlDst"],
                "nwSrc": flowrule["nwSrc"],
                "nwDst": flowrule["nwDst"],
                "tosBits": flowrule["tosBits"],
                "tpSrc": flowrule["tpSrc"],
                "tpDst": flowrule["tpDst"],
                "protocol": flowrule["protocol"],
                "actions": actions.split(",")}

    def getFlowmodsByFlowruleid(self, context, flowrule_id):
        LOG.debug(_("getFlowmodsByFlowruleid with id="+flowrule_id))
        dbcontext = context._plugin_context
        obj_getter = getattr(context._plugin, 'get_flowmods_by_flowrule_id')
        return obj_getter(dbcontext, flowrule_id)
        
    def deleteFlowmodById(self, context, flowmod_id):
        LOG.debug(_("deleteFlowmodById with id="+flowmod_id))
        dbcontext = context._plugin_context
        obj_getter = getattr(context._plugin, 'delete_flowmod')
        obj_getter(dbcontext, flowmod_id)
 
    def store_flowmod(self, context, switch_id, flowrule, input_port, actions, incapsulation_vlan=None):#returns unique id of the stored flowmod
        dbcontext = context._plugin_context
        obj_getter = getattr(context._plugin, 'store_flowmod')
        return obj_getter(dbcontext,
                          flowrule['id'],
                          switch_id,
                          flowrule["hardTimeout"],
                          flowrule["priority"],
                          input_port,
                          flowrule["etherType"],
                          flowrule["vlanId"],
                          flowrule["vlanPriority"],
                          flowrule["dlSrc"],
                          flowrule["dlDst"],
                          flowrule["nwSrc"],
                          flowrule["nwDst"],
                          flowrule["tosBits"],
                          flowrule["tpSrc"],
                          flowrule["tpDst"],
                          flowrule["protocol"],
                          str(actions),
                          incapsulation_vlan)
 

        
    def setVlanStatus(self, context, vlanid, status):
        dbcontext = context._plugin_context
        obj_getter = getattr(context._plugin, 'setVlanUsageStatus')
        obj_getter(dbcontext, vlanid, status)
        
    def getFreeAndSetAsUsed(self, context):
        LOG.debug(_("entered_getFreeVlanId"))
        dbcontext = context._plugin_context
        obj_getter = getattr(context._plugin, 'getFreeVlan')
        freeid = obj_getter(dbcontext)
        self.setVlanStatus(context, freeid, self.VLAN_BUSY_CODE)
        return freeid
        
    def splitActions(self, str):
        return str.strip(' \n\t\r').split(self.ACTIONS_SEPARATOR_CHARACTER)
    
    def calculate_path_between_two_switches(self, graph, source, target, weight_property_name):
        try:
            path = nx.dijkstra_path(graph, source, target, weight_property_name)
        except nx.NetworkXNoPath:
            path=None
        return path
    
    def check_create_flowrule_condition_validity(self, context, in_p, out_p):
        initial_port = in_p
        final_port = out_p
        #set rule in each switch
        try:
            swSource = self.locate_port(context, initial_port)
        except Exception:
            raise n_exc.PortTranslationNotPossible(port_id=initial_port)
        #output port must exist
        try:
            swDest = self.locate_port(context, final_port)
        except Exception:
            raise n_exc.PortTranslationNotPossible(port_id=final_port)
        #calculate path, a path between the two must exist
        affectedSwitches = self.calculate_path_between_two_switches(self.topology, swSource['sw_id'], swDest['sw_id'], self.WEIGHT_PROPERTY_NAME)
        LOG.debug("topology:archi"+str(self.topology.edges()))
        if affectedSwitches == None:
            LOG.debug("ETARDI:"+str(in_p)+' in switch '+str(swSource['sw_id'])+' and '+str(in_p)+' in switch '+str(swDest['sw_id']))
            LOG.debug("tardi2"+str(self.topology.edges()))
            raise n_exc.NonLinkablePorts(id1=in_p,id2=out_p)
        return affectedSwitches
    
    def get_up_to_date_topology_from_odl(self, context):
        myGraph = nx.DiGraph()
        #get switch list
        swList = self.get_switch_list()
        
        #update port list
        self.update_switches_port_list(context, swList)
        
        #calculate switches topology
        for switch in swList:
            sw = switch['node_id']
            myGraph.add_node(sw)
        j = self.my_sendjson('get', 'topology/default/')
        links = j['edgeProperties']
        for e in links:
            head = {'id':e['edge']['headNodeConnector']['node']['id'],'odl_port_id':e['edge']['headNodeConnector']['id']}
            tail = {'id':e['edge']['tailNodeConnector']['node']['id'],'odl_port_id':e['edge']['tailNodeConnector']['id']}
            #conn = e['properties']['name']['value']
            myGraph.add_edge(head['id'], tail['id'], {self.WEIGHT_PROPERTY_NAME:1, 'from_port':head['odl_port_id'],'to_port':tail['odl_port_id']})

        topologyImgPath = "/var/log/neutron/topology.jpg"
        nx.draw(myGraph)
        plt.savefig(topologyImgPath)
        LOG.debug("view of current topology stored in "+topologyImgPath)
        return myGraph
    
    def update_switches_port_list(self, context, swList):#updates the database
        #get port list
        for sw in swList:
            swPorts = self.get_up_to_date_switch_info(sw['node_id'])
            dbcontext = context._plugin_context
            obj_getter = getattr(context._plugin, 'update_ports_switch')
            obj_getter(dbcontext, sw['node_id'], swPorts)
    
    def get_up_to_date_switch_info(self, sw_id):#returns a list of ports {'odl_id','name'}
        #odl api call and some json parsing
        #odl api call
        j = self.my_sendjson('get', 'switchmanager/default/node/OF/' + sw_id)
        portsInSwitch = j['nodeConnectorProperties']
        #parsing the json
        ports = list()
        for p in portsInSwitch:
            port = {'odl_id':p['nodeconnector']['id'],'name':p['properties']['name']['value']}
            LOG.debug(_("sw_id:"+sw_id+" port:"+port['name']))
            ports.append(port)
        LOG.debug(_("switch info:"+sw_id+" has "+str(len(ports))))
        return ports
    
    def get_switch_list(self):#returns a list of switches {'node_id','node_name'}
        #odl api call and some json parsing
        #odl api call
        switches = self.my_sendjson('get', 'switchmanager/default/nodes')
        switches = switches['nodeProperties']
        #parsing the json
        swList = list()
        for s in switches:
            if s['node']['type']=='OF':
                swList.append({'node_id':s['node']['id'],'node_name':s['properties']['description']['value']})
        return swList
    
    def my_sendjson(self, method, urlpath, obj=None):
        headers = {'Content-Type': 'application/json', "cache-control": "no-cache"}
        data = jsonutils.dumps(obj, indent=2)
        if self.url:
            baseUrl = self.url[:len(self.url)-8] #getting rid of the /neutron part
            url = '/'.join([baseUrl, urlpath])
            LOG.debug(_('ODL-----> sending URL (%s) <-----ODL') % url)
            LOG.debug(_('ODL-----> sending JSON (%s) <-----ODL') % obj)
            r = requests.request(method, url=url,
                                 headers=headers, data=data,
                                 auth=self.auth, timeout=self.timeout)
            LOG.debug(_(str(r)))
            # ignore codes between 200 and 299, confirmation codes.
            LOG.debug(_("r.text"+r.text))
            if r.status_code in range(200, 300):
                try:
                    j = jsonutils.loads(r.text)
                except Exception:
                    LOG.debug(_("exception while parsing the json response"))
                    pass
                else:
                    return j
            r.raise_for_status()
