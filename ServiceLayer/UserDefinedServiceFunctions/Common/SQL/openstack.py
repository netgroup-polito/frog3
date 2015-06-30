'''
Created on Jun 20, 2015

@author: fabiomignini
'''

from sqlalchemy import Column, VARCHAR, Boolean
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from Common.config import Configuration



Base = declarative_base()
sqlserver = Configuration().CONNECTION

def create_session():
    engine = sqlalchemy.create_engine(sqlserver) # connect to server
    session = sessionmaker()
    session.configure(bind=engine)
    return session

def get_session():
    return create_session()

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
    

class OpenstackNetwork(object):
    def __init__(self):
        pass
    
class OpenstackSubnetModel(Base):
    '''
    Maps the database table node
    '''
    __tablename__ = 'openstack_subnet'
    attributes = ['id', 'name', 'os_neutron_id']
    id = Column(VARCHAR(64), primary_key=True)
    name = Column(VARCHAR(64))
    os_network_id = Column(VARCHAR(64))
    

class OpenstackSubnet(object):
    def __init__(self):
        pass
