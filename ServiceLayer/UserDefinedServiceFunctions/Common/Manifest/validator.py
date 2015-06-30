'''
Created on Oct 1, 2014

@author: fabiomignini
'''

'''
Created on Sep 29, 2014

@author: fabiomignini
'''
import logging

from json_hyper_schema import Schema, ValidationError

from Common.exception import ManifestValidationError

class ValidateManifest(object):
    '''
    classdocs
    '''


    def __init__(self, manifest):
        '''
        Constructor
        '''
        self.manifest = manifest
    
    def validate(self):
        schema={
                    "$schema": "http://json-schema.org/draft-04/schema#",
                    "type": "object",
                    "properties": {
                      "name": {
                         "type": "string"
                      },
                      "expandable": {
                         "type": "boolean"
                      },
                      "vnf-type": {
                        "type": "string"
                      },
                      "uri": {
                        "type": "string"
                      },
                      "memory-size": {
                        "type": "number"
                      },
                      "root-file-system-size": {
                        "type": "number"
                      },
                      "ephemeral-file-system-size": {
                        "type": "number"
                      },
                      "swap-disk-size":{
                        "type": "number"
                      },
                      "CPUrequirements": {
                        "type": "object",
                        "properties": {
                          "platformType": {
                            "type": "string"
                          },
                          "socket": {
                            "type": "array",
                            "items": {
                              "type": "object",
                              "properties": {
                                "coreNumbers": {
                                  "type": "number"
                                }
                              }
                            }
                          }
                        }
                      },
                      "ports": {
                        "type": "array",
                        "items": {
                          "type": "object",
                          "properties": {
                            "position": {
                              "type": "string"
                            },
                            "label": {
                              "type": "string"
                            },
                            "min": {
                              "type": "string",
                              
                            },
                            "ipv4-config": {
                              "type": "string"
                            },
                            "ipv6-config": {
                              "type": "string"
                            },
                            "name": {
                              "type": "string"
                            }
                          }
                        }
                      }
                    },
                    "required": [
                      "memory-size",
                      "CPUrequirements",
                      "ports"
                    ]
                  }
        hyperschema = Schema(schema)
        
        # TODO: checks that max number of ports is higher or equals to min
        
        #"pattern": "^([1-9][0-9]*(\.{2}(([1-9][0-9]*)|N))?)$"
                
        try:
            hyperschema.validate(self.manifest)
        except ValidationError as err:
            logging.debug(err.message)
            raise ManifestValidationError(err.message)
            
        