'''
Created on Oct 1, 2014

@author: fabiomignini
'''
import controller
import requests
import falcon
import json
import jsonschema
import logging

from sqlalchemy.orm.exc import NoResultFound
from service_layer_application_core.user_authentication import UserAuthentication
from service_layer_application_core.exception import SessionNotFound
from service_layer_application_core.controller import ServiceLayerController
from service_layer_application_core.validate_request import RequestValidator

class ServiceLayer(object):
    '''
    Orchestrator class that intercept the REST call through the WSGI server
    '''
    
    def on_delete(self, request, response, mac_address=None):
        try :
            user_data = UserAuthentication().authenticateUserFromRESTRequest(request)
            # Now, it initialize a new controller instance to handle the request
            controller = ServiceLayerController(user_data)
            controller.delete(mac_address = mac_address)
        except NoResultFound:
            print "EXCEPTION - NoResultFound"
            raise falcon.HTTPNotFound()
        except requests.HTTPError as err:
            logging.exception(err.response.text)
            if err.response.status_code == 401:
                raise falcon.HTTPUnauthorized(json.loads(err.response.text)['error']['title'],
                                              json.loads(err.response.text))
            elif err.response.status_code == 403:
                raise falcon.HTTPForbidden(json.loads(err.response.text)['error']['title'],
                                              json.loads(err.response.text)) 
            elif err.response.status_code == 404: 
                raise falcon.HTTPNotFound()
            raise err
        except jsonschema.ValidationError as err:
            logging.exception(err.message)
            raise falcon.HTTPBadRequest('Bad Request',
                                        err.message)
        except ValueError:
            
            logging.exception("Malformed JSON")
            raise falcon.HTTPError(falcon.HTTP_753,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect.')
        except SessionNotFound as err:
            logging.exception(err.message)
            raise falcon.HTTPNotFound()
        except falcon.HTTPError as err:
            logging.exception("Falcon "+err.title)
            raise
        except Exception as err:
            logging.exception(err)
            raise falcon.HTTPInternalServerError('Contact the admin. ',err.message)
   
    def on_put(self, request, response):
        '''          
        Instantiate  user profile
        Args:
            request: json that contain the MAC address of the user device {"session":{"mac":"fc:4d:e2:56:9f:19"}}
        '''
        try:
            user_data = UserAuthentication().authenticateUserFromRESTRequest(request)
            # Now, it initialize a new controller instance to handle the request
            controller = ServiceLayerController(user_data)
            request_dict = json.load(request.stream, 'utf-8')
            RequestValidator().validate(request_dict)
            if 'mac' in request_dict['session']:
                controller.put(mac_address = request_dict['session']['mac'])
            else:
                controller.put(mac_address = None)        
            response.status = falcon.HTTP_202
        except requests.HTTPError as err:
            logging.exception(err.response.text)
            if err.response.status_code == 401:
                raise falcon.HTTPUnauthorized(json.loads(err.response.text)['error']['title'],
                                              json.loads(err.response.text))
            elif err.response.status_code == 403:
                raise falcon.HTTPForbidden(json.loads(err.response.text)['error']['title'],
                                              json.loads(err.response.text)) 
            elif err.response.status_code == 404: 
                raise falcon.HTTPNotFound()
            raise err
        except jsonschema.ValidationError as err:
            logging.exception(err.message)
            raise falcon.HTTPBadRequest('Bad Request',
                                        err.message)
        except ValueError:
            logging.exception("Malformed JSON")
            raise falcon.HTTPInternalServerError("Internal Server Error","Malformed JSON")
        except falcon.HTTPError as err:
            logging.exception("Falcon "+err.title)
            raise
        except Exception as err:
            logging.exception(err)
            raise falcon.HTTPInternalServerError('Contact the admin. ',err.message)
            

    def on_get(self, request, response):
        try:
            user_data = UserAuthentication().authenticateUserFromRESTRequest(request)
            # Now, it initialize a new controller instance to handle the request
            controller = ServiceLayerController(user_data)
            controller.get()
        except ValueError:
            logging.exception("Malformed JSON")
            raise falcon.HTTPError(falcon.HTTP_753,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect.')
        except requests.HTTPError as err:
            logging.exception(err.response.text)
            if err.response.status_code == 401:
                raise falcon.HTTPUnauthorized(json.loads(err.response.text)['error']['title'],
                                              json.loads(err.response.text))
            elif err.response.status_code == 403:
                raise falcon.HTTPForbidden(json.loads(err.response.text)['error']['title'],
                                              json.loads(err.response.text)) 
            elif err.response.status_code == 404: 
                raise falcon.HTTPNotFound()
            raise err
        except SessionNotFound as err:
            raise falcon.HTTPNotFound()
        except falcon.HTTPError as err:
            logging.exception("Falcon "+err.title)
            raise
        except Exception as err:
            logging.exception(err)
            raise falcon.HTTPInternalServerError('Contact the admin. ',err.message)