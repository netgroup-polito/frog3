'''
Created on Jun 22, 2015

@author: fabiomignini
'''
import sqlalchemy
from sqlalchemy.orm import sessionmaker

import ConfigParser

config = ConfigParser.ConfigParser()
config.read('/etc/openstack-dashboard/conf.cfg')
sqlserver = config.get('mysqldb', 'connection')

def create_session():
    engine = sqlalchemy.create_engine(sqlserver) # connect to server
    session = sessionmaker()
    session.configure(bind=engine,autocommit=True)
    return session()

def get_session():
    return create_session()