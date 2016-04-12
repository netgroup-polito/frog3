'''
Created on Sep 29, 2014

@author: fabiomignini
'''
import logging

from json_hyper_schema import Schema, ValidationError

from exception import TemplateValidationError

class ValidateTemplate(object):

    def validate(self, template):
        schema={"$schema":"http://json-schema.org/draft-04/schema#","type":"object","properties":{"name":{"type":"string"},"expandable":{"type":"boolean"},"vnf-type":{"type":"string"},"uri":{"type":"string"},"memory-size":{"type":"number"},"root-file-system-size":{"type":"number"},"ephemeral-file-system-size":{"type":"number"},"swap-disk-size":{"type":"number"},"CPUrequirements":{"type":"object","properties":{"platformType":{"type":"string"},"socket":{"type":"array","items":{"type":"object","properties":{"coreNumbers":{"type":"number"}}}}}},"ports":{"type":"array","items":{"type":"object","properties":{"position":{"type":"string","pattern": "^(([0-9]|[1-9][0-9]*)([-](([1-9]?[0-9]*)|N))?)$"},"label":{"type":"string"},"min":{"type":"string"},"ipv4-config":{"type":"string"},"ipv6-config":{"type":"string"},"name":{"type":"string"}},"required":["position","label","min","name"],"additionalProperties":False}}},"required":["memory-size","CPUrequirements","ports"],"additionalProperties":False}
        hyperschema = Schema(schema)                
        try:
            hyperschema.validate(template)
        except ValidationError as err:
            logging.debug(err.message)
            raise TemplateValidationError(err.message)