'''
Created on May 21, 2015

@author: vida
'''
from sqlalchemy import Column, VARCHAR
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

class Resource(Base):
    '''
    Maps the database table resource
    
    id VARCHAR(64), profile_id VARCHAR(64), resource_type VARCHAR(64), name VARCHAR(64)
    '''
    __tablename__ = 'resource'
    attributes = ['id', 'profile_id', 'resource_type', 'name']
    id = Column(VARCHAR(64), primary_key=True)
    profile_id = Column(VARCHAR(64))
    resource_type = Column(VARCHAR(64))
    name = Column(VARCHAR(64))
    
def add_resource(res_id, profile_id, res_type, res_name):
    session = get_session()
    s = session()
    res_tuples = s.query(Resource).filter_by(id = res_id).first()
    if res_tuples is None:
        res_id = Resource(id = res_id, profile_id = profile_id, resource_type = res_type, name = res_name)
        s.add(res_id)
        s.commit()
    
def get_profile_resources(profile_id):
    session = get_session()
    s = session()
    res_tuples = s.query(Resource).filter_by(profile_id = profile_id).all()
    return res_tuples

def remove_resource(res_id):
    session = get_session()
    s = session()
    s.query(Resource).filter_by(id = res_id).delete(synchronize_session = False)
    s.commit()
