'''
Created on Sep 29, 2014

@author: fabiomignini
'''
import logging

from json_hyper_schema import Schema, ValidationError

from exception import NF_FGValidationError

class ValidateNF_FG(object):
    '''
    classdocs
    '''
    def validate(self, nffg):
        schema={"$schema":"http://json-schema.org/draft-04/schema#","type":"object","definitions":{"interface":{"type":"object","properties":{"node":{"type":"string"},"switch-id":{"type":"string"},"interface":{"type":"string"}},"required":["interface"],"additionalProperties":False},"gre":{"type":"object","properties":{"local-ip":{"type":"string"},"remote-ip":{"type":"string"},"interface":{"type":"string"},"ttl":{"type":"string"}},"required":["interface","remote-ip","local-ip"],"additionalProperties":False},"vlan":{"type":"object","properties":{"vlan-id":{"type":"string"},"interface":{"type":"string"},"switch-id":{"type":"string"},"node":{"type":"string"}},"required":["vlan-id","interface"],"additionalProperties":False},"match":{"type":"object","properties":{"hard_timeout":{"type":"string"},"ether_type":{"type":"string"},"vlan_id":{"type":"string"},"vlan_priority":{"type":"string"},"source_mac":{"type":"string"},"dest_mac":{"type":"string"},"source_ip":{"type":"string"},"dest_ip":{"type":"string"},"tos_bits":{"type":"string"},"source_port":{"type":"string"},"dest_port":{"type":"string"},"protocol":{"type":"string"},"port_in":{"type":"string"}},"additionalProperties":False},"action":{"type":"object","properties":{"output":{"type":"string"},"set_vlan_id":{"type":"string"},"set_vlan_priority-id":{"type":"string"},"pop_vlan":{"type":"string"},"set_ethernet_src_address":{"type":"string"},"set_ethernet_dst_address":{"type":"string"},"set_ip_src_address":{"type":"string"},"set_ip_dst_address":{"type":"string"},"set_ip_tos":{"type":"string"},"set_l4_src_port":{"type":"string"},"set_l4_dst_port":{"type":"string"},"output_to_queue":{"type":"string"}},"additionalProperties":False}},"properties":{"forwarding-graph":{"type":"object","properties":{"id":{"type":"string"},"name":{"type":"string"},"VNFs":{"type":"array","items":{"type":"object","properties":{"id":{"type":"string"},"name":{"type":"string"},"vnf_template":{"type":"string"},"ports":{"type":"array","items":{"type":"object","properties":{"id":{"type":"string"},"name":{"type":"string"}},"required":["id"],"additionalProperties":False}},"groups":{"type":"array"}},"required":["id","vnf_template","ports"],"additionalProperties":False}},"end-points":{"type":"array","items":{"type":"object","properties":{"id":{"type":"string"},"name":{"type":"string"},"type":{"enum":["internal","interface","interface-out","gre-tunnel","vlan"]},"remote_endpoint_id":{"type":"string"},"prepare_connection_to_remote_endpoint_ids":{"type":"array","items":{"type":"string"}},"internal":{},"interface":{"$ref":"#/definitions/interface"},"interface-out":{"$ref":"#/definitions/interface"},"gre-tunnel":{"$ref":"#/definitions/gre"},"vlan":{"$ref":"#/definitions/vlan"}},"required":["id"],"additionalProperties":False}},"big-switch":{"type":"object","properties":{"flow-rules":{"type":"array","items":{"type":"object","properties":{"id":{"type":"string"},"priority":{"type":"integer"},"match":{"$ref":"#/definitions/match"},"action":{"type":"array","items":{"$ref":"#/definitions/action"}}},"required":["id","priority","match","action"]}}},"required":["flow-rules"]}},"required":["id"],"additionalProperties":False}},"required":["forwarding-graph"],"additionalProperties":False}
        hyperschema = Schema(schema)
        try:
            hyperschema.validate(nffg)
        except ValidationError as err:
            logging.info(err.message)
            raise NF_FGValidationError(err.message)
        
