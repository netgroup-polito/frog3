'''
Created on Oct 23, 2015

@author: fabiomignini
'''
from service_layer_application_core.sql.sql_server import get_session
from service_layer_application_core.sql.session import SessionModel

session = get_session()
session.query(SessionModel).delete()

print "Database sessions deleted"
