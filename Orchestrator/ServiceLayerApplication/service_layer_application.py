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

from Common.authentication import KeystoneAuthentication
from Common.exception import sessionNotFound, ingoingFlowruleMissing, ManifestValidationError, NoMacAddress
from ServiceLayerApplication.controller import OrchestratorController

class Orchestrator(object):
    '''
    Orchestrator class that intercept the REST call through the WSGI server
    '''

    def __init__(self,AUTH_SERVER, orch_UN,orch_PW,orch_tenant):
        '''
        Constructor
        '''
        self.username=orch_UN;
        self.password=orch_PW; 
        self.tenant=orch_tenant;
        self.keystone_server = AUTH_SERVER;
        self.keystoneAuth = None;
        pass       
    
    def authenticateOrch(self):
        '''
        Verifies that the Orchestrator is well authenticated by the Keystone server
        '''
        logging.debug('Authenticating the Orchestrator')
        self.keystoneAuth = KeystoneAuthentication(self.keystone_server,self.tenant,self.username,self.password)
    
    def on_delete(self, request, response, mac_address=None):
        '''
        @author: Fabio Mignini
        '''
        try :
            # Orchestrator authenticates himself
            logging.debug('Authenticating the Orchestrator')
            self.authenticateOrch()
            # Now, it initialize a new controller instance to handle the request
            controller = OrchestratorController(self.keystone_server,self.keystoneAuth.get_admin_token(), "DELETE", response, request, self.keystoneAuth, mac_address = mac_address)

            #controller = controller.OrchestratorController(self.keystone_server,self.keystoneAuth.get_admin_token(), response, request)
            controller.delete()
        except NoResultFound:
            print "EXCEPTION - NoResultFound"
            raise falcon.HTTPNotFound()
        except requests.HTTPError as err:
            logging.exception(err.response.text)
            try:
                if 'code' not in json.loads(err.response.text)['error']:
                    code = json.loads(err.response.text)['code']
                else:
                    code = json.loads(err.response.text)['error']['code']
            except ValueError:
                logging.debug("No json error code")
            else:
                
                if code == 401:
                    raise falcon.HTTPUnauthorized(json.loads(err.response.text)['error']['title'],
                                                  json.loads(err.response.text))
                elif code == 403:
                    raise falcon.HTTPForbidden(json.loads(err.response.text)['error']['title'],
                                                  json.loads(err.response.text)) 
                elif code == 404: 
                    raise falcon.HTTPNotFound()
            raise
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
        except sessionNotFound as err:
            logging.exception(err.message)
            raise falcon.HTTPNotFound()
        except falcon.HTTPError as err:
            logging.exception("Falcon "+err.title)
            raise
        except Exception as err:
            try:
                logging.exception(err.message)
            except:
                logging.exception("Unexpected exception")
            raise
   
    def on_put(self, request, response):
        '''  
        @author: Fabio Mignini
        
        Instantiate  user profile
        
        Args:
   
            request:
                example:
                
                    {"session":{
                        "token": token_id,
                        "session_param" : {
                            "mac":"fc:4d:e2:56:9f:19",
                            
                            "endpoint":{
                                "type": "bridged",
                                "interface": "veth1", // questa sara la peer di veth0 in br-det
                                "switch": "br-int"
                            },
                        }    
                    }}
                    
                    endpoint can be also:
                     
                    "endpoint":{
                        "type": "physical"
                        "interface": "eth1"
                    }
                            
                    "endpoint":{
                        "type": "gre"
                        "interface": "eth1"
                        "switch": "br-int"
                        "remoteIP":"10.0.1.1"
                    }  
        '''
        try:
            # Orchestrator authenticates himself
            logging.info('Authenticating the Orchestrator')
            self.authenticateOrch()
            # Now, it initialize a new controller instance to handle the request
            controller = OrchestratorController(self.keystone_server,self.keystoneAuth.get_admin_token(), "PUT",response, request, self.keystoneAuth)
            controller.put()
            response.status = falcon.HTTP_202

            
        except requests.HTTPError as err:
            logging.exception(err.response.text)
            """
            if 'code' not in json.loads(err.response.text)['error']:
                code = json.loads(err.response.text)['code']
            else:
                code = json.loads(err.response.text)['error']['code']
                
            if code == 401:
                raise falcon.HTTPUnauthorized(json.loads(err.response.text)['error']['title'],
                                              json.loads(err.response.text))
            elif code == 403:
                raise falcon.HTTPForbidden(json.loads(err.response.text)['error']['title'],
                                              json.loads(err.response.text)) 
            elif code == 404: 
                raise falcon.HTTPNotFound()
            """
            raise
        except jsonschema.ValidationError as err:
            logging.exception(err.message)
            raise falcon.HTTPBadRequest('Bad Request',
                                        err.message)
 
        except ValueError:
            logging.exception("Malformed JSON")
            raise falcon.HTTPInternalServerError("Internal Server Error","Malformed JSON")
            """
            raise falcon.HTTPError(falcon.HTTP_753,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect.')
            """
        except falcon.HTTPError as err:
            logging.exception("Falcon "+err.title)
            raise
        
        except ingoingFlowruleMissing as err:
            logging.exception("Falcon "+err.get_mess())
            raise falcon.HTTPError(falcon.HTTP_753,
                                   'Ingoing flowrule missing',
                                   err.get_mess())
        except ManifestValidationError as err:
            logging.exception("Falcon "+err.get_mess())
            raise falcon.HTTPInternalServerError("Manifest validation error", err.get_mess())
        except NoMacAddress as err:
            logging.exception("Falcon "+err.get_mess())
            raise falcon.HTTPBadRequest("Bad Request", "You can't add specific ingress rule if an instance of the same graph is already up and runnig and accept all ingress traffic.")
        except Exception as err:
            try:
                logging.exception(err.message)
            except:
                logging.exception("Unexpected exception")
            raise
        except:
            logging.exception("Unexpected exception")
            raise
            

    def on_get(self, request, response):
        try:
            logging.debug('Authenticating the Orchestrator')
            self.authenticateOrch()
            # Now, it initialize a new controller instance to handle the request
            controller = OrchestratorController(self.keystone_server,self.keystoneAuth.get_admin_token(), "GET",response, request, self.keystoneAuth)
            controller.get()
        except ValueError:
            logging.exception("Malformed JSON")
            raise falcon.HTTPError(falcon.HTTP_753,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect.')
        except requests.HTTPError as err:
            logging.exception("CODE: "+err.response.text)
            
            
            if 'code' not in json.loads(err.response.text)['error']:
                code = json.loads(err.response.text)['code']
            else:
                code = json.loads(err.response.text)['error']['code']
                
            if code == 401:
                raise falcon.HTTPUnauthorized(json.loads(err.response.text)['error']['title'],
                                              json.loads(err.response.text))
            elif code == 403:
                raise falcon.HTTPForbidden(json.loads(err.response.text)['error']['title'],
                                              json.loads(err.response.text)) 
            elif code == 404: 
                raise falcon.HTTPNotFound()
            
            raise
        except sessionNotFound as err:
            raise falcon.HTTPNotFound()
        except falcon.HTTPError as err:
            logging.exception("Falcon "+err.title)
            raise
        except Exception as err:
            try:
                logging.exception(err.message)
            except:
                logging.exception("Unexpected exception")
            raise

   
        

                

