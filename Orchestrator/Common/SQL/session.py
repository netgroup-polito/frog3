'''
Created on Oct 1, 2014

@author: fabiomignini
'''
from sqlalchemy import Column, DateTime, func, VARCHAR, Text, not_
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import datetime
import json
import logging


from Common.config import Configuration

from Common.exception import sessionNotFound





Base = declarative_base()
sqlserver = Configuration().CONNECTION

class Session(Base):
    '''
    Maps the database table session
    
    id VARCHAR(64), user_id VARCHAR(64), session_info Text, infrastructure Text, started DATETIME, ended DATETIME
    '''
    __tablename__ = 'session'
    attributes = ['id', 'user_id', 'mac_address','session_info','profile','infrastructure',
                  'ingress_node','egress_node','started','last_update','error','ended']
    id = Column(VARCHAR(64), primary_key=True)
    user_id = Column(VARCHAR(64))
    mac_address = Column(Text)
    session_info = Column(Text)
    profile = Column(Text)
    infrastructure = Column(Text)
    ingress_node = Column(Text)
    egress_node = Column(Text)
    started = Column(DateTime)
    last_update = Column(DateTime, default=func.now())
    error = Column(DateTime)
    ended = Column(DateTime)
    
class Profile(Base):
    __tablename__ = 'profile'
    attributes = ['id', 'profile']
    id = Column(VARCHAR(64), primary_key=True)
    profile = Column(Text)
    
def checkEgressNode(node, profile):
    """
    Return False if the only ingress point in the node
    is that that we are deleting
    """
    session = get_session()
    s = session()
    egs = s.query(Session).filter_by(egress_node = node).filter(not_(Session.profile.contains(profile))).all()
    if egs is not None and len(egs) == 0:
        return False
    return True 

def checkIngressNode(node, profile):
    """
    Return False if the only ingress point in the node
    is that that we are deleting
    """
    session = get_session()
    s = session()
    ings = s.query(Session).filter_by(ingress_node = node).filter(not_(Session.profile.contains(profile))).all()
    if ings is not None and len(ings) == 0:
        return False
    return True 

def get_instantiated_profile(user_id):
    profile_id = get_profile_id_from_active_user_session(user_id)
    profile = get_profile(profile_id)    
    return profile

def get_profile_by_id(profile_id):
    profile = get_profile(profile_id)    
    return profile

def get_profile(graph_id):
    session = get_session()
    s = session()
    dt = s.query(Profile.profile).filter_by(id = graph_id).first()
    return dt[0]

def del_mac_address_in_the_session(mac_address, session_id):
    session = get_session()
    s = session()
    #mettere un order by
    dt = s.query(Session).filter_by(id = session_id).filter_by(ended = None).filter_by(error = None).first()
    if dt is not None:
        if dt.mac_address is not None:
            devices = json.loads(dt.mac_address)
            devices.remove(mac_address)
        else:
            raise sessionNotFound("Session Not Found")
        logging.info("devices deleted from db: \n"+str(mac_address))
        logging.info("devices that are still in db: \n"+str(devices))
        s.query(Session).filter_by(id = session_id).filter_by(ended = None).filter_by(error = None).update({"mac_address":json.dumps(devices)})
        s.commit()
    else:
        raise sessionNotFound("Session Not Found")
    
def add_mac_address_in_the_session(mac_address, session_id):
    session = get_session()
    s = session()
    #mettere un order by
    dt = s.query(Session).filter_by(id = session_id).filter_by(ended = None).filter_by(error = None).first()
    if dt is not None:
        if dt.mac_address is not None:
            devices = json.loads(dt.mac_address)
            devices.append(mac_address)
        else:
            devices = []
            devices.append(mac_address)
        logging.info("devices: \n"+str(devices))
        s.query(Session).filter_by(id = session_id).filter_by(ended = None).filter_by(error = None).update({"mac_address":json.dumps(devices)})
        s.commit()
    else:
        raise sessionNotFound("Session Not Found")
    
def update_session(nf_fg_id, profile, infrastructure):
    session = get_session()  
    s = session()
    dt_profile = s.query(Profile).filter_by(id = nf_fg_id).first()
    if dt_profile is not None:
        s.query(Profile).filter_by(id = nf_fg_id).update({"profile":profile}, synchronize_session = False)
    else:
        profile_id = Profile(id=nf_fg_id, profile=profile)
        s.add(profile_id)
    dt_session = s.query(Session).filter_by(profile = nf_fg_id).filter_by(ended = None).filter_by(error = None).first()
    if dt_session is not None:
        s.query(Session).filter_by(profile = nf_fg_id).filter_by(ended = None).filter_by(error = None).update({"last_update":datetime.datetime.now()})
    else:
        raise sessionNotFound("Session Not Found")
    s.commit()
    return dt_session.id

