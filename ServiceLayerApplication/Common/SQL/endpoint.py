'''
Created on Oct 1, 2014

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

class EndpointModel(Base):
    '''
    Maps the database table endpoint
    '''
    __tablename__ = 'endpoint'
    attributes = ['id', 'internal_id', 'graph_endpoint_id','session_id','graph_id','type','location']
    id = Column(VARCHAR(64), primary_key=True)
    internal_id = Column(VARCHAR(64))
    graph_endpoint_id = Column(VARCHAR(64))
    session_id = Column(VARCHAR(64))
    graph_id = Column(VARCHAR(64))
    type = Column(VARCHAR(64))
    location = Column(VARCHAR(64))
    
class Endpoint(object):
    def __init__(self):
        pass
    
class EndpointResourceModel(Base):
    '''
    Maps the database table endpoint_resource
    '''
    __tablename__ = 'endpoint_resource'
    attributes = ['endpoint_id', 'resource_type', 'resource_id']
    endpoint_id = Column(VARCHAR(64), primary_key=True)
    resource_type = Column(VARCHAR(64), primary_key=True)
    resource_id = Column(VARCHAR(64), primary_key=True)
   
class EndpointResource(object):
    def __init__(self):
        pass
    
class GraphConnectionModel(Base):
    '''
    Maps the database table graph_connection
    '''
    __tablename__ = 'graph_connection'
    attributes = ['endpoint_id_1', 'endpoint_id_2']
    endpoint_id_1 = Column(VARCHAR(64), primary_key=True)
    endpoint_id_2 = Column(VARCHAR(64), primary_key=True)
    
class GraphConnection(object):
    def __init__(self):
        pass
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
def delete_endpoint_connections(graph_id):
    # Delete connection with other graphs
    session = get_session()  
    s = session()
    s.query(Endpoint).filter_by(Graph_ID_connected = graph_id).update({"Available": True,
                                                                "Graph_ID_connected": None,
                                                                "Endpoint_ID_connected": None}, 
                                                                      synchronize_session = False)
    # Delete endpoint of the graph
    s.query(Endpoint).filter_by(Graph_ID = graph_id).delete(synchronize_session=False)
    s.commit()
    
def updateEndpointConnection(graph_id, endpoint_id, graph_id_connection, endpoint_id_connected):
    session = get_session()  
    s = session()
    dt_profile = s.query(Endpoint).filter_by(Graph_ID = graph_id).filter_by(Endpoint_ID = endpoint_id).first()
    if dt_profile is not None:
        s.query(Endpoint).filter_by(Graph_ID = graph_id).filter_by(Endpoint_ID = endpoint_id).update(
                                                                {"Graph_ID_connected": graph_id_connection,
                                                            "Endpoint_ID_connected": endpoint_id_connected},
                                                                     synchronize_session = False)
    else:
        raise
    s.commit()

def get_first_available_endpoint_by_name(graph_id, endpoint_name):
    session = get_session()
    s = session()
    endpoint_tuple = s.query(Endpoint).filter_by(Graph_ID = graph_id).filter_by(Name = endpoint_name).filter_by(Available = True).first()
    s.query(Endpoint.Endpoint_ID).filter_by(Graph_ID = graph_id).filter_by(Endpoint_ID = endpoint_tuple.Endpoint_ID).update(
                                                            {"Available": False},
                                                            synchronize_session = False)
    s.commit()
    return endpoint_tuple
    
def get_available_endpoints_by_name(graph_id, endpoint_name):
    session = get_session()
    s = session()
    endpoint_tuples = s.query(Endpoint.Endpoint_ID).filter_by(Graph_ID = graph_id).filter_by(Name = endpoint_name).all()  
    return endpoint_tuples

def get_available_endpoints_by_id(graph_id, endpoint_id):
    session = get_session()
    s = session()
    endpoint_tuples = s.query(Endpoint).filter_by(Graph_ID = graph_id).filter_by(Endpoint_ID = endpoint_id).all()  
    return endpoint_tuples

def get_endpoint_by_graph_id(graph_id):
    session = get_session()
    s = session()
    endpoint_tuples = s.query(Endpoint).filter_by(Graph_ID = graph_id).all()  
    return endpoint_tuples

def set_endpoint(graph_id, endpoint_id, available, name, generic_endpoint_id,
                  endpoint_type = None, graph_id_connected = None, endpoint_id_connected = None):
    session = get_session()
    s = session()
    endpoint_id = Endpoint(Graph_ID = graph_id, Endpoint_ID = endpoint_id,
                            Available = available, Name =name, ID = generic_endpoint_id, 
                            Type=endpoint_type, Graph_ID_connected=graph_id_connected,
                             Endpoint_ID_connected=endpoint_id_connected)
    s.add(endpoint_id)
    s.commit()

