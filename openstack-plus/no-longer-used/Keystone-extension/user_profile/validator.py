'''
Created on May 22, 2014

@author: fmignini
'''
from jsonschema import validate
from keystone.openstack.common import log
from keystone.common import utils
from keystone import exception
from keystone.openstack.common import jsonutils

import jsonschema

LOG = log.getLogger(__name__)

class UserProfileValidator():
    
    def validate_user_profile(self, profile):
        LOG.info("validator")
        schema = {"profile" : "object",
                  "properties" : {
                      "links" : {
                         "type" : "array",
                         "items": {
                            "type": "object",
                            "properties": {
                                "VNF_A" : {
                                    "type": "string"
                                },
                                "VNF_B" : {
                                    "type": "string"
                                },
                                "port_A" : {
                                    "type": "string"
                                },
                                "port_B" : {
                                    "type": "string"
                                },
                                "flowrules" : {
                                    "type": "array",
                                    "items": {
                                        "type": "object" ,
                                        "properties": {
                                            "action" : {
                                                "type": "object",
                                                "properties": {
                                                    "VNF_id" : {
                                                        "type": "string"
                                                    },
                                                    "port" : {
                                                        "type": "string"
                                                    },
                                                    "type" : {
                                                        "type": "string"
                                                    }
                                                }
                                            },  
                                            "flowspec" : {
                                                "type": "object",
                                                "properties": {
                                                    "source_VNF_id" : {
                                                        "type": "string"
                                                    },         
                                                    "ingressPort" : {
                                                        "type": "string"
                                                    },
                                                    "matches" : {
                                                        "type": "array" ,
                                                        "items": {
                                                            "type": "object" ,
                                                            "properties": {
                                                                "hardTimeout" : {
                                                                    "type": "string"
                                                                },           
                                                                "priority" : {
                                                                    "type": "string"
                                                                },
                                                                "etherType" : {
                                                                    "type": "string"
                                                                },
                                                                "vlanId" : {
                                                                    "type": "string"
                                                                },
                                                                "vlanPriority" : {
                                                                    "type": "string"
                                                                },
                                                                "sourceMAC" : {
                                                                    "type": "string"
                                                                },
                                                                "destMAC" : {
                                                                    "type": "string"
                                                                },
                                                                "sourceIP" : {
                                                                    "type": "string"
                                                                },
                                                                "destIP" : {
                                                                    "type": "string"
                                                                },
                                                                "tosBits" : {
                                                                    "type": "string"
                                                                },
                                                                "sourcePort" : {
                                                                    "type": "string"
                                                                },
                                                                "destPort" : {
                                                                    "type": "string"
                                                                },
                                                                "protocol" : {
                                                                    "type": "string"
                                                                },
                                                                "id" : {
                                                                    "type": "string"
                                                                }
                                                            }#,
                                                            #"additionalProperties" : False,
                                                            #"required":["id"] 
                                                        }
                                                    }                                                   
                                                }#,
                                                #"additionalProperties" : False,
                                                #"required":["source_VNF_id","ingressPort","matches"]
                                            }
                                        }#,
                                        #"additionalProperties" : False,
                                        #"required":["action","flowspec"]
                                    }
                                }
                            }#,
                            #"additionalProperties" : False,
                            #"required":["VNF_A","VNF_B","flowrules"]                 
                        }
                    },
                    "VNFs" : {  
                        "type" : "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id" : {
                                    "type": "string"
                                },
                                "template" : {
                                    
                                    "type": "string"
                                }
                            }#,
                            #"additionalProperties" : False,
                            #"required":["id","template"]
                        }
                    }
                },
                #"additionalProperties" : False,
                #"required":["VNFs","links"]    
        }
        """
        "additionalProperties" : False,
        """
        try:
            validate(profile, schema)
        except jsonschema.ValidationError as e:
            LOG.info("profile")
            LOG.info(profile)
            LOG.info("eccezione")
            LOG.info(e)
            raise exception.ValidationError(message = "schema: "+jsonutils.dumps(schema, cls = utils.SmarterEncoder))