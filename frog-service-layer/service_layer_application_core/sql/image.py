'''
Created on Jul 16, 2015

@author: fabiomignini
'''
from sqlalchemy import Column, VARCHAR, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import logging
from service_layer_application_core.config import Configuration
from service_layer_application_core.sql.sql_server import get_session

Base = declarative_base()

class VNFImage(Base):
    '''
    Maps the database table vnf_image
    '''
    __tablename__ = 'vnf_image'
    attributes = ['id', 'internal_id', 'template', 'configuration_model']
    id = Column(VARCHAR(255), primary_key=True)
    internal_id = Column(VARCHAR(255))
    template = Column(Text())
    configuration_model = Column(Text())

class Images(object):
    
    def getTemplate(self, image_internal_id):
        session = get_session()  
        try:
            return session.query(VNFImage).filter_by(internal_id = image_internal_id).one().template
        except Exception as ex:
            logging.error(ex)
            raise Exception("No template found for image id: "+str(image_internal_id))
        
    def getConfiguationModel(self, image_internal_id):
        session = get_session()  
        try:
            return session.query(VNFImage).filter_by(internal_id = image_internal_id).one().configuration_model
        except Exception as ex:
            logging.error(ex)
            raise Exception("No configuration model found for image id: "+str(image_internal_id))