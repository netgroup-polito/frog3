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
from nffg_library.validator import ValidateNF_FG
from nffg_library.nffg import NF_FG

from orchestrator_core.controller import UpperLayerOrchestratorController
from orchestrator_core.userAuthentication import UserAuthentication
from orchestrator_core.exception import wrongRequest, unauthorizedRequest, sessionNotFound, ingoingFlowruleMissing, ManifestValidationError
from orchestrator_core.nffg_manager import NFFG_Manager

class YANGAPI(object):
    
    def on_get(self, request, response, instance_id):
        try :
            user_data = UserAuthentication().authenticateUserFromRESTRequest(request)
            controller = UpperLayerOrchestratorController(user_data)
            response.body = controller.getYANG(instance_id)
        except unauthorizedRequest as err:
            logging.debug("Unauthorized access attempt from user "+request.get_header("X-Auth-User"))
            raise falcon.HTTPUnauthorized("Unauthorized", err.message)
        except Exception as ex:
            logging.exception(ex)
            raise falcon.HTTPInternalServerError('Contact the admin. ',ex.message)
    
class TemplateAPI(object):
    
    def on_get(self, request, response, instance_id):
        try :
            user_data = UserAuthentication().authenticateUserFromRESTRequest(request)
            controller = UpperLayerOrchestratorController(user_data)
            response.body = controller.getTemplate(instance_id)
        except unauthorizedRequest as err:
            logging.debug("Unauthorized access attempt from user "+request.get_header("X-Auth-User"))
            raise falcon.HTTPUnauthorized("Unauthorized", err.message)
        except Exception as ex:
            logging.exception(ex)
            raise falcon.HTTPInternalServerError('Contact the admin. ',ex.message)
    
class TemplateAPILocation(object):
    
    def on_get(self, request, response, template_location):
        try :
            UserAuthentication().authenticateUserFromRESTRequest(request)
            response.body = json.dumps(NFFG_Manager(None).getTemplate(template_location).getDict())
        except unauthorizedRequest as err:
            logging.debug("Unauthorized access attempt from user "+request.get_header("X-Auth-User"))
            raise falcon.HTTPUnauthorized("Unauthorized", err.message)
        except Exception as ex:
            logging.exception(ex)
            raise falcon.HTTPInternalServerError('Contact the admin. ',ex.message)

class NFFGStatus(object):
    def on_get(self, request, response, nffg_id):
        try :
            
            user_data = UserAuthentication().authenticateUserFromRESTRequest(request)
                   
            controller = UpperLayerOrchestratorController(user_data)
            response.body = controller.getStatus(nffg_id)
            
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
        except unauthorizedRequest as err:
            logging.debug("Unauthorized access attempt from user "+request.get_header("X-Auth-User"))
            raise falcon.HTTPUnauthorized("Unauthorized", err.message)
        except Exception as ex:
            logging.exception(ex)
            raise falcon.HTTPInternalServerError('Contact the admin. ',ex.message)
      
class UpperLayerOrchestrator(object):
    '''
    Admin class that intercept the REST call through the WSGI server
    '''
        
    def on_delete(self, request, response, nffg_id):
        try :
            
            user_data = UserAuthentication().authenticateUserFromRESTRequest(request)
                   
            controller = UpperLayerOrchestratorController(user_data)
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
        except unauthorizedRequest as err:
            logging.debug("Unauthorized access attempt from user "+request.get_header("X-Auth-User"))
            raise falcon.HTTPUnauthorized("Unauthorized", err.message)
        except Exception as ex:
            logging.exception(ex)
            raise falcon.HTTPInternalServerError('Contact the admin. ',ex.message)
    
    def on_get(self, request, response, nffg_id):
        try :
            
            user_data = UserAuthentication().authenticateUserFromRESTRequest(request)
                   
            controller = UpperLayerOrchestratorController(user_data)
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
        except unauthorizedRequest as err:
            logging.debug("Unauthorized access attempt from user "+request.get_header("X-Auth-User"))
            raise falcon.HTTPUnauthorized("Unauthorized", err.message)
        except Exception as ex:
            logging.exception(ex)
            raise falcon.HTTPInternalServerError('Contact the admin. ',ex.message)
        
    def on_put(self, request, response):
        """
        Take as body request the NF-FG      
        """
        try:
            
            user_data = UserAuthentication().authenticateUserFromRESTRequest(request)
            
            nffg_dict = json.load(request.stream, 'utf-8')
            ValidateNF_FG().validate(nffg_dict)
            nffg = NF_FG()
            nffg.parseDict(nffg_dict)
            
            controller = UpperLayerOrchestratorController(user_data)
            response.body = controller.put(nffg)

            response.status = falcon.HTTP_202
            
        except wrongRequest as err:
            logging.exception(err)
            raise falcon.HTTPBadRequest("Bad Request", err.description)
        except unauthorizedRequest as err:
            logging.debug("Unauthorized access attempt from user "+request.get_header("X-Auth-User"))
            raise falcon.HTTPUnauthorized("Unauthorized", err.message)
        except requests.HTTPError as err:
            logging.exception(err)
            if err.response.status_code == 401:
                raise falcon.HTTPInternalServerError('Unauthorized.',err.message)
            elif err.response.status_code == 403:
                raise falcon.HTTPInternalServerError('Forbidden.',err.message)
            elif err.response.status_code == 404: 
                raise falcon.HTTPInternalServerError('Resource Not found.',err.message)
            raise err
        except Exception as err:
            logging.exception(err)
            raise falcon.HTTPInternalServerError('Contact the admin. ', err.message)