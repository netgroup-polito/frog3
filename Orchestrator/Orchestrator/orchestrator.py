'''
Created on Oct 1, 2014

@author: fabiomignini
'''

import falcon
import logging
import requests
import json
import jsonschema

from sqlalchemy.orm.exc import NoResultFound


from Orchestrator.controller import UpperLayerOrchestratorController
from Orchestrator.ComponentAdapter.OpenstackCommon.authentication import KeystoneAuthentication
from Common.userAuthentication import UserAuthentication
from Common.NF_FG.validator import ValidateNF_FG
from Common.exception import wrongRequest, unauthorizedRequest, sessionNotFound, ingoingFlowruleMissing, ManifestValidationError


class YANGAPI(object):
    
    '''def __init__(self, AUTH_SERVER, orch_UN,orch_PW,orch_tenant):
        self.username=orch_UN;
        self.password=orch_PW; 
        self.tenant=orch_tenant;
        self.keystone_server = AUTH_SERVER;
        try:
            self.keystoneAuth = KeystoneAuthentication(self.keystone_server, self.tenant, self.username, self.password);
        except:
            logging.exception("Orchestrator not authenticated!!")
            raise'''
    
    def __init__(self):
        pass
    
    def get(self, request, response, image_id):
        pass
    
class TemplateAPI(object):
    
    '''def __init__(self, AUTH_SERVER, orch_UN,orch_PW,orch_tenant):
        self.username=orch_UN;
        self.password=orch_PW; 
        self.tenant=orch_tenant;
        self.keystone_server = AUTH_SERVER;
        try:
            self.keystoneAuth = KeystoneAuthentication(self.keystone_server, self.tenant, self.username, self.password);
        except:
            logging.exception("Orchestrator not authenticated!!")
            raise'''
    
    def __init__(self):
        pass
    
    def get(self, request, response, image_id):
        pass

class UpperLayerOrchestrator(object):
    '''
    Admin class that intercept the REST call through the WSGI server
    '''

    '''def __init__(self, AUTH_SERVER, orch_UN,orch_PW,orch_tenant):
        self.username=orch_UN;
        self.password=orch_PW; 
        self.tenant=orch_tenant;
        self.keystone_server = AUTH_SERVER;
        try:
            self.keystoneAuth = KeystoneAuthentication(self.keystone_server, self.tenant, self.username, self.password);
        except:
            logging.exception("Orchestrator not authenticated!!")
            raise'''
        
    def __init__(self):
        pass
        
    def on_delete(self, request, response, nffg_id):
        try :
            
            user = UserAuthentication().authenticateUserFromRESTRequest(request)
                   
            controller = UpperLayerOrchestratorController(user)
            response.body = controller.delete(nffg_id)
            
        except NoResultFound:
            logging.exception("EXCEPTION - NoResultFound")
            raise falcon.HTTPNotFound()
        except requests.HTTPError as err:
            logging.exception(err.response.text)
            if err.response.status_code == 401:
                raise falcon.HTTPInternalServerError('Unauthorized.',err.message)
            elif err.response.status_code == 403:
                raise falcon.HTTPInternalServerError('Forbidden.',err.message)
            elif err.response.status_code == 404:
                raise falcon.HTTPInternalServerError('Resource Not found.',err.message)
            raise err
        except jsonschema.ValidationError as err:
            logging.exception(err.message)
            raise falcon.HTTPBadRequest('Bad Request',
                                        err.message)
        except sessionNotFound as err:
            logging.exception(err.message)
            raise falcon.HTTPNotFound()
        except ingoingFlowruleMissing as err:
            logging.exception(err.message)
            raise falcon.HTTPInternalServerError('ingoingFlowruleMissing',err.message)
        except ManifestValidationError as err:
            logging.exception(err.message)
            raise falcon.HTTPInternalServerError('ManifestValidationError',err.message)
        except Exception as ex:
            logging.exception(ex)
            raise falcon.HTTPInternalServerError('Contact the admin. ',ex.message)
    
    def on_get(self, request, response, nffg_id):
        try :
            
            user = UserAuthentication().authenticateUserFromRESTRequest(request)
                   
            controller = UpperLayerOrchestratorController(user)
            response.body = controller.get(nffg_id)
            
            response.status = falcon.HTTP_200
            
        except NoResultFound:
            logging.exception("EXCEPTION - NoResultFound")
            raise falcon.HTTPNotFound()
        except requests.HTTPError as err:
            logging.exception(err.response.text)
            if err.response.status_code == 401:
                raise falcon.HTTPInternalServerError('Unauthorized.',err.message)
            elif err.response.status_code == 403:
                raise falcon.HTTPInternalServerError('Forbidden.',err.message)
            elif err.response.status_code == 404:
                raise falcon.HTTPInternalServerError('Resource Not found.',err.message)
            raise err
        except jsonschema.ValidationError as err:
            logging.exception(err.message)
            raise falcon.HTTPBadRequest('Bad Request',
                                        err.message)
        except sessionNotFound as err:
            logging.exception(err.message)
            raise falcon.HTTPNotFound()
        except ingoingFlowruleMissing as err:
            logging.exception(err.message)
            raise falcon.HTTPInternalServerError('ingoingFlowruleMissing',err.message)
        except ManifestValidationError as err:
            logging.exception(err.message)
            raise falcon.HTTPInternalServerError('ManifestValidationError',err.message)
        except Exception as ex:
            logging.exception(ex)
            raise falcon.HTTPInternalServerError('Contact the admin. ',ex.message)
        
    def on_put(self, request, response):
        """
        Take as body request the NF-FG      
        """
        try:
            
            user = UserAuthentication().authenticateUserFromRESTRequest(request)
            
            nf_fg = json.load(request.stream, 'utf-8')
            ValidateNF_FG(nf_fg).validate()
            
            controller = UpperLayerOrchestratorController(user)
            response.body = controller.put(nf_fg)

            response.status = falcon.HTTP_202
            
        except wrongRequest as err:
            raise falcon.HTTPBadRequest("Bad Request", err.description)
        except unauthorizedRequest as err:
            raise falcon.HTTPUnauthorized("Unauthorized", err.description)
        except requests.HTTPError as err:
            logging.exception(err.response.text)
            if err.response.status_code == 401:
                raise falcon.HTTPInternalServerError('Unauthorized.',err.message)
            elif err.response.status_code == 403:
                raise falcon.HTTPInternalServerError('Forbidden.',err.message)
            elif err.response.status_code == 404: 
                raise falcon.HTTPInternalServerError('Resource Not found.',err.message)
            raise err
    
    #TODO: no more used
    def getAdminToken(self, token):
        if token.validateToken(self.keystone_server, token.get_admin_token(), token.get_admin_token()) is True:
            return token.get_admin_token()
        else:
            logging.debug("Admin token out of date, renewing...")
            self.keystoneAuth = KeystoneAuthentication(self.keystone_server,self.tenant,self.username,self.password)
            return self.keystoneAuth.get_admin_token()
    
    
