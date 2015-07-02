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
from Common.authentication import KeystoneAuthentication
from Common.NF_FG.validator import ValidateNF_FG
from Common.exception import wrongRequest, unauthorizedRequest, sessionNotFound, ingoingFlowruleMissing, ManifestValidationError




class UpperLayerOrchestrator(object):
    '''
    Admin class that intercept the REST call through the WSGI server
    '''

    def __init__(self, AUTH_SERVER, orch_UN,orch_PW,orch_tenant):
        '''
        Constructor
        '''
        self.username=orch_UN;
        self.password=orch_PW; 
        self.tenant=orch_tenant;
        self.keystone_server = AUTH_SERVER;
        try:
            self.keystoneAuth = KeystoneAuthentication(self.keystone_server, self.tenant, self.username, self.password);
        except:
            logging.exception("Orchestrator not authenticated!!")
            raise
        if self.keystoneAuth is not None:
            logging.info("Login Servlet orchestrator successfully authenticated!!")

        logging.debug('Authenticating the Orchestrator')
        self.keystoneAuth = KeystoneAuthentication(self.keystone_server,self.tenant,self.username,self.password)
        

        
    def on_delete(self, request, response, nffg_id):
        try :
            # Orchestrator authenticates himself
            logging.debug('Authenticating the Orchestrator')
            #self.authenticateOrch()
            
            token = request.get_header("X-Auth-Token")
            
            if token is None:
                description = "{\"error\":{\"message\":\"Please provide an auth token\",\"code\":\"401\",\"title\":\"Unauthorized\"}}"            
                raise falcon.HTTPUnauthorized('Auth token required',
                                              description,
                                              href='http://docs.example.com/auth')
            self.token = token
            
            # Now, it initialize a new controller instance to handle the request        
            controller = UpperLayerOrchestratorController(self.keystone_server, self.keystoneAuth.get_admin_token(), "Orchestrator", self.token, response)

            controller.delete(nffg_id)
            
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
        pass
        
    def on_put(self, request, response):
        """
        Take as body request the NF-FG      
        """
        try:
            # Orchestrator authenticates himself
            logging.info('Authenticating the Orchestrator')
            #self.authenticateOrch()
            
            token = request.get_header("X-Auth-Token")
            nf_fg = json.load(request.stream, 'utf-8')
            ValidateNF_FG(nf_fg).validate()
            
            if token is None:
                description = "{\"error\":{\"message\":\"Please provide an auth token\",\"code\":\"401\",\"title\":\"Unauthorized\"}}"            
                raise falcon.HTTPUnauthorized('Auth token required',
                                              description,
                                              href='http://docs.example.com/auth')
            self.token = token
            
            # Now, it initialize a new controller instance to handle the request        
            controller = UpperLayerOrchestratorController(self.keystone_server, self.keystoneAuth.get_admin_token(), "Orchestrator", self.token, response)
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
    
    def on_post(self, request, response):
        pass
