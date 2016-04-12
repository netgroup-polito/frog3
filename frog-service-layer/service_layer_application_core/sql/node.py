'''
Created on Jun 20, 2015

@author: fabiomignini
'''

from sqlalchemy import Column, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
import logging
from service_layer_application_core.exception import NodeNotFound, UserLocationNotFound
from service_layer_application_core.sql.sql_server import get_session

Base = declarative_base()

class NodeModel(Base):
    '''
    Maps the database table node
    '''
    __tablename__ = 'node'
    attributes = ['id', 'name', 'domain_id']
    id = Column(VARCHAR(64), primary_key=True)
    name = Column(VARCHAR(64))
    domain_id = Column(VARCHAR(64))

class UserLocationModel(Base):
    '''
    Maps the database table node (used only by the Service layer)
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
    
    def getNodeDomainID(self, node_id):
        session = get_session()
        try:
            return session.query(NodeModel.domain_id).filter_by(id = node_id).one().domain_id
        except Exception as ex:
            logging.error(ex)
            raise NodeNotFound("Node not found: "+str(node_id))
        
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