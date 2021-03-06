'''
Created on Jun 20, 2015

@author: fabiomignini
'''

from sqlalchemy import Column, VARCHAR, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

from openstack_dashboard.dashboards.admin.forwarding_graph.SQL.session import Session
from openstack_dashboard.dashboards.admin.forwarding_graph.SQL.sql import get_session
from openstack_dashboard.dashboards.admin.forwarding_graph.NFFG.nffg import NF_FG, Match
import datetime
import json
import logging


Base = declarative_base()

class GraphModel(Base):
    '''
    Maps the database table graph
    '''
    __tablename__ = 'graph'
    attributes = ['id', 'session_id','node_id','partial']
    id = Column(Integer, primary_key=True)
    session_id = Column(VARCHAR(64))
    node_id = Column(VARCHAR(64))
    partial = Column(Boolean())
    
class VNFModel(Base):
    '''
    Maps the database table node
    '''
    __tablename__ = 'vnf_instance'
    attributes = ['id', 'internal_id', 'graph_vnf_id','session_id', 'graph_id', 'name','template_location', 'image_location', 'location','type', 'status', 'creation_date','last_update', 'availability_zone']
    id = Column(Integer, primary_key=True)
    internal_id = Column(VARCHAR(64))
    graph_vnf_id = Column(VARCHAR(64))
    session_id = Column(VARCHAR(64))
    graph_id = Column(VARCHAR(64))
    name = Column(VARCHAR(64))
    template_location = Column(VARCHAR(64))
    image_location = Column(VARCHAR(64))
    location = Column(VARCHAR(64))
    type = Column(VARCHAR(64))
    status = Column(VARCHAR(64))
    creation_date = Column(VARCHAR(64))
    last_update = Column(VARCHAR(64))
    availability_zone = Column(VARCHAR(64))

class PortModel(Base):
    '''
    Maps the database table node
    '''
    __tablename__ = 'port'
    attributes = ['id', 'internal_id', 'graph_port_id','session_id', 'graph_id', 'name','vnf_id', 'location','type', 'virtual_switch', 'status', 'creation_date','last_update', 'os_network_id',
                    'mac_address', 'ipv4_address', 'vlan_id','gre_key']
    id = Column(Integer, primary_key=True)
    internal_id = Column(VARCHAR(64))
    graph_port_id = Column(VARCHAR(64))
    session_id = Column(VARCHAR(64))
    graph_id = Column(VARCHAR(64))
    name = Column(VARCHAR(64))
    vnf_id = Column(VARCHAR(64))
    location = Column(VARCHAR(64))
    type = Column(VARCHAR(64))
    virtual_switch = Column(VARCHAR(64))
    status = Column(VARCHAR(64))
    creation_date = Column(VARCHAR(64))
    last_update = Column(VARCHAR(64))
    os_network_id = Column(VARCHAR(64))
    mac_address = Column(VARCHAR(64))
    ipv4_address = Column(VARCHAR(64))
    vlan_id = Column(VARCHAR(64))
    gre_key = Column(VARCHAR(64))
    
class EndpointModel(Base):
    '''
    Maps the database table endpoint
    '''
    __tablename__ = 'endpoint'
    attributes = ['id', 'internal_id', 'graph_endpoint_id','session_id','graph_id','name', 'type','location']
    id = Column(Integer, primary_key=True)
    internal_id = Column(VARCHAR(64))
    graph_endpoint_id = Column(VARCHAR(64))
    session_id = Column(VARCHAR(64))
    graph_id = Column(VARCHAR(64))
    name = Column(VARCHAR(64))
    type = Column(VARCHAR(64))
    location = Column(VARCHAR(64))
    
class EndpointResourceModel(Base):
    '''
    Maps the database table endpoint_resource
    '''
    __tablename__ = 'endpoint_resource'
    attributes = ['endpoint_id', 'resource_type', 'resource_id']
    endpoint_id = Column(Integer, primary_key=True)
    resource_type = Column(VARCHAR(64), primary_key=True)
    resource_id = Column(Integer, primary_key=True)
    session_id = Column(VARCHAR(64), primary_key=True)

