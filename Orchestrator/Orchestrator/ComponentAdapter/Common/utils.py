'''
Created on Jul 24, 2015

@author: fabiomignini
'''
import random
from sqlalchemy.orm.exc import NoResultFound
from Common.SQL.graph import Graph

def getMacAddress(port):
    while True:
        mac_address = _generateMacAddress()
        if _check_unique_mac(mac_address) is True:
            # save the mac_address in the DB port table
            Graph().setPortMacAddress(port.db_id, mac_address)
            break
    return mac_address

def _generateMacAddress():
    mac = [0xfa, 0x16, 0x3e, random.randint(0x00, 0xff),
           random.randint(0x00, 0xff), random.randint(0x00, 0xff)]
    return ':'.join(["%02x" % x for x in mac])

def _check_unique_mac(mac_address):
    try:
        Graph().checkMacAddress(mac_address)
    except  NoResultFound:
        return True
    return False
    