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

from Common.exception import NF_FGValidationError

class ValidateNF_FG(object):
    '''
    classdocs
    '''


    def __init__(self, nf_fg):
        '''
        Constructor
        '''
        self.nf_fg = nf_fg
        
        # TODO: validate id port_label
    
    def validate(self):
        schema={
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "definitions": {
    "port_label": {
      "type": "object",
      "properties": {
        "flowrules": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "action": {
                "type": "object",
                "properties": {
                  "VNF": {
                    "type": "object",
                    "properties": {
                      "id": {
                        "type": "string"
                      },
                      "port": {
                        "type": "string"
                      }
                    },
                    "dependencies": {
                      "id": [
                        "port"
                      ],
                      "port": [
                        "id"
                      ]
                    }
                  },
                  "endpoint": {
                    "type": "object",
                    "properties": {
                      "port": {
                        "type": "string"
                      }
                    }
                  }
                }
              },
              "flowspec": {
                "type": "object",
                "properties": {
                  "matches": {
                    "type": "array",
                    "items": {
                      "type": "object",
                      "properties": {
                        "hardTimeout": {
                          "type": "string"
                        },
                        "priority": {
                          "type": "string"
                        },
                        "etherType": {
                          "type": "string"
                        },
                        "vlanId": {
                          "type": "string"
                        },
                        "vlanPriority": {
                          "type": "string"
                        },
                        "sourceMAC": {
                          "type": "string"
                        },
                        "destMAC": {
                          "type": "string"
                        },
                        "sourceIP": {
                          "type": "string"
                        },
                        "destIP": {
                          "type": "string"
                        },
                        "tosBits": {
                          "type": "string"
                        },
                        "sourcePort": {
                          "type": "string"
                        },
                        "destPort": {
                          "type": "string"
                        },
                        "protocol": {
                          "type": "string"
                        },
                        "id": {
                          "type": "string"
                        }
                      },
                      "additionalProperties": False,
                      "required": [
                        "id"
                      ]
                    }
                  }
                },
                "required": [
                  "matches"
                ]
              }
            },
            "additionalProperties": False,
            "required": [
              "action",
              "flowspec"
            ]
          }
        }
      }
    },
    "node": {
      "type": "object",
      "properties": {
        "VNF": {
          "type": "string"
        },
        "port": {
          "type": "string"
        },
        "endpoint_id": {
          "type": "string"
        }
      },
      "dependencies": {
        "VNF": [
          "port"
        ],
        "port": [
          "VNF"
        ]
      }
    }
  },
  "properties": {
    "profile": {
      "type": "object",
      "properties": {
        "VNFs": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "id": {
                "type": "string"
              },
              "template": {
                "type": "string",
                "format": "uri"
              },
              "ports_labels": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "id": {
                      "type": "string"
                    },
                    "outgoing": {
                      "$ref": "#/definitions/port_label"
                    },
                    "ingoing": {
                      "$ref": "#/definitions/port_label"
                    }
                  }
                }
              }
            },
            "required": [
              "id",
              "template"
            ]
          }
        },
        "endpoints": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "id": {
                "type": "string"
              }
            },
            "required": [
              "id"
            ]
          }
        },
        "links": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "id": {
                "type": "string"
              },
              "nodeA": {
                "$ref": "#/definitions/node"
              },
              "nodeB": {
                "$ref": "#/definitions/node"
              }
            },
            "required": [
              "id"
            ]
          }
        }
      },
      "required": [
        "VNFs",
        "endpoints",
        "links"
      ]
    }
  },
  "required": [
    "profile"
  ]
}
        hyperschema = Schema(schema)
                
        try:
            hyperschema.validate(self.nf_fg)
        except ValidationError as err:
            logging.info(err.message)
            raise NF_FGValidationError(err.message)