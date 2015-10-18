'''
Created on Oct 1, 2014

@author: fabiomignini
'''
from sqlalchemy import Column, DateTime, func, VARCHAR, Text, not_, desc
from openstack_dashboard.dashboards.admin.forwarding_graph.SQL.sql import get_session
from sqlalchemy.ext.declarative import declarative_base


import datetime
import logging

Base = declarative_base()

class SessionModel(Base):
    '''
    Maps the database table session
    '''
    __tablename__ = 'session'
    attributes = ['id', 'user_id', 'service_graph_id', 'service_graph_name', 'ingress_node','egress_node','status','started_at',
                  'last_update','error','ended']
    id = Column(VARCHAR(64), primary_key=True)
    user_id = Column(VARCHAR(64))
    service_graph_id = Column(Text)
    service_graph_name = Column(Text)
    ingress_node = Column(Text)
    egress_node = Column(Text)
    status = Column(Text)
    started_at = Column(Text)
    last_update = Column(DateTime, default=func.now())
    error = Column(Text)
    ended = Column(DateTime)
    
 
class UserDeviceModel(Base):
    '''
    Maps the database table user_device
    '''
    __tablename__ = 'user_device'
    attributes = ['session_id', 'mac_address']
    session_id = Column(VARCHAR(64), primary_key=True)
    mac_address = Column(VARCHAR(64), primary_key=True)

class Session(object):
    def __init__(self):
        pass
    
    def get_service_graph_info(self,session_id):
        session = get_session()
        return session.query(SessionModel.service_graph_id, SessionModel.service_graph_name).filter_by(id = session_id).one()
     
    
    def get_active_user_session_by_nf_fg_id(self, service_graph_id, error_aware=True):
        session = get_session()
        if error_aware:
            session_ref = session.query(SessionModel).filter_by(service_graph_id = service_graph_id).filter_by(ended = None).filter_by(error = None).first()
        else:
            session_ref = session.query(SessionModel).filter_by(service_graph_id = service_graph_id).filter_by(ended = None).order_by(desc(SessionModel.started_at)).first()
        if session_ref is None:
            raise Exception("Session Not Found, for servce graph id: "+str(service_graph_id))
        return session_ref     
    
    def get_active_user_session(self):
        '''
        returns all the active nffg instatiated
        '''
        session = get_session()
        session_refs = session.query(SessionModel).filter_by(ended = None).filter_by(error = None).all()
        return session_refs
 