'''
Created on Jun 20, 2015

@author: fabiomignini
'''

from sqlalchemy import Column, VARCHAR, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from Common.SQL.sql import get_session
from sqlalchemy.sql import func

from Common.config import Configuration
from Common.SQL.session import Session
import datetime
import json
import logging
from Common.NF_FG.nf_fg import NF_FG, Match
from Common.SQL.endpoint import EndpointModel
from Common.exception import EndpointNotFound, PortNotFound, GraphNotFound


Base = declarative_base()
sqlserver = Configuration().CONNECTION



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
    __tablename__ = 'vnf'
    attributes = ['id', 'internal_id', 'graph_vnf_id','session_id', 'graph_id', 'name','template_location', 'image_location', 'location','type', 'status', 'creation_date','last_update', 'avialability_zone']
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
    avialability_zone = Column(VARCHAR(64))

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
    attributes = ['id', 'internal_id', 'graph_endpoint_id','session_id','graph_id','type','location']
    id = Column(Integer, primary_key=True)
    internal_id = Column(VARCHAR(64))
    graph_endpoint_id = Column(VARCHAR(64))
    session_id = Column(VARCHAR(64))
    graph_id = Column(VARCHAR(64))
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
                  'end_node_type', 'end_node_id', 'creation_date','last_update']
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
    