class O_ArchModel(Base):
    '''
    Maps the database table node
    '''
    __tablename__ = 'o_arch'
    attributes = ['id', 'internal_id', 'graph_o_arch_id','session_id', 'graph_id', 'type','start_node_type', 'start_node_id',
                  'end_node_type', 'end_node_id', 'status', 'creation_date','last_update']
    id = Column(Integer, primary_key=True)
    internal_id = Column(VARCHAR(64))
    graph_o_arch_id = Column(VARCHAR(64))
    session_id = Column(VARCHAR(64))
    graph_id = Column(VARCHAR(64))
    type = Column(VARCHAR(64))
    start_node_type = Column(VARCHAR(64))
    start_node_id = Column(VARCHAR(64))
    end_node_type = Column(VARCHAR(64))
    end_node_id = Column(VARCHAR(64))
    status = Column(VARCHAR(64))
    creation_date = Column(VARCHAR(64))
    last_update = Column(VARCHAR(64))
    
class FlowspecModel(Base):
    '''
    Maps the database table flowspec
    '''
    __tablename__ = 'flowspec'
    attributes = ['id', 'o_arch_id', 'priority', 'etherType','vlanId','vlanPriority', 'dlSrc','dlDst','nwSrc',
                 'nwDst','tosBits','tpSrc', 'tpDst','protocol']
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer)
    o_arch_id = Column(VARCHAR(64))
    session_id = Column(Integer)
    graph_id = Column(Integer)
    priority = Column(VARCHAR(64))
    etherType = Column(VARCHAR(64))
    vlanId = Column(VARCHAR(64))
    vlanPriority = Column(VARCHAR(64))
    dlSrc = Column(VARCHAR(64))
    dlDst = Column(VARCHAR(64))
    nwSrc = Column(VARCHAR(64))
    nwDst = Column(VARCHAR(64))
    tosBits = Column(VARCHAR(64))
    tpSrc = Column(VARCHAR(64))
    tpDst = Column(VARCHAR(64))
    protocol = Column(VARCHAR(64))

class GraphConnectionModel(Base):
    '''
    Maps the database table graph_connection
    '''
    __tablename__ = 'graph_connection'
    attributes = ['endpoint_id_1', 'endpoint_id_2']
    endpoint_id_1 = Column(VARCHAR(64), primary_key=True)
    endpoint_id_2 = Column(VARCHAR(64), primary_key=True)
    
class OpenstackNetworkModel(Base):
    '''
    Maps the database table node
    '''
    __tablename__ = 'openstack_network'
    attributes = ['id', 'name', 'status','vlan_id']
    id = Column(VARCHAR(64), primary_key=True)
    name = Column(VARCHAR(64))
    status = Column(VARCHAR(64))
    vlan_id = Column(VARCHAR(64))
    
class OpenstackSubnetModel(Base):
    '''
    Maps the database table node
    '''
    __tablename__ = 'openstack_subnet'
    attributes = ['id', 'name', 'os_neutron_id']
    id = Column(VARCHAR(64), primary_key=True)
    name = Column(VARCHAR(64))
    os_network_id = Column(VARCHAR(64))
    
