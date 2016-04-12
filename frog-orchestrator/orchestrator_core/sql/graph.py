'''
Created on Jun 20, 2015

@author: fabiomignini
'''
from exceptions import Exception 
from sqlalchemy import Column, VARCHAR, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from orchestrator_core.sql.sql_server import get_session
from sqlalchemy.sql import func
from sqlalchemy.orm.exc import NoResultFound

from orchestrator_core.config import Configuration
from orchestrator_core.sql.session import Session
import datetime
import logging
from nffg_library.nffg import NF_FG, VNF, Port, EndPoint, FlowRule, Match, Action
from orchestrator_core.exception import EndpointNotFound, PortNotFound, GraphNotFound

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
    
class VNFInstanceModel(Base):
    '''
    Maps the database table node
    '''
    __tablename__ = 'vnf_instance'
    attributes = ['id', 'internal_id', 'graph_vnf_id', 'graph_id', 'name','template_location', 'image_location', 'location','type', 'status', 'creation_date','last_update', 'availability_zone']
    id = Column(Integer, primary_key=True)
    internal_id = Column(VARCHAR(64)) # id in the infrastructure
    graph_vnf_id = Column(VARCHAR(64)) # id in the json
    graph_id = Column(Integer)
    name = Column(VARCHAR(64))
    template_location = Column(VARCHAR(64))
    image_location = Column(VARCHAR(64))
    location = Column(VARCHAR(64)) # node where the VNF is instantiated
    type = Column(VARCHAR(64)) # es. docker or virtual-machine
    status = Column(VARCHAR(64)) # initialization, complete, error
    creation_date = Column(VARCHAR(64))
    last_update = Column(VARCHAR(64))
    availability_zone = Column(VARCHAR(64)) 

class PortModel(Base):
    '''
    Maps the database table node
    '''
    __tablename__ = 'port'
    attributes = ['id', 'internal_id', 'graph_port_id', 'graph_id', 'name','vnf_id', 'location','type', 'virtual_switch', 'status', 'creation_date','last_update', 'os_network_id',
                    'mac_address', 'ipv4_address', 'vlan_id','gre_key']
    id = Column(Integer, primary_key=True)
    internal_id = Column(VARCHAR(64)) # id in the infrastructure
    graph_port_id = Column(VARCHAR(64)) # id in the json
    graph_id = Column(Integer)
    name = Column(VARCHAR(64))
    vnf_id = Column(VARCHAR(64)) # could be NULL, for example a port in an end-point
    location = Column(VARCHAR(64)) # node where the port is instantiated
    type = Column(VARCHAR(64)) # OpenStack port, etc.
    virtual_switch = Column(VARCHAR(64))
    status = Column(VARCHAR(64)) # initialization, complete, error
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
    attributes = ['id', 'internal_id', 'graph_endpoint_id','graph_id','name', 'type','location']
    id = Column(Integer, primary_key=True)
    internal_id = Column(VARCHAR(64)) # id of the infrastructure graph
    graph_endpoint_id = Column(VARCHAR(64)) # id in the json
    graph_id = Column(VARCHAR(64))
    name = Column(VARCHAR(64))
    type = Column(VARCHAR(64)) # internal, interface, interface-out, vlan, gre
    location = Column(VARCHAR(64)) # node where the end-point is instantiated
    
class EndpointResourceModel(Base):
    '''
    Maps the database table endpoint_resource
    '''
    __tablename__ = 'endpoint_resource'
    attributes = ['endpoint_id', 'resource_type', 'resource_id']
    endpoint_id = Column(Integer, primary_key=True)
    resource_type = Column(VARCHAR(64), primary_key=True) # port or flow-rule (flow-rule will be the flow-rules that connect the end-point to an external end-point)
    resource_id = Column(Integer, primary_key=True)

class FlowRuleModel(Base):
    '''
    Maps the database table node
    '''
    __tablename__ = 'flow_rule'
    attributes = ['id', 'internal_id', 'graph_flow_rule_id', 'graph_id','node_id', 'type', 'priority','status', 'creation_date','last_update']
    id = Column(Integer, primary_key=True)
    internal_id = Column(VARCHAR(64)) # id of the infrastructure graph
    graph_flow_rule_id = Column(VARCHAR(64)) # id in the json
    graph_id = Column(VARCHAR(64))
    node_id = Column(VARCHAR(64))
    type = Column(VARCHAR(64))
    priority = Column(VARCHAR(64)) # openflow priority    
    status = Column(VARCHAR(64)) # initialization, complete, error
    creation_date = Column(VARCHAR(64))
    last_update = Column(VARCHAR(64))
    
class MatchModel(Base):
    '''
    Maps the database table match
    '''
    __tablename__ = 'match'

    attributes = ['id', 'flow_rule_id', 'port_in_type', 'port_in', 'ether_type','vlan_id','vlan_priority', 'source_mac','dest_mac','source_ip',
                 'dest_ip','tos_bits','source_port', 'dest_port', 'protocol']
    id = Column(Integer, primary_key=True)
    flow_rule_id = Column(Integer)
    port_in_type = Column(VARCHAR(64)) # port or endpoint
    port_in = Column(VARCHAR(64))
    ether_type = Column(VARCHAR(64))
    vlan_id = Column(VARCHAR(64))
    vlan_priority = Column(VARCHAR(64))
    source_mac = Column(VARCHAR(64))
    dest_mac = Column(VARCHAR(64))
    source_ip = Column(VARCHAR(64))
    dest_ip = Column(VARCHAR(64))
    tos_bits = Column(VARCHAR(64))
    source_port = Column(VARCHAR(64))
    dest_port = Column(VARCHAR(64))
    protocol = Column(VARCHAR(64))