class Graph(object):
    def __init__(self):
        self.user_session = Session()

    def getGraphConnections(self, service_graph_id, endpoint_name):
        #graph_id = self._getGraphID(service_graph_id)
        session_id = Session().get_active_user_session_by_nf_fg_id(service_graph_id)
        endpoints = self.getEndpoints(session_id)
        for endpoint in endpoints:
            if endpoint.type == endpoint_name:
                return self.checkConnection(endpoint.id)
        
    def checkConnection(self, endpoint_id):
        session = get_session() 
        return session.query(GraphConnectionModel).filter_by(endpoint_id_2 = endpoint_id).all()

    def getNodeID(self, session_id):
        session = get_session()
        return session.query(GraphModel.node_id).filter_by(session_id = session_id).one().node_id

    def setNodeID(self, session_id, node_id):
        session = get_session()
        with session.begin():
            logging.debug(session.query(GraphModel).filter_by(session_id = str(session_id)).update({"node_id":node_id}))
            
    def addNFFG(self, nffg, session_id, partial=False, default_status = 'initialization'):
        session = get_session()  
        with session.begin():
            self._id_generator(nffg, session_id)
            
            '''
            attributes = ['id', 'session_id','node_id','partial']
            '''
            graph_ref = GraphModel(id=nffg.db_id, session_id=session_id, partial=partial)
            session.add(graph_ref)
            for vnf in nffg.listVNF:
                '''
                attributes = ['id', 'internal_id', 'graph_vnf_id','session_id', 'graph_id',
                               'name','template_location', 'image_location', 'location',
                               'type', 'status', 'creation_date','last_update', 'avialability_zone']
                '''
                
                vnf_ref = VNFModel(id=vnf.db_id, graph_vnf_id = vnf.id, session_id=session_id,
                                   graph_id=nffg.db_id, name=vnf.name, template_location=vnf.template,
                                   creation_date=datetime.datetime.now(), last_update=datetime.datetime.now(), status=default_status)
                session.add(vnf_ref)
                for port in vnf.listPort:
                    '''
                    attributes = ['id', 'internal_id', 'graph_port_id','session_id', 'graph_id',
                                 'name','vnf_id', 'location','type', 'virtual_switch', 'status', 
                                 'creation_date','last_update', 'os_network_id','mac_address', 
                                 'ipv4_address', 'vlan_id','gre_key']
                    '''
                    port_ref = PortModel(id=port.db_id, graph_port_id = port.id, session_id=session_id,
                                   graph_id=nffg.db_id, name=port.id, vnf_id=vnf.db_id,
                                   creation_date=datetime.datetime.now(), last_update=datetime.datetime.now(), status=default_status)
                    session.add(port_ref)                        
                            
                    for o_arch in port.list_outgoing_label:
                        '''
                        attributes = ['id', 'internal_id', 'graph_o_arch_id','session_id', 'graph_id',
                                     'type','start_node_type', 'start_node_id','end_node_type',
                                      'end_node_id', 'creation_date','last_update']
                        '''
                                    
                        start_node_id = port.db_id
                        start_node_type = 'port'
                        if o_arch.action.endpoint is not None:
                            end_node_type = 'endpoint'
                            end_node_id = nffg.getEndpointByID(o_arch.action.endpoint['id']).db_id
                        elif o_arch.action.vnf is not None:
                            end_node_type = 'port'
                            end_node_id = nffg.getVNFByID(o_arch.action.vnf['id']).getPortFromID(o_arch.action.vnf['port']).db_id
                        
                        self._add_flowrule(session, session_id, nffg, o_arch, start_node_type, start_node_id, end_node_type, end_node_id)
                    for o_arch in port.list_ingoing_label:
                        start_node_id = nffg.getEndpointByID(o_arch.flowspec['ingress_endpoint']).db_id
                        start_node_type = 'endpoint'                    
                        end_node_type = 'port'
                        end_node_id = port.db_id

                        self._add_flowrule(session, session_id, nffg, o_arch, start_node_type, start_node_id, end_node_type, end_node_id)

            for endpoint in nffg.listEndpoint:
                '''
                attributes = ['id', 'internal_id', 'graph_endpoint_id','session_id','graph_id',
                            'type','location']
                '''
                endpoint_ref = EndpointModel(id=endpoint.db_id, graph_endpoint_id=endpoint.id, session_id=session_id,
                                             graph_id=nffg.db_id, type=endpoint.name)
                session.add(endpoint_ref)
                
                # Add end-point resources
                # End-point attached to something that is not another graph
                if endpoint.attached is not None and endpoint.attached is True:
                    if endpoint.type is not None and endpoint.type == 'physical':
                        port_ref = PortModel(id=self.port_id, session_id=session_id,
                                   graph_id=nffg.db_id, internal_id=endpoint.interface, name=endpoint.interface, location=endpoint.node,
                                   creation_date=datetime.datetime.now(), last_update=datetime.datetime.now())
                        session.add(port_ref)
                        endpoint_resource_ref = EndpointResourceModel(endpoint_id=endpoint.db_id,
                                              resource_type='port',
                                              resource_id=self.port_id,
                                              session_id=session_id)
                        session.add(endpoint_resource_ref)
                        self.port_id = self.port_id + 1
                    
                # End-point attached to another graph
                if endpoint.connection is not None and endpoint.connection is True:
                    if endpoint.type is not None and endpoint.type == 'physical':
                        port_ref = PortModel(id=self.port_id, session_id=session_id,
                                   graph_id=endpoint.remote_graph, internal_id=endpoint.interface, name=endpoint.interface, location=endpoint.node,
                                   creation_date=datetime.datetime.now(), last_update=datetime.datetime.now())
                        session.add(port_ref)
                        endpoint_resource_ref = EndpointResourceModel(endpoint_id=endpoint.db_id,
                                                                      resource_type='port',
                                                                      resource_id=self.port_id,
                                                                      session_id=session_id)
                        session.add(endpoint_resource_ref)
                        self.port_id = self.port_id + 1
                        
                    
                    # Add graph connection
                    remote_graph_db_id =  self._getGraphID(endpoint.remote_graph)
                    endpoint2_db_id = self._getEndpointID(endpoint.remote_id, remote_graph_db_id)
                    graph_connection_ref = GraphConnectionModel(endpoint_id_1=endpoint.db_id, endpoint_id_2=endpoint2_db_id)
                    session.add(graph_connection_ref)
                    
    def getEndpoints(self, session_id):
        session = get_session()  
        return session.query(EndpointModel).filter_by(session_id = session_id).all()

    def get_instantiated_nffg(self, user_id):
        service_graph_id = self.user_session.get_profile_id_from_active_user_session(user_id)
        nffg = self.get_nffg(service_graph_id)    
        return nffg
    
    def delete_graph(self, session_id):
        session = get_session()
        with session.begin():
            session.query(GraphModel).filter_by(session_id = session_id).delete()
            session.query(VNFModel).filter_by(session_id = session_id).delete()
            session.query(PortModel).filter_by(session_id = session_id).delete()
            session.query(FlowspecModel).filter_by(session_id= session_id).delete()
            session.query(EndpointModel).filter_by(session_id = session_id).delete()
            session.query(EndpointResourceModel).filter_by(session_id = session_id).delete()
    
    def get_nffg(self, session_id, encode=False):
        nffg = NF_FG()
        session = get_session()
        graphs_ref = session.query(GraphModel).filter_by(session_id = session_id).all()
        service_graph_info_ref = Session().get_service_graph_info(session_id)

        nffg._id = service_graph_info_ref.service_graph_id
        nffg.name = service_graph_info_ref.service_graph_name
        vnfs_ref = session.query(VNFModel).filter_by(session_id = session_id).all()
        for vnf_ref in vnfs_ref:
            vnf = nffg.createVNF(vnf_ref.name, vnf_ref.template_location, vnf_ref.graph_vnf_id)
            ports_ref = session.query(PortModel).filter_by(session_id = session_id).filter_by(vnf_id = str(vnf_ref.id)).all()
            for port_ref in ports_ref:
                port = vnf.addPort(vnf=vnf,port_id=port_ref.graph_port_id)
                o_archs_ref = session.query(O_ArchModel).filter_by(session_id = session_id).filter_by(start_node_type = "port").filter_by(start_node_id = port_ref.id).all()
                for o_arch_ref in o_archs_ref:
                    if o_arch_ref.end_node_type == 'port':
                        connected_port_ref = session.query(PortModel).filter_by(id = o_arch_ref.end_node_id).first()
                        connected_vnf_ref = session.query(VNFModel).filter_by(id = connected_port_ref.vnf_id).first()
                        if connected_port_ref is not None:
                            flowspecs_ref = session.query(FlowspecModel).filter_by(o_arch_id= o_arch_ref.id).all()
                            for flowspec_ref in flowspecs_ref:
                                flowrule = port.setFlowRuleToVNF(connected_vnf_ref.graph_vnf_id, connected_port_ref.graph_port_id)
                                of_field=self._encode_of_field(flowspec_ref)
                                matches = []
                                matches.append(Match(priority= flowspec_ref.priority, match_id=flowspec_ref.id, of_field=of_field))
                                flowrule.changeMatches(matches)
                            
                    elif o_arch_ref.end_node_type == 'endpoint':
                        connected_endpoint_ref = session.query(EndpointModel).filter_by(id = o_arch_ref.end_node_id).first()
                        if connected_endpoint_ref is not None:
                            flowspecs_ref = session.query(FlowspecModel).filter_by(o_arch_id= o_arch_ref.id).all()
                            for flowspec_ref in flowspecs_ref:
                                flowrule = port.setFlowRuleToEndpoint(connected_endpoint_ref.graph_endpoint_id)
                                of_field=self._encode_of_field(flowspec_ref)
                                matches = []
                                matches.append(Match(priority=flowspec_ref.priority, match_id=flowspec_ref.id, of_field=of_field))
                                flowrule.changeMatches(matches)
                        
                        # TODO: find arch from endpoint to this port
                        #connection_from_endpoints_ref = session.query(O_ArchModel).filter_by(session_id = session_id).filter_by(start_node_type = "endpoint").filter_by(end_node_type = "port").filter_by(end_node_id = port_ref.id).join(O_ArchModel.start_node_id).join(EndpointModel.id).all()
                        #session.query(O_ArchModel).filter_by(session_id = session_id).filter_by(start_node_type = "endpoint").filter_by(end_node_type = "port").filter_by(end_node_id = port_ref.id).join(O_ArchModel.start_node_id).join(EndpointModel.id).all()
                        connection_from_endpoints_ref = session.query(EndpointModel,O_ArchModel.id).filter(O_ArchModel.start_node_id == EndpointModel.id).filter(O_ArchModel.session_id == session_id).filter(O_ArchModel.start_node_type == "endpoint").filter(O_ArchModel.end_node_type == "port").filter(O_ArchModel.end_node_id == port_ref.id).all()
                        
                        for connection_from_endpoint_ref, ingress_o_arch_id_from_endpoint in connection_from_endpoints_ref:
                            flowspecs_ref = session.query(FlowspecModel).filter_by(o_arch_id= ingress_o_arch_id_from_endpoint).all()
                            for flowspec_ref in flowspecs_ref:
                                flowrule = port.setFlowRuleFromEndpoint(vnf.id, connection_from_endpoint_ref.graph_endpoint_id)
                                of_field=self._encode_of_field(flowspec_ref)
                                matches = []
                                matches.append(Match(priority=flowspec_ref.priority, match_id=flowspec_ref.id, of_field=of_field))
                                flowrule.changeMatches(matches)
                        
                            
        endpoints_ref = session.query(EndpointModel).filter_by(session_id = session_id).all()
        for endpoint_ref in endpoints_ref:
            endpoint = nffg.createEndpoint(endpoint_ref.type, endpoint_id=endpoint_ref.graph_endpoint_id)
            # TODO: endpoint resource
            endpoint_resorces_ref = session.query(EndpointResourceModel).filter_by(endpoint_id = endpoint_ref.id).filter_by(session_id = session_id).all()
            for endpoint_resorce_ref in endpoint_resorces_ref:
                if endpoint_resorce_ref.resource_type == 'port':
                    port = self._getPort(endpoint_resorce_ref.resource_id)
                    nffg.characterizeEndpoint(endpoint, endpoint_type = endpoint_resorce_ref.resource_type, interface = port.graph_port_id, node = port.location)
                    internal = False
                    for graph_ref in graphs_ref:
                        logging.debug("port.graph_id: "+str(port.graph_id)+" graph_ref.id: "+str(graph_ref.id))
                        if str(port.graph_id) == str(graph_ref.id):
                            internal=True
                            break
                    if internal is False:
                        service_graph_info_ref =  Session().get_service_graph_info(port.session_id)
                        endpoint.remote_graph = service_graph_info_ref.service_graph_id
                        endpoint.remote_graph_name = service_graph_info_ref.service_graph_name
            
                        graph_connection_ref = session.query(GraphConnectionModel).filter_by(endpoint_id_1 = endpoint_ref.id).one()
                        endpoint.remote_id = self._getEndpoint(graph_connection_ref.endpoint_id_2)

        if encode:
            return nffg.getJSON()
        else:
            return nffg
    
    def get_nffg_by_id(self, service_graph_id):
        session = Session().get_active_user_session_by_nf_fg_id(service_graph_id)
        logging.debug('[get_nffg_by_id] session id: '+str(session.id))
        return self.get_nffg(session.id)
    
    def _getPort(self, port_db_id):
        session = get_session()  
        try:
            return session.query(PortModel).filter_by(id=port_db_id).one()
        except Exception as ex:
            logging.error(ex)
            raise PortNotFound("Port Not Found for db id: "+str(port_db_id))
    
    def _getGraph(self, graph_id):
        session = get_session()  
        try:
            return session.query(GraphModel).filter_by(id=graph_id).one()
        except Exception as ex:
            logging.error(ex)
            raise GraphNotFound("Graph not found for db id: "+str(graph_id))
    
    def _getGraphID(self, service_graph_id):
        session = get_session()  
        try:
            session_id = Session().get_active_user_session_by_nf_fg_id(service_graph_id).id
            return session.query(GraphModel).filter_by(session_id=session_id).one().id
        except Exception as ex:
            logging.error(ex)
            raise GraphNotFound("Graph not found for service graph id: "+str(service_graph_id))
    
    def _getEndpoint(self, endpoint_id):
        session = get_session()  
        try:
            return session.query(EndpointModel).filter_by(id=endpoint_id).one()
        except Exception as ex:
            logging.error(ex)
            raise EndpointNotFound("Endpoint not found: ")
    
    def _getEndpointID(self, graph_endpoint_id, graph_id):
        session = get_session()  
        try:
            return session.query(EndpointModel).filter_by(graph_endpoint_id=graph_endpoint_id).filter_by(graph_id=graph_id).one()
        except Exception as ex:
            logging.error(ex)
            raise EndpointNotFound("Endpoint not found: ")
    
    def _id_generator(self, nffg, session_id):
        graph_base_id = self._get_higher_graph_id()
        print "graph_base_id: "+str(graph_base_id)
        vnf_base_id = self._get_higher_vnf_id()
        print "vnf_base_id: "+str(vnf_base_id)
        port_base_id = self._get_higher_port_id()
        print "port_base_id: "+str(port_base_id)
        endpoint_base_id = self._get_higher_endpoint_id()
        print "endpoint_base_id: "+str(endpoint_base_id)
        o_arch_base_id = self._get_higher_o_arch_id()
        print "o_arch_base_id: "+str(o_arch_base_id)
        flowspec_base_id = self._get_higher_flowspec_id()
        print "flowspec_base_id: "+str(flowspec_base_id)
        if graph_base_id is not None:
            self.graph_id = int(graph_base_id) + 1
        else:
            self.graph_id = 0
        if vnf_base_id is not None:
            self.vnf_id = int(vnf_base_id) + 1
        else:
            self.vnf_id = 0
        if port_base_id is not None:
            self.port_id = int(port_base_id) + 1
        else:
            self.port_id = 0
        if endpoint_base_id is not None:
            self.endpoint_id = int(endpoint_base_id) + 1
        else:
            self.endpoint_id = 0
        if o_arch_base_id is not None:
            self.o_arch_id = int(o_arch_base_id) + 1
        else:
            self.o_arch_id = 0
        if flowspec_base_id is not None:
            self.flowspec_id = int(flowspec_base_id) + 1
        else:
            self.flowspec_id = 0  
        nffg.db_id = self.graph_id
        for vnf in nffg.listVNF:
            vnf.db_id = self.vnf_id
            self.vnf_id = self.vnf_id+1
            for port in vnf.listPort:
                port.db_id = self.port_id
                self.port_id = self.port_id + 1
                for o_arch in port.list_outgoing_label:  
                    o_arch.db_id = self.o_arch_id
                    self.o_arch_id = self.o_arch_id +1
                    for match in o_arch.matches:
                        match.db_id = self.flowspec_id
                        self.flowspec_id = self.flowspec_id + 1
                for o_arch in port.list_ingoing_label:  
                    o_arch.db_id = self.o_arch_id
                    self.o_arch_id = self.o_arch_id + 1
                    for match in o_arch.matches:
                        match.db_id = self.flowspec_id
                        self.flowspec_id = self.flowspec_id + 1
        for endpoint in nffg.listEndpoint:
            endpoint.db_id = self.endpoint_id 
            self.endpoint_id = self.endpoint_id + 1
    
    def _get_higher_graph_id(self):  
        session = get_session()  
        return session.query(func.max(GraphModel.id).label("max_id")).one().max_id
    
    def _get_higher_vnf_id(self):
        session = get_session()  
        return session.query(func.max(VNFModel.id).label("max_id")).one().max_id
        
    def _get_higher_port_id(self):
        session = get_session()  
        return session.query(func.max(PortModel.id).label("max_id")).one().max_id
        
    def _get_higher_endpoint_id(self):
        session = get_session()  
        return session.query(func.max(EndpointModel.id).label("max_id")).one().max_id
        
    def _get_higher_o_arch_id(self):
        session = get_session()  
        return session.query(func.max(O_ArchModel.id).label("max_id")).one().max_id
    
    def _get_higher_flowspec_id(self):
        session = get_session()  
        return session.query(func.max(FlowspecModel.id).label("max_id")).one().max_id
    
    def _add_flowrule(self, session, session_id, nffg, o_arch, start_node_type, start_node_id, end_node_type, end_node_id):
        o_arch_ref = O_ArchModel(id=o_arch.db_id, graph_o_arch_id = str(start_node_id)+":"+str(end_node_id), session_id=session_id,
                                    graph_id=nffg.db_id, start_node_type=start_node_type,
                                    start_node_id=start_node_id, end_node_type=end_node_type,
                                    end_node_id=end_node_id,
                                    creation_date=datetime.datetime.now(), last_update=datetime.datetime.now())
        session.add(o_arch_ref)
        

        for match in o_arch.matches:
            '''
            attributes = ['id', 'o_arch_id', 'priority', 'etherType','vlanId','vlanPriority',
                     'dlSrc','dlDst','nwSrc','nwDst','tosBits','tpSrc', 'tpDst',
                     'protocol']
            '''
            if 'etherType' in match.of_field:
                etherType=match.of_field['etherType']
            else:
                etherType = None
            if 'vlanId' in match.of_field:
                vlanId=match.of_field['vlanId']
            else:
                vlanId = None
            if 'vlanPriority' in match.of_field:
                vlanPriority=match.of_field['vlanPriority']
            else:
                vlanPriority = None
            if 'sourceMAC' in match.of_field:
                dlSrc=match.of_field['sourceMAC']
            else:
                dlSrc = None
            if 'destMAC' in match.of_field:
                dlDst=match.of_field['destMAC']
            else:
                dlDst = None
            if 'sourceIP' in match.of_field:
                nwSrc=match.of_field['sourceIP']
            else:
                nwSrc = None
            if 'destIP' in match.of_field:
                nwDst=match.of_field['destIP']
            else:
                nwDst = None
            if 'tosBits' in match.of_field:
                tosBits=match.of_field['tosBits']
            else:
                tosBits = None
            if 'sourcePort' in match.of_field:
                tpSrc=match.of_field['sourcePort']
            else:
                tpSrc = None
            if 'destPort' in match.of_field:
                tpDst=match.of_field['destPort']
            else:
                tpDst = None
            if 'protocol' in match.of_field:
                protocol=match.of_field['protocol']
            else:
                protocol = None
            

            flowspec_ref = FlowspecModel(id = match.db_id, match_id = match.id, o_arch_id=o_arch.db_id ,
                          session_id=session_id, graph_id = nffg.db_id,
                          priority=match.priority, etherType=etherType,
                          vlanId=vlanId,vlanPriority=vlanPriority,
                          dlSrc=dlSrc,dlDst=dlDst,
                          nwSrc=nwSrc,nwDst=nwDst,
                          tosBits=tosBits,tpSrc=tpSrc,
                          tpDst=tpDst,protocol=protocol)
            session.add(flowspec_ref)

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
        
