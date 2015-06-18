'''
Created on 20/apr/2015

@author: vida
'''
from sqlalchemy import Column, VARCHAR
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from Common.config import Configuration
from sqlalchemy.types import Integer

Base = declarative_base()
sqlserver = Configuration().CONNECTION

def create_session():
    engine = sqlalchemy.create_engine(sqlserver) # connect to server
    session = sessionmaker()
    session.configure(bind=engine)
    return session

def get_session():
    return create_session()

class Flow(Base):
    '''
    Maps the database table flow
    
    id VARCHAR(64), switch_id VARCHAR(64), flowtype VARCHAR(64), user VARCHAR(64)
    '''
    __tablename__ = 'flow'
    attributes = ['id', 'switch_id', 'flowtype', 'user', 'users_count']
    id = Column(VARCHAR(64), primary_key=True)
    switch_id = Column(VARCHAR(64), primary_key=True)
    flowtype = Column(VARCHAR(64))
    user = Column(VARCHAR(64))
    users_count = Column(Integer)
    
def flow_already_exists(flow_id, flow_switch):
    session = get_session()
    s = session()
    flow = s.query(Flow).filter_by(id = flow_id).filter_by(switch_id = flow_switch).first()
    if flow is None:
        return False
    else:
        return True

def get_user_flows(user_mac):
    session = get_session()
    s = session()
    flow_tuples = s.query(Flow).filter_by(flowtype = "edge").filter_by(user = user_mac).all()
    return flow_tuples

def get_internal_link_flows(vlan):
    session = get_session()
    s = session()
    flow_tuples = s.query(Flow).filter_by(flowtype = "internal").filter_by(user = vlan).all()
    return flow_tuples

def get_edge_link_flows(mac_addr):
    session = get_session()
    s = session()
    flow_tuples = s.query(Flow).filter_by(flowtype = "edge").filter_by(user = mac_addr).all()
    return flow_tuples

def get_internal_flows():
    session = get_session()
    s = session()
    flow_tuples = s.query(Flow).filter_by(flowtype = "internal").all()
    return flow_tuples

def get_edge_flows():
    session = get_session()
    s = session()
    flow_tuples = s.query(Flow).filter_by(flowtype = "edge").all()
    return flow_tuples

def add_flow(flow_id, flow_switch, flow_type, flow_user, users_count = 1):
    session = get_session()
    s = session()
    flow_tuple = s.query(Flow).filter_by(id = flow_id).filter_by(switch_id = flow_switch).first()
    flow_id = Flow(id = flow_id, switch_id = flow_switch, flowtype = flow_type, user = flow_user, users_count = users_count)
    if flow_tuple is None:
        s.add(flow_id)
        s.commit()

def remove_flow(flow_id, flow_switch):
    session = get_session()
    s = session()
    s.query(Flow).filter_by(id = flow_id).filter_by(switch_id = flow_switch).delete(synchronize_session = False)
    s.commit()

def update_flow(flow_id, flow_switch, flow_type, flow_user, users_count):
    session = get_session()
    s = session()
    flow = s.query(Flow).filter_by(id = flow_id).filter_by(switch_id = flow_switch).first()
    if flow is not None:
        s.query(Flow).filter_by(id = flow_id).filter_by(switch_id = flow_switch).update({"user" : flow_user},
                                                                                    {"users_count" : users_count},
                                                                                    synchronize_session = False)
    else:
        raise
    s.commit()