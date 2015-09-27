'''
Created on Jun 20, 2015

@author: fabiomignini
'''

from sqlalchemy import Column, VARCHAR, Boolean
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import logging
from Common.config import Configuration
from Common.exception import NodeNotFound, ControllerNotFound, UserLocationNotFound
from Common.SQL.sql import get_session

Base = declarative_base()

class NodeModel(Base):
    '''
    Maps the database table node
    '''
    __tablename__ = 'node'
    attributes = ['id', 'name', 'type','domain_id','availability_zone','openstack_controller', 'openflow_controller']
    id = Column(VARCHAR(64), primary_key=True)
    name = Column(VARCHAR(64))
    
    '''
    This field is used to specify what kind of component adapter should be used.
    It can assume the following values:
        HeatCA             # for the FROG component adapter
        OpenStack_compute  # this value doesn't correspond to a component_adapter
                           # in this type of nodes is not possible to directly
                           # instantiate a VNF
        JolnetCA           # for the Jolnet component adapter
        UnifiedNode        # for the Universal node component adapter 
    '''
    type = Column(VARCHAR(64))
    domain_id = Column(VARCHAR(64))
    availability_zone = Column(VARCHAR(64))
    
    '''
    This specifies the endpoint for Keystone authentication on the controller (es: http://1.1.1.1:35357)
    '''
    openstack_controller = Column(VARCHAR(64))
    '''
    This specifies the id of the tuple in the openflow_controller table
    '''
    openflow_controller = Column(VARCHAR(64))
    
class OpenflowControllerModel(Base):
    '''
    Maps the database table openflow_controller
    '''
    __tablename__ = 'openflow_controller'
    attributes = ['id', 'endpoint', 'version', 'username', 'password']
    id = Column(VARCHAR(64), primary_key=True)
    
    '''
    This specifies the endpoint for REST APIs on the openflow controller (es: http://2.2.2.2:8181)
    '''
    endpoint = Column(VARCHAR(64))
    version = Column(VARCHAR(64))
    username = Column(VARCHAR(64))
    password = Column(VARCHAR(64))
    
class UserLocationModel(Base):
    '''
    Maps the database table node
    '''
    __tablename__ = 'user_location'
    attributes = ['user_id', 'node_id']
    user_id = Column(VARCHAR(64), primary_key=True)
    node_id = Column(VARCHAR(64))

class Node(object):
    def __init__(self):
        pass
    
    def getNode(self, node_id):
        session = get_session()
        try:
            return session.query(NodeModel).filter_by(id = node_id).one()
        except Exception as ex:
            logging.error(ex)
            raise NodeNotFound("Node not found: "+str(node_id))
    
        
    def getNodeID(self, user_id):
        '''
        This method should returns the ingress and egress node for a specific user
        '''
        pass
    
    def getInstantiationNode(self):
        session = get_session()
        try:
            return session.query(NodeModel).filter(NodeModel.type != 'HeatCA' ).one()
        except Exception as ex:
            logging.error(ex)
            raise NodeNotFound("Node not found.")
    
    def getNodeFromDomainID(self, domain_id):
        session = get_session()
        try:
            return session.query(NodeModel).filter_by(domain_id = domain_id).one()
        except Exception as ex:
            logging.error(ex)
            raise NodeNotFound("Node not found for domain id: "+str(domain_id))
    
    def getAvailabilityZone(self, node_id):
        session = get_session()
        try:
            return session.query(NodeModel.availability_zone).filter_by(id = node_id).one().availability_zone
        except Exception as ex:
            logging.error(ex)
            raise NodeNotFound("Node not found: "+str(node_id))
    
    def getNodeDomainID(self, node_id):
        session = get_session()
        try:
            return session.query(NodeModel.domain_id).filter_by(id = node_id).one().domain_id
        except Exception as ex:
            logging.error(ex)
            raise NodeNotFound("Node not found: "+str(node_id))
    
    def getComponentAdapter(self, node_id):
        session = get_session()
        logging.debug("node_id: "+str(node_id))
        try:
            return session.query(NodeModel.type).filter_by(id = node_id).one().type
        except Exception as ex:
            logging.error(ex)
            raise NodeNotFound("Node not found")
        
    def getOpenstackControllerURL(self, node_id):
        session = get_session()
        try:
            return session.query(NodeModel.openstack_controller).filter_by(id = node_id).one().openstack_controller
        except Exception as ex:
            logging.error(ex)
            raise NodeNotFound("Node not found: "+str(node_id))
    
    def getOpenflowControllerID(self, node_id):
        session = get_session()
        try:
            return session.query(NodeModel.openflow_controller).filter_by(id = node_id).one().openflow_controller
        except Exception as ex:
            logging.error(ex)
            raise NodeNotFound("Node not found: "+str(node_id))
        
    def getOpenflowController(self, controller_id):
        session = get_session()
        try:
            return session.query(OpenflowControllerModel.id).filter_by(id = controller_id).one()
        except Exception as ex:
            logging.error(ex)
            raise ControllerNotFound("Node not found: "+str(controller_id))
        
    def getUserLocation(self, user_id):
        '''
        Ruturns the id of the node, where the User is connected
        '''
        session = get_session()
        try:
            return session.query(UserLocationModel.node_id).filter_by(user_id = user_id).one().node_id
        except Exception as ex:
            logging.error(ex)
            raise UserLocationNotFound("It is not defined a default location for the user: "+str(user_id))