class Graph(object):
    def __init__(self):
        self.user_session = Session()
    
    def get_nffg_by_id(self, service_graph_id, encode=False):
        session = Session().get_active_user_session_by_nf_fg_id(service_graph_id)
        logging.debug('[get_nffg_by_id] session id: '+str(session.id))
        return self.get_nffg(session.id, encode)
    
    def get_nffg(self, session_id, encode=False):
        nffg = NF_FG()
        session = get_session()
        graphs_ref = session.query(GraphModel).filter_by(session_id = session_id).all()
        logging.debug(session_id)
        service_graph_info_ref = Session().get_service_graph_info(session_id)

        nffg._id = service_graph_info_ref.service_graph_id
        nffg.name = service_graph_info_ref.service_graph_name
        vnfs_ref = session.query(VNFModel).filter_by(session_id = session_id).all()
        for vnf_ref in vnfs_ref:
            vnf = nffg.createVNF(vnf_ref.name, vnf_ref.template_location, vnf_ref.graph_vnf_id, db_id=vnf_ref.id,internal_id=vnf_ref.internal_id)
            ports_ref = session.query(PortModel).filter_by(session_id = session_id).filter_by(vnf_id = str(vnf_ref.id)).all()
            for port_ref in ports_ref:
                port = vnf.addPort(vnf=vnf,port_id=port_ref.graph_port_id, db_id=port_ref.id,internal_id=port_ref.internal_id, type = port_ref.type)
                o_archs_ref = session.query(O_ArchModel).filter_by(session_id = session_id).filter_by(start_node_type = "port").filter_by(start_node_id = port_ref.id).all()
                for o_arch_ref in o_archs_ref:
                    if o_arch_ref.end_node_type == 'port':
                        connected_port_ref = session.query(PortModel).filter_by(id = o_arch_ref.end_node_id).first()
                        connected_vnf_ref = session.query(VNFModel).filter_by(id = connected_port_ref.vnf_id).first()
                        if connected_port_ref is not None:
                            flowspecs_ref = session.query(FlowspecModel).filter_by(o_arch_id= o_arch_ref.id).all()
                            for flowspec_ref in flowspecs_ref: 
                                flowrule = port.setFlowRuleToVNF(connected_vnf_ref.graph_vnf_id, connected_port_ref.graph_port_id, db_id=o_arch_ref.id, internal_id=o_arch_ref.internal_id, flowrule_id=o_arch_ref.graph_o_arch_id)
                                of_field=self._encode_of_field(flowspec_ref)
                                matches = []
                                matches.append(Match(priority= flowspec_ref.priority, match_id=flowspec_ref.match_id, of_field=of_field, db_id=flowspec_ref.id))
                                flowrule.changeMatches(matches)
                            
                    elif o_arch_ref.end_node_type == 'endpoint':
                        connected_endpoint_ref = session.query(EndpointModel).filter_by(id = o_arch_ref.end_node_id).first()
                        if connected_endpoint_ref is not None:
                            flowspecs_ref = session.query(FlowspecModel).filter_by(o_arch_id= o_arch_ref.id).all()
                            for flowspec_ref in flowspecs_ref:
                                flowrule = port.setFlowRuleToEndpoint(connected_endpoint_ref.graph_endpoint_id, db_id=o_arch_ref.id, internal_id=o_arch_ref.internal_id, flowrule_id=o_arch_ref.graph_o_arch_id)
                                of_field=self._encode_of_field(flowspec_ref)
                                matches = []
                                matches.append(Match(priority=flowspec_ref.priority, match_id=flowspec_ref.match_id, of_field=of_field, db_id=flowspec_ref.id))
                                flowrule.changeMatches(matches)
                        
                        # find arch from endpoint to this port
                        #connection_from_endpoints_ref = session.query(O_ArchModel).filter_by(session_id = session_id).filter_by(start_node_type = "endpoint").filter_by(end_node_type = "port").filter_by(end_node_id = port_ref.id).join(O_ArchModel.start_node_id).join(EndpointModel.id).all()
                        #session.query(O_ArchModel).filter_by(session_id = session_id).filter_by(start_node_type = "endpoint").filter_by(end_node_type = "port").filter_by(end_node_id = port_ref.id).join(O_ArchModel.start_node_id).join(EndpointModel.id).all()
                        connection_from_endpoints_ref = session.query(EndpointModel,O_ArchModel).filter(O_ArchModel.start_node_id == EndpointModel.id).filter(O_ArchModel.session_id == session_id).filter(O_ArchModel.start_node_type == "endpoint").filter(O_ArchModel.end_node_type == "port").filter(O_ArchModel.end_node_id == port_ref.id).all()
                        
                        for connection_from_endpoint_ref, ingress_o_arch_id_from_endpoint in connection_from_endpoints_ref:
                            flowspecs_ref = session.query(FlowspecModel).filter_by(o_arch_id= ingress_o_arch_id_from_endpoint.id).all()
                            for flowspec_ref in flowspecs_ref:
                                flowrule = port.setFlowRuleFromEndpoint(vnf.id, connection_from_endpoint_ref.graph_endpoint_id, db_id=ingress_o_arch_id_from_endpoint.id, internal_id=ingress_o_arch_id_from_endpoint.internal_id, flowrule_id=ingress_o_arch_id_from_endpoint.graph_o_arch_id)
                                of_field=self._encode_of_field(flowspec_ref)
                                matches = []
                                matches.append(Match(priority=flowspec_ref.priority, match_id=flowspec_ref.match_id, of_field=of_field, db_id=flowspec_ref.id))
                                flowrule.changeMatches(matches)
                        
                            
        endpoints_ref = session.query(EndpointModel).filter_by(session_id = session_id).all()
        for endpoint_ref in endpoints_ref:
            endpoint = nffg.createEndpoint(endpoint_ref.name, endpoint_id=endpoint_ref.graph_endpoint_id, db_id=endpoint_ref.id)
            # endpoint resource
            endpoint_resorces_ref = session.query(EndpointResourceModel).filter_by(endpoint_id = endpoint_ref.id).filter_by(session_id = session_id).all()
            for endpoint_resorce_ref in endpoint_resorces_ref:
                if endpoint_resorce_ref.resource_type == 'port':
                    try:
                        port = self._getPort(endpoint_resorce_ref.resource_id)
                    except PortNotFound:
                        continue
                    endpoint_type = endpoint_ref.type
                    if endpoint_type in 'remote_interface':
                        nffg.characterizeEndpoint(endpoint, endpoint_type = endpoint_type, interface = port.internal_id, node = port.location)
                    else:
                        nffg.characterizeEndpoint(endpoint, endpoint_type = endpoint_type, interface = port.name, node = port.location)
                    internal = False
                    for graph_ref in graphs_ref:
                        logging.debug("port.graph_id: "+str(port.graph_id)+" graph_ref.id: "+str(graph_ref.id))
                        if str(port.graph_id) == str(graph_ref.id):
                            internal=True
                            endpoint.attached = True
                            break
                    if internal is False:
                        service_graph_info_ref =  Session().get_service_graph_info(port.session_id)
                        endpoint.remote_graph = service_graph_info_ref.service_graph_id
                        endpoint.remote_graph_name = service_graph_info_ref.service_graph_name
                        endpoint.connection = True                 
                        graph_connection_ref = session.query(GraphConnectionModel).filter_by(endpoint_id_1 = endpoint_ref.id).one()
                        endpoint.remote_id = self._getEndpoint(graph_connection_ref.endpoint_id_2).graph_endpoint_id

        if encode:
            return nffg.getJSON()
        else:
            return nffg
        
    def _getPort(self, port_db_id):
        session = get_session()  
        try:
            return session.query(PortModel).filter_by(id=port_db_id).one()
        except Exception as ex:
            logging.error(ex)
            raise Exception("Port Not Found for db id: "+str(port_db_id))
        
    def _getEndpoint(self, endpoint_id):
        session = get_session()  
        try:
            return session.query(EndpointModel).filter_by(id=endpoint_id).one()
        except Exception as ex:
            logging.error(ex)
            raise Exception("Endpoint not found: "+str(endpoint_id))
        
    def _encode_of_field(self, flowspec_ref):
        of_field = {}
        if flowspec_ref.etherType is not None:
            of_field['etherType'] = flowspec_ref.etherType
        if flowspec_ref.vlanId is not None:
            of_field['vlanId'] = flowspec_ref.vlanId
        if flowspec_ref.vlanPriority is not None:
            of_field['vlanPriority'] = flowspec_ref.vlanPriority
        if flowspec_ref.dlSrc is not None:
            of_field['sourceMAC'] = flowspec_ref.dlSrc
        if flowspec_ref.dlDst is not None:
            of_field['destMAC'] = flowspec_ref.dlDst
        if flowspec_ref.nwSrc is not None:
            of_field['sourceIP'] = flowspec_ref.nwSrc
        if flowspec_ref.nwSrc is not None:
            of_field['destIP'] = flowspec_ref.nwSrc
        if flowspec_ref.nwDst is not None:
            of_field['destIP'] = flowspec_ref.nwDst
        if flowspec_ref.tosBits is not None:
            of_field['tosBits'] = flowspec_ref.tosBits
        if flowspec_ref.tpSrc is not None:
            of_field['sourcePort'] = flowspec_ref.tpSrc
        if flowspec_ref.tpDst is not None:
            of_field['destPort'] = flowspec_ref.tpDst
        if flowspec_ref.protocol is not None:
            of_field['protocol'] = flowspec_ref.protocol
        return of_field
        