class ActionModel(Base):
    '''
    Maps the database table action
    '''
    __tablename__ = 'action'

    attributes = ['id', 'flow_rule_id', 'output_type', 'output', 'controller', '_drop', 'set_vlan_id','set_vlan_priority','pop_vlan', 'set_ethernet_src_address',
                  'set_ethernet_dst_address','set_ip_src_address','set_ip_dst_address', 'set_ip_tos','set_l4_src_port','set_l4_dst_port', 'output_to_queue']    
    id = Column(Integer, primary_key=True)
    flow_rule_id = Column(Integer)
    output_type = Column(VARCHAR(64)) # port or endpoint
    output = Column(VARCHAR(64))
    controller = Column(Boolean)
    _drop = Column(Boolean)
    set_vlan_id = Column(VARCHAR(64))
    set_vlan_priority = Column(VARCHAR(64))
    pop_vlan = Column(Boolean)
    set_ethernet_src_address = Column(VARCHAR(64))
    set_ethernet_dst_address = Column(VARCHAR(64))
    set_ip_src_address = Column(VARCHAR(64))
    set_ip_dst_address = Column(VARCHAR(64))
    set_ip_tos = Column(VARCHAR(64))
    set_l4_src_port = Column(VARCHAR(64))
    set_l4_dst_port = Column(VARCHAR(64))
    output_to_queue = Column(VARCHAR(64))