def add_session(session_id, user_id, nf_fg_id, profile, infrastructure, ingress_node, egress_node, user_mac = None, session_info = None):
    '''
    store the session in db
    '''

    # If isn't an update of NF-FG for another user device 
    session = get_session()  
    s = session()
    dt_profile = s.query(Profile).filter_by(id = nf_fg_id).first()
    if dt_profile is not None:
        s.query(Profile).filter_by(id = nf_fg_id).update({"profile":profile}, synchronize_session = False)
    else:
        profile_id = Profile(id=nf_fg_id, profile=profile)
        s.add(profile_id)
    session_id = Session(id=session_id, user_id = user_id, mac_address=user_mac, session_info = session_info,
                          profile=nf_fg_id, infrastructure = infrastructure, ingress_node = ingress_node,
                           egress_node = egress_node, started = datetime.datetime.now())
    
    
    
    s.add(session_id)
    s.commit()  

def updateProfile(profile_id, profile):     
    session = get_session()
    s = session()
    s.query(Profile).filter_by(id=profile_id).update({"profile":profile}, synchronize_session = False)
    s.commit() 
    
def get_active_user_devices(user_id):
    session = get_session()
    s = session()
    mac_address = s.query(Session.mac_address).filter_by(user_id = user_id).filter_by(ended = None).filter_by(error = None).first()
    if mac_address is not None:
        return mac_address[0]
    else:
        return None
   
def get_profile_id_from_active_user_session(user_id):
    session = get_session()
    s = session()
    dt = s.query(Session.profile).filter_by(user_id = user_id).filter_by(ended = None).filter_by(error = None).first()
    
    if dt is None:
        raise sessionNotFound("Session Not Found")
    return dt[0]

def get_active_user_session_by_nf_fg_id(graph_id):
    session = get_session()
    s = session()
    dt = s.query(Session).filter_by(profile = graph_id).filter_by(ended = None).filter_by(error = None).first()
    if dt is None:
        raise sessionNotFound("Session Not Found")
    return dt

def get_active_user_session(user_id):
    '''
    returns if exists an active session of the user
    '''
    session = get_session()
    s = session()
    dt = s.query(Session).filter_by(user_id = user_id).filter_by(ended = None).filter_by(error = None).first()
    if dt is None:
        raise sessionNotFound("Session Not Found")
    return dt
    
def get_active_user_device_session(user_id, mac_address = None):
    '''
    returns if exists an active session of the user connected on the port of the switch passed
    '''
    session = get_session()
    s = session()
    user_sessions = s.query(Session).filter_by(user_id = user_id).filter_by(ended = None).filter_by(error = None).all()

    logging.debug("MAC address:"+str(mac_address))
    for user_session in user_sessions:
        if mac_address is not None:
            if user_session.mac_address is not None:
                for mac in json.loads(user_session.mac_address):
                    if mac == mac_address:
                        return len(json.loads(user_session.
                            mac_address)), user_session
        elif mac_address is None:
            return 1, user_session

    raise sessionNotFound("Session Not Found")


def get_active_user_session_from_id(session_id):
    session = get_session()
    s = session() 
    
    user_session = s.query(Session).filter_by(id=session_id).filter_by(ended = None).filter_by(error = None).first()
    if not user_session:
        logging.debug("Query - no results")
        raise sessionNotFound("Session Not Found") 
    s.commit()
    return user_session

def get_active_user_session_info_from_id(session_id):
    session = get_session()
    s = session() 
    
    user_session = s.query(Session).filter_by(id=session_id).filter_by(ended = None).filter_by(error = None).first()
    if not user_session:
        logging.debug("Query - no results")
        raise sessionNotFound("Session Not Found")
    infrastructure = user_session.infrastructure
    profile = user_session.profile 
    s.commit()
    return infrastructure, profile
    
def set_ended(session_id):
    session = get_session()
    s = session() 
    
    s.query(Session).filter_by(id=session_id).update({"ended":datetime.datetime.now()}, synchronize_session = False)
    s.commit()
    
def set_error(user_id):
    session = get_session()
    s = session() 
    logging.debug("Session - set_error - user_id: "+str(user_id))
    query  = s.query(Session).filter_by(user_id=user_id).filter_by(ended = None).filter_by(error = None)
    logging.debug("Session - set_error - query: "+str(query))
    res = s.query(Session).filter_by(user_id=user_id).filter_by(ended = None).filter_by(error = None).update({"error":datetime.datetime.now()}, synchronize_session = False)
    logging.debug("Session - set_error - update result: "+str(res))
    s.commit()

def checkDeviceSession(user_id, mac_address):
    '''
    return true if there is already an active session of the user with this mac
    '''
    session = get_session()
    s = session()
    user_sessions =s.query(Session).filter_by(user_id = user_id).filter_by(ended = None).filter_by(error = None).all()
    for user_session in user_sessions:
        if user_session.mac_address is not None:
            for mac in json.loads(user_session.mac_address):
                if mac == mac_address:
                    return True
    return False
    
def checkSession(user_id, token, profile = None):
    '''
    return true if there is already an active session of the user
    '''
    session = get_session()
    s = session()
    if profile is None:
        user_session = s.query(Session).filter_by(user_id = user_id).filter_by(ended = None).filter_by(error = None).first()
    else:
        user_session = s.query(Session).filter_by(user_id = user_id).filter_by(profile = profile).filter_by(ended = None).filter_by(error = None).first()
    
    if user_session is None:
        res = False
    else:
        res = True
    return res, user_session
     
def create_session():
    engine = sqlalchemy.create_engine(sqlserver) # connect to server
    session = sessionmaker()
    session.configure(bind=engine)
    return session

def get_session():
    return create_session()
