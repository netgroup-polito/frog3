'''
Created on Oct 1, 2014

@author: fabiomignini
'''
'''
Created on May 31, 2014

@author: fmignini
'''
from sqlalchemy import Column, VARCHAR, Text
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from Common.exception import InfoNotFound

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

class ComponentAdapter(Base):
    '''
    Maps the database table component_adapter
    
    session_id VARCHAR(64), extra mediumtext
    '''
    __tablename__ = 'component_adapter'
    attributes = ['session_id', 'extra']
    session_id = Column(VARCHAR(64), primary_key=True)
    extra = Column(Text, primary_key=True)
    

def get_extra_info(session_id):
    session = get_session()
    s = session()
    info_tuple = s.query(ComponentAdapter.extra).filter_by(session_id = session_id).first()
    if info_tuple is not None:
        return info_tuple.extra
    else: 
        raise InfoNotFound("Component adapter info not found")
    


def set_extra_info(session_id, extra):
    session = get_session()
    s = session()
    info_tuple = ComponentAdapter(session_id=session_id, extra=extra)
    s.add(info_tuple)
    s.commit()
    
def update_extra_info(session_id, extra):
    session = get_session()
    s = session()
    s.query(ComponentAdapter).filter_by(session_id = session_id).update({"extra": extra}, synchronize_session = False)
    s.commit()