class GraphConnectionModel(Base):
    '''
    Maps the database table graph_connection
    '''
    __tablename__ = 'graph_connection'
    attributes = ['endpoint_id_1', 'endpoint_id_1_type', 'endpoint_id_2', 'endpoint_id_2_type']
    endpoint_id_1 = Column(VARCHAR(64), primary_key=True)
    endpoint_id_1_type = Column(VARCHAR(64), primary_key=True) # internal (the endpoint exists in the DB), external (the endpoint doesn't exist in the DB, its value will be graph_id:endpoint_graph_id)
    endpoint_id_2 = Column(VARCHAR(64), primary_key=True)
    endpoint_id_2_type = Column(VARCHAR(64), primary_key=True) # internal (the endpoint exists in the DB), external (the endpoint doesn't exist in the DB, its value will be graph_id:endpoint_graph_id)
    
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

    def get_nffg(self, graph_id, complete=False):
        nffg = NF_FG()
        session = get_session()
        graph_ref = session.query(GraphModel).filter_by(id = graph_id).one()
        service_graph_info_ref = Session().get_service_graph_info(graph_ref.session_id)

        if graph_ref.partial is True:
            nffg.id = graph_ref.id
        else:
            nffg.id = service_graph_info_ref.service_graph_id
        nffg.name = service_graph_info_ref.service_graph_name
        nffg.db_id = graph_ref.id
        
        # VNFs
        vnfs_ref = session.query(VNFInstanceModel).filter_by(graph_id = graph_id).all()
        for vnf_ref in vnfs_ref:
            if complete is False and 'end-point-switch' in vnf_ref.name:
                continue
            vnf = VNF(_id=vnf_ref.graph_vnf_id, name=vnf_ref.name, vnf_template_location=vnf_ref.template_location,
                db_id=vnf_ref.id, internal_id=vnf_ref.internal_id)
            nffg.addVNF(vnf)
            
            # Ports
            ports_ref = session.query(PortModel).filter_by(graph_id = graph_id).filter_by(vnf_id = str(vnf.db_id)).all()
            for port_ref in ports_ref:
                port = Port(_id=port_ref.graph_port_id, name=port_ref.name, _type=port_ref.type,
                      db_id=port_ref.id, internal_id=port_ref.internal_id)
                vnf.addPort(port)
                
        # FlowRules
        flow_rules_ref = session.query(FlowRuleModel).filter_by(graph_id = graph_id).all()
        for flow_rule_ref in flow_rules_ref:
            if complete is False and flow_rule_ref.type is not None and (flow_rule_ref.type == 'external' or 'connection_end_point' in flow_rule_ref.type):
                continue
            flow_rule = FlowRule(_id=flow_rule_ref.graph_flow_rule_id, priority=int(flow_rule_ref.priority),
                      db_id=flow_rule_ref.id, internal_id=flow_rule_ref.internal_id)
            nffg.addFlowRule(flow_rule)
            try:
                
                # Match
                match_ref = session.query(MatchModel).filter_by(flow_rule_id = flow_rule.db_id).one()
                if match_ref.port_in_type == 'port':
                    port_ref = session.query(PortModel).filter_by(id = match_ref.port_in).first()
                    vnf_ref = session.query(VNFInstanceModel).filter_by(id = port_ref.vnf_id).first()
                    port_in = 'vnf:'+vnf_ref.graph_vnf_id+':'+port_ref.graph_port_id
                elif match_ref.port_in_type == 'endpoint':
                    end_point_ref = session.query(EndpointModel).filter_by(id = match_ref.port_in).first()
                    port_in = match_ref.port_in_type+':'+end_point_ref.graph_endpoint_id
                match = Match(port_in=port_in, ether_type=match_ref.ether_type, vlan_id=match_ref.vlan_id,
                       vlan_priority=match_ref.vlan_priority, source_mac=match_ref.source_mac,
                        dest_mac=match_ref.dest_mac, source_ip=match_ref.source_ip, dest_ip=match_ref.dest_ip,
                        tos_bits=match_ref.tos_bits, source_port=match_ref.source_port, dest_port=match_ref.dest_port,
                         protocol=match_ref.protocol, db_id=match_ref.id)
                flow_rule.match = match
            except NoResultFound:
                logging.info("Found flowrule without a match")
            try:
                
                # Actions
                actions_ref = session.query(ActionModel).filter_by(flow_rule_id = flow_rule.db_id).all()
                for action_ref in actions_ref:
                    output = None
                    if action_ref.output_type == 'port':
                        port_ref = session.query(PortModel).filter_by(id = action_ref.output).first()
                        vnf_ref = session.query(VNFInstanceModel).filter_by(id = port_ref.vnf_id).first()
                        output = 'vnf:'+vnf_ref.graph_vnf_id+':'+port_ref.graph_port_id
                    elif action_ref.output_type == 'endpoint':
                        end_point_ref = session.query(EndpointModel).filter_by(id = action_ref.output).first()
                        output = action_ref.output_type+':'+end_point_ref.graph_endpoint_id
                    action = Action(output=output, controller=action_ref.controller, drop=action_ref._drop, set_vlan_id=action_ref.set_vlan_id,
                                    set_vlan_priority=action_ref.set_vlan_priority, pop_vlan=action_ref.pop_vlan, 
                                    set_ethernet_src_address=action_ref.set_ethernet_src_address, 
                                    set_ethernet_dst_address=action_ref.set_ethernet_dst_address, 
                                    set_ip_src_address=action_ref.set_ip_src_address, set_ip_dst_address=action_ref.set_ip_dst_address, 
                                    set_ip_tos=action_ref.set_ip_tos, set_l4_src_port=action_ref.set_l4_src_port, 
                                    set_l4_dst_port=action_ref.set_l4_dst_port, output_to_queue=action_ref.output_to_queue,
                                    db_id=action_ref.id)
                    flow_rule.actions.append(action)
            except NoResultFound:
                logging.debug("Found flowrule without actions")
            
        # EndPoints           
        end_points_ref = session.query(EndpointModel).filter_by(graph_id = graph_id).all()
        for end_point_ref in end_points_ref:
            if complete is False and end_point_ref.type is not None and 'connection_end_point' in end_point_ref.type:
                continue
                
            end_point = EndPoint(_id=end_point_ref.graph_endpoint_id, name=end_point_ref.name, _type=end_point_ref.type,
                                 db_id=end_point_ref.id, internal_id=end_point_ref.internal_id)
            nffg.addEndPoint(end_point)
            
            
            # EndPoint resources
            end_point_resorces_ref = session.query(EndpointResourceModel).filter_by(endpoint_id = end_point_ref.id).all()
            for end_point_resorce_ref in end_point_resorces_ref:
                if end_point_resorce_ref.resource_type == 'port':
                    try:
                        port = self._getPort(end_point_resorce_ref.resource_id)
                    except PortNotFound:
                        raise Exception("I dont'know when I'm here. There was a continue here, why?")
                        #continue
                        
                    end_point.node = port.location
                    end_point.switch_id = port.virtual_switch
                    end_point.interface = port.graph_port_id
                    end_point.vlan_id = port.vlan_id
                    
            graph_connections_ref = session.query(GraphConnectionModel).filter_by(endpoint_id_1 = str(graph_id)+':'+end_point_ref.graph_endpoint_id).filter_by(endpoint_id_1_type = 'external').all()
            for graph_connection_ref in graph_connections_ref:
                ext_endpoint = self._getEndpoint(graph_connection_ref.endpoint_id_2)
                ext_nffg_id = ext_endpoint.graph_id
                external_graph = self.get_nffg(ext_endpoint.graph_id, complete=True)
                same_ext_endpoints = external_graph.getEndPointsFromName(ext_endpoint.name)
                for same_ext_endpoint in same_ext_endpoints:
                    if 'connection_end_point' not in same_ext_endpoint.type: 
                        end_point.remote_endpoint_id = ext_nffg_id+':'+same_ext_endpoint.id
            end_pont_connections_ref = self.getEndPointsFromName(graph_id, end_point_ref.name)
            for end_pont_connection_ref in end_pont_connections_ref:
                graph_connections_ref = session.query(GraphConnectionModel).filter_by(endpoint_id_2 = end_pont_connection_ref.id).filter_by(endpoint_id_2_type = 'internal').all()
                for graph_connection_ref in graph_connections_ref:
                    assert (graph_connection_ref.endpoint_id_1_type == 'external')
                    end_point.prepare_connection_to_remote_endpoint_ids.append(graph_connection_ref.endpoint_id_1)
        for end_point in nffg.end_points:
            if complete is False and end_point.type == 'shadow':
                same_end_points = nffg.getEndPointsFromName(end_point.name)
                for same_end_point in same_end_points:
                    if 'connection_end_point' in same_end_point.type:
                        end_point.type = same_end_point.type.split('connection_end_point')[0]
                        break
        return nffg
        
    def addNFFG(self, nffg, session_id, partial=False):
        session = get_session()  
        with session.begin():
            self.id_generator(nffg, session_id)
            graph_ref = GraphModel(id=nffg.db_id, session_id=session_id, partial=partial)
            session.add(graph_ref)
            for vnf in nffg.vnfs:
                vnf_ref = VNFInstanceModel(id=vnf.db_id, graph_vnf_id = vnf.id,
                                           graph_id=nffg.db_id, name=vnf.name, template_location=vnf.vnf_template_location,
                                           creation_date=datetime.datetime.now(), last_update=datetime.datetime.now(),
                                            status=vnf.status)
                session.add(vnf_ref)
                for port in vnf.ports:
                    port_ref = PortModel(id=port.db_id, graph_port_id = port.id, graph_id=nffg.db_id, 
                                         name=port.id, vnf_id=vnf.db_id, creation_date=datetime.datetime.now(),
                                         last_update=datetime.datetime.now(), status=port.status)
                    session.add(port_ref)                        
                            
            for flow_rule in nffg.flow_rules:
                
                self.addFlowRule(nffg.db_id, flow_rule, nffg)                
            for endpoint in nffg.end_points:
                endpoint_ref = EndpointModel(id=endpoint.db_id, graph_endpoint_id=endpoint.id, 
                                             graph_id=nffg.db_id, name = endpoint.name, type=endpoint.type)
                session.add(endpoint_ref)
                
                # Add end-point resources
                # End-point attached to something that is not another graph
                if "interface" in endpoint.type or endpoint.type == "vlan":
                    port_ref = PortModel(id=self.port_id, graph_port_id = endpoint.interface, graph_id=nffg.db_id, 
                                         internal_id=endpoint.interface, name=endpoint.interface, location=endpoint.node,
                                         virtual_switch=endpoint.switch_id, vlan_id=endpoint.vlan_id, creation_date=datetime.datetime.now(), 
                                         last_update=datetime.datetime.now())
                    session.add(port_ref)
                    endpoint_resource_ref = EndpointResourceModel(endpoint_id=endpoint.db_id,
                                          resource_type='port',
                                          resource_id=self.port_id)
                    session.add(endpoint_resource_ref)
                    self.port_id = self.port_id + 1
  
    def addFlowRule(self, graph_id, flow_rule, nffg):
        session = get_session()
        with session.begin():  
            # FlowRule
            if self._get_higher_flow_rule_id() is not None:
                flow_rule_db_id = self._get_higher_flow_rule_id() + 1
            else:
                flow_rule_db_id = 0
            flow_rule_ref = FlowRuleModel(id=flow_rule_db_id, internal_id=flow_rule.internal_id, 
                                       graph_flow_rule_id=flow_rule.id, graph_id=graph_id,
                                       priority=flow_rule.priority,  status=flow_rule.status,
                                       creation_date=datetime.datetime.now(), last_update=datetime.datetime.now(), type=flow_rule.type, node_id=flow_rule.node_id)
            session.add(flow_rule_ref)
            
            # Match
            if flow_rule.match is not None:
                match_db_id = flow_rule_db_id
                port_in_type = None
                port_in = None
                if flow_rule.match.port_in.split(':')[0] == 'vnf':
                    port_in_type = 'port'
                    port_in = nffg.getVNF(flow_rule.match.port_in.split(':')[1]).getPort(flow_rule.match.port_in.split(':')[2]+':'+flow_rule.match.port_in.split(':')[3]).db_id
                elif flow_rule.match.port_in.split(':')[0] == 'endpoint':
                    port_in_type = 'endpoint'
                    port_in = nffg.getEndPoint(flow_rule.match.port_in.split(':')[1]).db_id
                match_ref = MatchModel(id=match_db_id, flow_rule_id=flow_rule_db_id, port_in_type = port_in_type, port_in=port_in,
                                ether_type=flow_rule.match.ether_type, vlan_id=flow_rule.match.vlan_id,
                                vlan_priority=flow_rule.match.vlan_priority, source_mac=flow_rule.match.source_mac,
                                dest_mac=flow_rule.match.dest_mac, source_ip=flow_rule.match.source_ip,
                                dest_ip=flow_rule.match.dest_ip, tos_bits=flow_rule.match.tos_bits,
                                source_port=flow_rule.match.source_port, dest_port=flow_rule.match.dest_port,
                                protocol=flow_rule.match.protocol)
                session.add(match_ref)
            
            # Actions
            if flow_rule.actions:
                if self._get_higher_action_id() is not None:
                    action_db_id = self._get_higher_action_id() + 1
                else:
                    action_db_id = 0
                for action in flow_rule.actions:
                    output_type = None
                    output = None
                    if action.output != None and action.output.split(':')[0] == 'vnf':
                        output_type = 'port'
                        output = nffg.getVNF(action.output.split(':')[1]).getPort(action.output.split(':')[2]+':'+action.output.split(':')[3]).db_id
                    elif action.output != None and action.output.split(':')[0] == 'endpoint':
                        output_type = 'endpoint'
                        output = nffg.getEndPoint(action.output.split(':')[1]).db_id
                    action_ref = ActionModel(id=action_db_id, flow_rule_id=flow_rule_db_id,
                                             output_type=output_type, output=output,
                                             controller=action.controller, _drop=action.drop, set_vlan_id=action.set_vlan_id,
                                             set_vlan_priority=action.set_vlan_priority, pop_vlan=action.pop_vlan,
                                             set_ethernet_src_address=action.set_ethernet_src_address, 
                                             set_ethernet_dst_address=action.set_ethernet_dst_address,
                                             set_ip_src_address=action.set_ip_src_address, set_ip_dst_address=action.set_ip_dst_address,
                                             set_ip_tos=action.set_ip_tos, set_l4_src_port=action.set_l4_src_port,
                                             set_l4_dst_port=action.set_l4_dst_port, output_to_queue=action.output_to_queue)
                    session.add(action_ref)
                    action_db_id += 1
        return flow_rule_db_id
                    
    def addFlowRuleAsEndpointResource(self, graph_id, flow_rule, nffg, endpoint_id):
        session = get_session()
        with session.begin():  
            flow_rule_db_id = self.addFlowRule(graph_id, flow_rule, nffg)    
            endpoint_resource_ref = EndpointResourceModel(endpoint_id=endpoint_id,
                                                                  resource_type='flowrule',
                                                                  resource_id=flow_rule_db_id)
            session.add(endpoint_resource_ref)
    
    def updateNFFG(self, nffg, graph_id, partial=False):
        session = get_session()  
        with session.begin():
            self.id_generator(nffg=nffg, session_id=None, update=True, graph_id=graph_id)
            #graph_ref = GraphModel(id=nffg.db_id, session_id=session_id, partial=partial)
            #session.add(graph_ref)
            for vnf in nffg.vnfs:
                if vnf.status == 'new' or vnf.status is None:
                    vnf_ref = VNFInstanceModel(id=vnf.db_id, graph_vnf_id = vnf.id,
                                           graph_id=nffg.db_id, name=vnf.name, template_location=vnf.vnf_template_location,
                                           creation_date=datetime.datetime.now(), last_update=datetime.datetime.now(),
                                            status=vnf.status)
                    session.add(vnf_ref)
                for port in vnf.ports:
                    if port.status == 'new' or port.status is None:
                        port_ref = PortModel(id=port.db_id, graph_port_id = port.id, graph_id=nffg.db_id, 
                                         name=port.id, vnf_id=vnf.db_id, creation_date=datetime.datetime.now(),
                                         last_update=datetime.datetime.now(), status=port.status)
                        session.add(port_ref)                        
                            
            for flow_rule in nffg.flow_rules:
                if flow_rule.status == 'new' or flow_rule.status is None:
                    self.addFlowRule(nffg.db_id, flow_rule, nffg)            

            for endpoint in nffg.end_points:
                if endpoint.status == 'new' or endpoint.status is None:        
                    endpoint_ref = EndpointModel(id=endpoint.db_id, graph_endpoint_id=endpoint.id, 
                                             graph_id=nffg.db_id, name = endpoint.name, type=endpoint.type)
                    session.add(endpoint_ref)
                    
                    # Add end-point resources
                    # End-point attached to something that is not another graph
                    if "interface" in endpoint.type or endpoint.type == "vlan":
                        port_ref = PortModel(id=self.port_id, graph_port_id = endpoint.interface, graph_id=nffg.db_id, 
                                             internal_id=endpoint.interface, name=endpoint.interface, location=endpoint.node,
                                             virtual_switch=endpoint.switch_id, vlan_id=endpoint.vlan_id, creation_date=datetime.datetime.now(), 
                                             last_update=datetime.datetime.now())
                        session.add(port_ref)
                        endpoint_resource_ref = EndpointResourceModel(endpoint_id=endpoint.db_id,
                                              resource_type='port',
                                              resource_id=self.port_id)
                        session.add(endpoint_resource_ref)
                        self.port_id = self.port_id + 1
    
    def delete_session(self, session_id):
        session = get_session()
        graphs_ref = session.query(GraphModel).filter_by(session_id = session_id).all()
        for graph_ref in graphs_ref:
            self.delete_graph(graph_ref.id)
    
    def delete_graph(self, graph_id):
        session = get_session()
        with session.begin():
            session.query(GraphModel).filter_by(id = graph_id).delete()
            subnets_ref = session.query(OpenstackSubnetModel.id).\
                filter(OpenstackNetworkModel.id == OpenstackSubnetModel.os_network_id).\
                filter(OpenstackNetworkModel.id == PortModel.os_network_id).\
                filter(PortModel.graph_id == graph_id).all()
            for subnet_ref in subnets_ref:
                session.query(OpenstackSubnetModel).filter_by(id=subnet_ref.id).delete()
            networks_ref = session.query(OpenstackNetworkModel.id).filter(OpenstackNetworkModel.id == PortModel.os_network_id).filter(PortModel.graph_id == graph_id).all()
            for network_ref in networks_ref:
                session.query(OpenstackNetworkModel).filter_by(id=network_ref.id).delete()
            vnfs_ref = session.query(VNFInstanceModel).filter_by(graph_id = graph_id).all()
            for vnf_ref in vnfs_ref:
                session.query(PortModel).filter_by(vnf_id = vnf_ref.id).delete()
            session.query(VNFInstanceModel).filter_by(graph_id = graph_id).delete()
            
            session.query(PortModel).filter_by(graph_id = graph_id).delete()
              
            flow_rules_ref = session.query(FlowRuleModel).filter_by(graph_id = graph_id).all()
            for flow_rule_ref in flow_rules_ref:
                session.query(MatchModel).filter_by(flow_rule_id = flow_rule_ref.id).delete()
                session.query(ActionModel).filter_by(flow_rule_id = flow_rule_ref.id).delete()
            session.query(FlowRuleModel).filter_by(graph_id = graph_id).delete()
            endpoints_ref = session.query(EndpointModel.id).filter_by(graph_id = graph_id).all()
            for endpoint_ref in endpoints_ref:
                session.query(GraphConnectionModel).filter_by(endpoint_id_1 = endpoint_ref.id).filter_by(endpoint_id_1_type = 'internal').delete()
                session.query(GraphConnectionModel).filter_by(endpoint_id_2 = endpoint_ref.id).filter_by(endpoint_id_2_type = 'internal').delete()
                session.query(EndpointResourceModel).filter_by(endpoint_id = endpoint_ref.id).delete()
            session.query(EndpointModel).filter_by(graph_id = graph_id).delete()
        
    def id_generator(self, nffg, session_id, update=False, graph_id=None):
        graph_base_id = self._get_higher_graph_id()
        vnf_base_id = self._get_higher_vnf_id()
        port_base_id = self._get_higher_port_id()
        endpoint_base_id = self._get_higher_endpoint_id()
        flow_rule_base_id = self._get_higher_flow_rule_id()
        action_base_id = self._get_higher_action_id()
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
        if flow_rule_base_id is not None:
            self.flow_rule_id = int(flow_rule_base_id) + 1
        else:
            self.flow_rule_id = 0
        if action_base_id is not None:
            self.action_id = int(action_base_id) + 1
        else:
            self.action_id = 0  
        if update == False:
            nffg.db_id = self.graph_id
        else:
            session = get_session()  
            if graph_id is None:
                graphs_ref = session.query(GraphModel).filter_by(session_id = session_id).all()
                nffg.db_id = graphs_ref[0].id
            else:
                nffg.db_id = graph_id
        for vnf in nffg.vnfs:
            if vnf.status is None or vnf.status == "new":
                vnf.db_id = self.vnf_id
                self.vnf_id = self.vnf_id+1
            for port in vnf.ports:
                if port.status is None or port.status == "new":
                    port.db_id = self.port_id
                    self.port_id = self.port_id + 1
        for flow_rule in nffg.flow_rules: 
            if flow_rule.status is None or flow_rule.status == "new": 
                flow_rule.db_id = self.flow_rule_id
                self.flow_rule_id = self.flow_rule_id +1
            for action in flow_rule.actions:
                if flow_rule.status is None or flow_rule.status == "new":
                    action.db_id = self.action_id
                    self.action_id = self.action_id + 1
        for endpoint in nffg.end_points:
            if endpoint.status is None or endpoint.status == "new":   
                endpoint.db_id = self.endpoint_id 
                self.endpoint_id = self.endpoint_id + 1
    
    def _get_higher_graph_id(self):  
        session = get_session()  
        return session.query(func.max(GraphModel.id).label("max_id")).one().max_id
    
    def _get_higher_vnf_id(self):
        session = get_session()  
        return session.query(func.max(VNFInstanceModel.id).label("max_id")).one().max_id
        
    def _get_higher_port_id(self):
        session = get_session()  
        return session.query(func.max(PortModel.id).label("max_id")).one().max_id
        
    def _get_higher_endpoint_id(self):
        session = get_session()  
        return session.query(func.max(EndpointModel.id).label("max_id")).one().max_id
        
    def _get_higher_flow_rule_id(self):
        session = get_session()  
        return session.query(func.max(FlowRuleModel.id).label("max_id")).one().max_id
    
    def _get_higher_action_id(self):
        session = get_session()  
        return session.query(func.max(ActionModel.id).label("max_id")).one().max_id
    
    def getGraphs(self, session_id):
        session = get_session()
        return session.query(GraphModel).filter_by(session_id=session_id).all()
    
    def getUnusedNetworks(self):
        '''
        select openstack_network.id
        from openstack_network
        where openstack_network.id 
        not in ( select os_network_id 
                 from port 
                 where os_network_id is not NULL )
        '''
        session = get_session()
        used_networks_ref = session.query(PortModel.os_network_id).filter(PortModel.os_network_id != None)
        query = session.query(OpenstackNetworkModel.id).filter(~OpenstackNetworkModel.id.in_(used_networks_ref))
        unsed_networks_ref = query.all()
        return unsed_networks_ref

    def getNetwork(self, port_id):
        session = get_session()
        return session.query(OpenstackNetworkModel).\
                filter(OpenstackNetworkModel.id == PortModel.os_network_id).\
                filter(PortModel.id == port_id).one()
                
    def getHigherNumberOfNet(self, graph_id):
        session = get_session()
        networks = session.query(OpenstackNetworkModel.name).filter(PortModel.os_network_id == OpenstackNetworkModel.id).filter(PortModel.graph_id == graph_id).all()
        net_max = -1
        for network in networks:
            net_number = int(network.name.split('fakenet_')[1])
            if net_max < net_number:
                net_max = net_number
        return net_max+1
    
    def getFlowRules(self, graph_id):
        session = get_session()
        return session.query(FlowRuleModel).filter_by(graph_id = graph_id).all()
    
    def getVNFs(self, graph_id):
        session = get_session()
        return session.query(VNFInstanceModel).filter_by(graph_id = graph_id).all()
    
    def getPorts(self, graph_id):
        session = get_session()
        return session.query(PortModel).filter_by(graph_id = graph_id).all()

    def getSubnets(self, graph_id):
        session = get_session()
        return session.query(OpenstackSubnetModel.id).\
                filter(OpenstackNetworkModel.id == OpenstackSubnetModel.os_network_id).\
                filter(OpenstackNetworkModel.id == PortModel.os_network_id).\
                filter(PortModel.graph_id == graph_id).all()
    
    def getSubnet(self, os_network_id):
        session = get_session()
        return session.query(OpenstackSubnetModel.id).filter_by(os_network_id=os_network_id).one()
    
    def getPortNetwork(self, port_id):
        session = get_session()
        return session.query(OpenstackNetworkModel.id).filter(OpenstackNetworkModel.id == PortModel.os_network_id).filter(PortModel.id == port_id).one()

    def getNetworks(self, graph_id):
        session = get_session()
        return session.query(OpenstackNetworkModel.id).filter(OpenstackNetworkModel.id == PortModel.os_network_id).filter(PortModel.graph_id == graph_id).all()
    
    def getAllNetworks(self):
        session = get_session()
        return session.query(OpenstackNetworkModel).all()
    
    def setOSNetwork(self, os_network_id, graph_port_id, vnf_id, internal_id, graph_id, vlan_id = None, status='complete'):
        session = get_session()  
        with session.begin():
            assert (session.query(PortModel).filter_by(graph_port_id = graph_port_id).filter_by(vnf_id = vnf_id).filter_by(graph_id = graph_id).update({"os_network_id": os_network_id, 'vlan_id':vlan_id, "last_update":datetime.datetime.now(), 'status':status})==1)
       
    def addOSNetwork(self, os_network_id, name, status='complete', vlan_id = None):
        session = get_session() 
        with session.begin():            
            os_network_ref = OpenstackNetworkModel(id = os_network_id, name = name, status=status, vlan_id=vlan_id)
            session.add(os_network_ref)
    
    def addOSSubNet(self, os_subnet_id, name, os_network_id):
        session = get_session() 
        with session.begin():            
            os_network_ref = OpenstackSubnetModel(id = os_subnet_id, name = name, os_network_id=os_network_id)
            session.add(os_network_ref)
    
    def setPortInternalID(self, graph_id, vnf_id, port_graph_id, port_internal_id, port_status, port_type):
        session = get_session()
        logging.debug("graph_id: "+str(graph_id)+" vnf_id: "+str(vnf_id)+" port_graph_id: "+str(port_graph_id))
        with session.begin():
            res = session.query(PortModel).filter_by(graph_port_id = port_graph_id).filter_by(vnf_id = vnf_id).filter_by(graph_id = graph_id).update({"internal_id": port_internal_id,"last_update":datetime.datetime.now(), 'status':port_status, 'type':port_type})
            logging.debug("Num of tuple: "+str(res))
            assert (res==1)
            
    def setPortMacAddress(self, port_id, mac_address):
        session = get_session()  
        with session.begin():
            assert (session.query(PortModel).filter_by(id = port_id).update({"mac_address": mac_address,"last_update":datetime.datetime.now()})==1)
    
    def checkMacAddress(self, mac_address):
        session = get_session()  
        with session.begin():
            session.query(PortModel).filter_by(mac_address = mac_address).one()
                    
    def setVNFInternalID(self, graph_id, graph_vnf_id, internal_id, status):
        session = get_session()  
        with session.begin():
            assert (session.query(VNFInstanceModel).filter_by(graph_vnf_id = graph_vnf_id).filter_by(graph_id = graph_id).update({"internal_id": internal_id, "last_update":datetime.datetime.now(), 'status':status})==1)
  
    def setFlowRuleInternalID(self, graph_id, graph_flow_rule_id, internal_id, status='complete'):
        session = get_session()  
        with session.begin():
            session.query(FlowRuleModel).filter_by(graph_flow_rule_id = graph_flow_rule_id).filter_by(graph_id = graph_id).update({"internal_id": internal_id, "last_update":datetime.datetime.now(), 'status':status})
    
    def updateFlowRuleStatus(self, flow_rule_id, internal_id=None, status='complete'):
        session = get_session()  
        with session.begin():
            session.query(FlowRuleModel).filter_by(id = flow_rule_id).update({"internal_id": internal_id, "last_update":datetime.datetime.now(), 'status':status})
    
    def updateFlowRuleType(self, flow_rule_id, _type):
        session = get_session()  
        with session.begin():
            session.query(FlowRuleModel).filter_by(id = flow_rule_id).update({"type": _type, "last_update":datetime.datetime.now()})
       
    def getGraphConnections(self, graph_id, endpoint_name):
        #graph_id = self._getGraphID(service_graph_id)
        endpoints = self.getEndpoints(graph_id)
        connections = []
        for endpoint in endpoints:
            if endpoint.name == endpoint_name:
                connections = connections + self.checkConnection(endpoint.id)
        return connections
    
    def checkConnection(self, endpoint_id, endpoint_type='internal'):
        session = get_session() 
        connections = []
        connections = connections+session.query(GraphConnectionModel).filter_by(endpoint_id_2 = endpoint_id).filter_by(endpoint_id_2_type = endpoint_type).all()
        connections = connections+session.query(GraphConnectionModel).filter_by(endpoint_id_1 = endpoint_id).filter_by(endpoint_id_1_type = endpoint_type).all()
        return connections

    def getNodeID(self, graph_id):
        session = get_session()
        return session.query(GraphModel.node_id).filter_by(id = graph_id).one().node_id

    def setNodeID(self, graph_id, node_id):
        session = get_session()
        with session.begin():
            logging.debug(session.query(GraphModel).filter_by(id = graph_id).update({"node_id":node_id}))
    
    def updateEndpointType(self, graph_endpoint_id, graph_id, endpoint_type):
        session = get_session()  
        with session.begin():
            session.query(EndpointModel).filter_by(graph_id = graph_id).filter_by(graph_endpoint_id = graph_endpoint_id).update({"type": endpoint_type})

    def addGraphConnection(self, endpoint_id_1, endpoint_id_2, endpoint_id_1_type, endpoint_id_2_type):
        session = get_session()  
        with session.begin():
            graph_connection_ref = GraphConnectionModel(endpoint_id_1=endpoint_id_1, endpoint_id_2=endpoint_id_2, endpoint_id_1_type=endpoint_id_1_type, endpoint_id_2_type=endpoint_id_2_type)
            session.add(graph_connection_ref)

    def addPort(self, graph_port_id, graph_id, name=None, vnf_id=None, location=None,_type=None,
                virtual_switch=None, status=None, creation_date=datetime.datetime.now(),
                last_update=datetime.datetime.now(), os_network_id=None, mac_address=None,
                ipv4_address=None, vlan_id=None, gre_key=None, internal_id=None):
        session = get_session()  
        with session.begin():
            _id = self._get_higher_port_id() + 1
            port_ref = PortModel(id=_id, internal_id=internal_id, graph_port_id=graph_port_id,
                                 graph_id=graph_id, name=name, vnf_id=vnf_id, location=location,
                                 type=_type, virtual_switch=virtual_switch, status=status,
                                 creation_date=creation_date, last_update=last_update,
                                 os_network_id=os_network_id, mac_address=mac_address,
                                 ipv4_address=ipv4_address, vlan_id=vlan_id, gre_key=gre_key)
            session.add(port_ref)
        return _id
    
    def addVNF(self, graph_vnf_id, graph_id, name, vnf_template_location, status):
        session = get_session()  
        with session.begin():
            _id = self._get_higher_vnf_id() + 1
            vnf_ref = VNFInstanceModel(id=_id, graph_vnf_id = graph_vnf_id,
                graph_id=graph_id, name=name, template_location=vnf_template_location,
                creation_date=datetime.datetime.now(), last_update=datetime.datetime.now(),
                status=status)
            session.add(vnf_ref)
        return _id 

    def addEndPoint(self, graph_endpoint_id, graph_id, name=None, _type=None, location=None, internal_id=None):
        session = get_session()  
        with session.begin():
            _id = self._get_higher_endpoint_id() + 1
            endpoint_ref = EndpointModel(id=_id,
                                          internal_id=internal_id,
                                          graph_endpoint_id=graph_endpoint_id,
                                          graph_id=graph_id,
                                          name=name,
                                          type=_type,
                                          location=location)
            session.add(endpoint_ref)
        return _id 
    def addEndpointResource(self, endpoint_id, endpoint_type, port_id):
        session = get_session()  
        with session.begin():
            if endpoint_type is not None and "interface" in endpoint_type:

                endpoint_resource_ref = EndpointResourceModel(endpoint_id=endpoint_id,
                                                              resource_type='port',
                                                              resource_id=port_id)
                session.add(endpoint_resource_ref)
                    
    def getEndpoints(self, graph_id):
        session = get_session()  
        return session.query(EndpointModel).filter_by(graph_id = graph_id).all()
    
    def getEndPointsFromName(self, graph_id, name):
        session = get_session()  
        return session.query(EndpointModel).filter_by(graph_id = graph_id).filter_by(name = name).all()
    
    def setEndpointLocation(self, graph_id, graph_endpoint_id, location):
        session = get_session()
        with session.begin():
            assert (session.query(EndpointModel).filter_by(graph_id = graph_id).filter_by(graph_endpoint_id = graph_endpoint_id).update({"location": location}) == 1)

    def get_instantiated_nffg(self, user_id):
        session_id = self.user_session.get_active_user_session(user_id)
        nffg = self.get_nffg(session_id.id)    
        return nffg
    
    def deleteNetwork(self, network_id):
        session = get_session()
        with session.begin():
            session.query(OpenstackNetworkModel).filter_by(id = network_id).delete()
    
    def deleteVNFNetworks(self, graph_id, vnf_id):
        #TODO: check if it is the only VNF using that ports before deleting       
        session = get_session()
        ports = session.query(PortModel).filter_by(graph_id = graph_id).filter_by(vnf_id = vnf_id).all()
        for port in ports:
            with session.begin():
                session.query(OpenstackNetworkModel).filter_by(id = port.os_network_id).delete()
    
    def deleteSubnet(self, os_network_id):
        session = get_session()
        with session.begin():
            session.query(OpenstackSubnetModel).filter_by(os_network_id = os_network_id).delete()
    
    def deleteVNF(self, graph_vnf_id, graph_id):
        session = get_session()
        with session.begin():
            session.query(VNFInstanceModel).filter_by(graph_id = graph_id).filter_by(graph_vnf_id = graph_vnf_id).delete()

    def deletePort(self, port_id, graph_id, vnf_id=None):
        session = get_session()
        with session.begin():
            if vnf_id is None:
                session.query(PortModel).filter_by(graph_id = graph_id).filter_by(id = port_id).delete()
            else:
                session.query(PortModel).filter_by(graph_id = graph_id).filter_by(vnf_id = vnf_id).delete()
    
    def deleteFlowRuleFromVNF(self, vnf_id):
        session = get_session()
        with session.begin():
            ports_ref = session.query(PortModel.id).filter_by(vnf_id = vnf_id)
            for port_ref in ports_ref:
                flow_rules_ref = session.query(FlowRuleModel.id).\
                    filter(FlowRuleModel.id == ActionModel.flow_rule_id).\
                    filter(FlowRuleModel.id == MatchModel.flow_rule_id).\
                    filter(MatchModel.port_in == port_ref.id).\
                    filter(MatchModel.port_in_type == 'port').all()
                for flow_rule_ref in flow_rules_ref:
                    session.query(FlowRuleModel).filter_by(id = flow_rule_ref.id).delete()
                    session.query(MatchModel).filter_by(flow_rule_id = flow_rule_ref.id).delete()
                    session.query(ActionModel).filter_by(flow_rule_id = flow_rule_ref.id).delete()
    
    def deleteFlowspecFromPort(self, port_id):
        session = get_session()
        with session.begin():
            flow_rules_ref = session.query(FlowRuleModel.id).\
                filter(FlowRuleModel.id == ActionModel.flow_rule_id).\
                filter(FlowRuleModel.id == MatchModel.flow_rule_id).\
                filter(MatchModel.port_in == port_id).\
                filter(MatchModel.port_in_type == 'port').all()
            for flow_rule_ref in flow_rules_ref:
                session.query(FlowRuleModel).filter_by(id = flow_rule_ref.id).delete()
                session.query(MatchModel).filter_by(flow_rule_id = flow_rule_ref.id).delete()
                session.query(ActionModel).filter_by(flow_rule_id = flow_rule_ref.id).delete()
    
    def deleteFlowRule(self, flow_rule_id):
        session = get_session()
        with session.begin():
            session.query(FlowRuleModel).filter_by(id = flow_rule_id).delete()
            session.query(MatchModel).filter_by(flow_rule_id = flow_rule_id).delete()
            session.query(ActionModel).filter_by(flow_rule_id = flow_rule_id).delete()
            
    def deleteActions(self, flow_rule_id):
        session = get_session()
        with session.begin():
            session.query(ActionModel).filter_by(flow_rule_id = flow_rule_id).delete()
    
    def deleteEndpoint(self, graph_endpoint_id, graph_id):
        session = get_session()
        with session.begin():
            session.query(EndpointModel).filter_by(graph_id = graph_id).filter_by(graph_endpoint_id = graph_endpoint_id).delete()
    
    def deleteEndpointResource(self, endpoint_id):
        session = get_session()
        with session.begin():
            session.query(EndpointResourceModel).filter_by(endpoint_id = endpoint_id).delete()
            
    def deleteEndpointResourceAndResources(self, endpoint_id):
        session = get_session()
        with session.begin():
            end_point_resources_ref = session.query(EndpointResourceModel).filter_by(endpoint_id = endpoint_id).all()
            for end_point_resource_ref in end_point_resources_ref:
                if end_point_resource_ref.resource_type == 'port':
                    session.query(PortModel).filter_by(id = end_point_resource_ref.resource_id).delete()
                elif end_point_resource_ref.resource_type == 'flowrule':
                    session.query(FlowRuleModel).filter_by(id = end_point_resource_ref.resource_id).delete()
                    session.query(MatchModel).filter_by(flow_rule_id = end_point_resource_ref.resource_id).delete()
                    session.query(ActionModel).filter_by(flow_rule_id = end_point_resource_ref.resource_id).delete()    
            session.query(EndpointResourceModel).filter_by(endpoint_id = endpoint_id).delete()
            
    def getEndpointResource(self, endpoint_id, resource_type=None):
        session = get_session()
        resources=[]
        with session.begin():
            if resource_type is None:
                end_point_resources_ref = session.query(EndpointResourceModel).filter_by(endpoint_id = endpoint_id).all()
            else:
                end_point_resources_ref = session.query(EndpointResourceModel).filter_by(endpoint_id = endpoint_id).filter_by(resource_type = resource_type).all()
            for end_point_resource_ref in end_point_resources_ref:
                if end_point_resource_ref.resource_type == 'port':
                    port_ref = session.query(PortModel).filter_by(id = end_point_resource_ref.resource_id).one()
                    port = Port(_id=port_ref.graph_port_id, name=port_ref.name, _type=port_ref.type,
                      db_id=port_ref.id, internal_id=port_ref.internal_id)
                    resources.append(port)
                elif end_point_resource_ref.resource_type == 'flowrule':
                    flow_rule_ref = session.query(FlowRuleModel).filter_by(id = end_point_resource_ref.resource_id).one()
                    flow_rule = FlowRule(_id=flow_rule_ref.graph_flow_rule_id, priority=int(flow_rule_ref.priority),
                      db_id=flow_rule_ref.id, internal_id=flow_rule_ref.internal_id, node_id=flow_rule_ref.node_id, _type=flow_rule_ref.type, status=flow_rule_ref.status)
                    resources.append(flow_rule)
                #TODO: actions and match not considered
            return resources
                        
    def deleteGraphConnection(self, endpoint_id_2, endpoint_id_2_type='internal', endpoint_id_1=None):
        session = get_session()
        with session.begin():
            if endpoint_id_1 is None:
                session.query(GraphConnectionModel).filter_by(endpoint_id_2 = endpoint_id_2).filter_by(endpoint_id_2_type = endpoint_id_2_type).delete()
            else:
                #other parameters are ignored
                session.query(GraphConnectionModel).filter_by(endpoint_id_1 = endpoint_id_1).delete()

    
    def getPortFromInternalID(self, internal_id, graph_id):
        session = get_session()  
        try:
            return session.query(PortModel).filter_by(internal_id=internal_id).filter_by(graph_id=graph_id).one()
        except Exception as ex:
            logging.error(ex)
            raise PortNotFound("Port Not Found for internal ID: "+str(internal_id))
    
    def getVNFFromInternalID(self, internal_id):
        session = get_session()  
        try:
            return session.query(VNFInstanceModel).filter_by(internal_id=internal_id).one()
        except Exception as ex:
            logging.error(ex)
            raise PortNotFound("Port Not Found for internal ID: "+str(internal_id))
    
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
            raise EndpointNotFound("Endpoint not found - id: "+str(endpoint_id))
    
    def _getEndpointID(self, graph_endpoint_id, graph_id):
        session = get_session()  
        try:
            return session.query(EndpointModel).filter_by(graph_endpoint_id=graph_endpoint_id).filter_by(graph_id=graph_id).one().id
        except Exception as ex:
            logging.error(ex)
            raise EndpointNotFound("Endpoint not found - graph_endpoint_id: "+str(graph_endpoint_id)+" - graph_id: "+str(graph_id))
