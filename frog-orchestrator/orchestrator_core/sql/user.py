'''
Created on 18 set 2015

@author: Andrea
'''

from sqlalchemy import Column, VARCHAR
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
import logging

from orchestrator_core.sql.sql_server import get_session
from orchestrator_core.exception import UserNotFound, TenantNotFound

Base = declarative_base()

class UserModel(Base):
    '''
    Maps the database table user
    '''
    __tablename__ = 'user'
    attributes = ['id', 'name', 'password', 'tenant_id', 'mail']
    id = Column(VARCHAR(64), primary_key=True)
    name = Column(VARCHAR(64))
    password = Column(VARCHAR(64))
    tenant_id = Column(VARCHAR(64))
    mail = Column(VARCHAR(64))
    
class TenantModel(Base):
    '''
    Maps the database table tenant
    '''
    __tablename__ = 'tenant'
    attributes = ['id', 'name', 'description']
    id = Column(VARCHAR(64), primary_key=True)
    name = Column(VARCHAR(64))
    description = Column(VARCHAR(128))
    

class User(object):
    
    def __init__(self):
        pass
    
    def getUser(self, username):
        session = get_session()
        try:
            return session.query(UserModel).filter_by(name = username).one()
        except Exception as ex:
            logging.error(ex)
            raise UserNotFound("User not found: "+str(username))
    
    def getUserFromID(self, user_id):
        session = get_session()
        try:
            return session.query(UserModel).filter_by(id = user_id).one()
        except Exception as ex:
            logging.error(ex)
            raise UserNotFound("User not found id: "+str(user_id))
    
    def getTenantName(self, tenant_id):
        session = get_session()
        try:
            return session.query(TenantModel).filter_by(id = tenant_id).one().name
        except Exception as ex:
            logging.error(ex)
            raise TenantNotFound("User not found: "+str(tenant_id))