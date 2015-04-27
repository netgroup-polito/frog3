'''
Created on Oct 1, 2014

@author: fabiomignini
'''
import falcon

from jsonschema import validate


class UserProfileValidator():
    
    def validate_sessione(self, session):
        schema = {
                  "title" : "session",
                  "properties" : {                        
                        "session_param" : {
                            "type": "object",
                            "properties": {
                                "mac" : {
                                    "type": "string"
                                }
                            }
                        }                 
                    },
                    "required":["session_param"]   
                }     
            
        
        if 'session' not in session:
            raise falcon.HTTPBadRequest('BadRequest',
                                        'The root value of the json must be session')
        validate(session['session'], schema)

