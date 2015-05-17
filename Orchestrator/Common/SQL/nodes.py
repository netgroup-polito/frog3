'''
Created on Apr 1, 2015

@author: fabiomignini
'''

from sqlalchemy import Column, VARCHAR, Boolean
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from Common.config import Configuration
from Common.exception import NoUserNodeDefined


Base = declarative_base()
sqlserver = Configuration().CONNECTION

def create_session():
    engine = sqlalchemy.create_engine(sqlserver) # connect to server
    session = sessionmaker()
    session.configure(bind=engine)
    return session

def get_session():
    return create_session()

class Node(Base):
    '''
    Maps the database table node
    '''
    __tablename__ = 'node'
    attributes = ['node_id', 'node_name', 'ip_address', 'avaibility_zone']
    node_id = Column(VARCHAR(64), primary_key=True)
    node_name = Column(VARCHAR(64))
    ip_address = Column(VARCHAR(64))
    avaibility_zone = Column(VARCHAR(64))
    
def updateIPAddress(node_id, ip_address):
    session = get_session()
    s = session()
    s.query(Node.node_name).filter_by(node_id = node_id).update({"ip_address": ip_address}, 
                                                                 synchronize_session = False)
    s.commit()
    
def getNodeName(node_id):    
    session = get_session()
    s = session()
    node_name = s.query(Node.node_name).filter_by(node_id = node_id).first()
    s.commit()
    return node_name[0]
    
def getAvaibilityZoneByHostname(hostname):
    session = get_session()
    s = session()
    avaibility_zone = s.query(Node.avaibility_zone).filter_by(node_name = hostname).first()
    s.commit()
    return avaibility_zone[0]
    
def getAvaibilityZone(node_id):
    session = get_session()
    s = session()
    avaibility_zone = s.query(Node.avaibility_zone).filter_by(node_id = node_id).first()
    s.commit()
    return avaibility_zone[0]

def getIPAddress(node_id):
    session = get_session()
    s = session()
    ip_address = s.query(Node.ip_address).filter_by(node_id = node_id).first()
    s.commit()
    return ip_address[0]
    
def get_node_id(ip_address):
    session = get_session()
    s = session()
    node = s.query(Node.node_id).filter_by(ip_address = ip_address).first()
    s.commit()
    return node[0]
    
class UserLocation(Base):
    '''
    Maps the database table user_location
    This is a temporary table that fix a position of the user in a specific access node
    '''
    __tablename__ = 'user_location'
    attributes = ['user_id', 'node_id']
    user_id = Column(VARCHAR(64), primary_key=True)
    node_id = Column(VARCHAR(64), primary_key=True)


def getNodeID(user_id):
    session = get_session()
    s = session()
    node_id = s.query(UserLocation.node_id).filter_by(user_id = user_id).first()
    s.commit()
    try:
        node_id = node_id[0]
    except:
        raise NoUserNodeDefined('No one node is defined for user_id '+str(user_id))
        #node_id = None
    return node_id

class NodesEgressInterface(Base):
    '''
    Maps the database table nodes_egress_interface
    This is a temporary table that associate an egress port to a node
    '''
    __tablename__ = 'nodes_egress_interface'
    attributes = ['node_id', 'interface']
    node_id = Column(VARCHAR(64), primary_key=True)
    interface = Column(VARCHAR(64), primary_key=True)
    
def getEgressInterface(node_id):
    session = get_session()
    s = session()
    interface = s.query(NodesEgressInterface.interface).filter_by(node_id = node_id).first()
    s.commit()
    return interface[0]

class NodesIngressInterface(Base):
    '''
    Maps the database table nodes_ingress_interface
    This is a temporary table that associate an ingress port to a node
    '''
    __tablename__ = 'nodes_ingress_interface'
    attributes = ['node_id', 'interface']
    node_id = Column(VARCHAR(64), primary_key=True)
    interface = Column(VARCHAR(64), primary_key=True)

def getIngressInterface(node_id):
    session = get_session()
    s = session()
    interface = s.query(NodesIngressInterface.interface).filter_by(node_id = node_id).first()
    s.commit()
    return interface[0]
