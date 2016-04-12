'''
Created on Oct 24, 2015

@author: fabiomignini
'''
from vnf_template_library.template import Template
from vnf_template_library.validator import ValidateTemplate
import json

template_dict1 = {"name":"cisco_firewall","expandable":False,"uri":"http://controller:9292/v2/images/6dc7b8af-3b92-4683-9400-ba40420c784b","vnf-type":"virtual-machine","memory-size":2048,"root-file-system-size":40,"ephemeral-file-system-size":0,"swap-disk-size":0,"CPUrequirements":{"platformType":"x86","socket":[{"coreNumbers":1}]},"ports":[{"position":"0-0","label":"User","min":"1","ipv4-config":"none","ipv6-config":"none","name":"eth"},{"position":"1-1","label":"WAN","min":"1","ipv4-config":"none","ipv6-config":"none","name":"eth"}]}
template_dict2 = {"name":"nobody_switch","expandable":False,"uri":"http://controller:9292/v2/images/c476ae2d-89bd-4c02-82ad-d99d4b21499c","vnf-type":"virtual-machine","memory-size":2048,"root-file-system-size":40,"ephemeral-file-system-size":0,"swap-disk-size":0,"CPUrequirements":{"platformType":"x86","socket":[{"coreNumbers":1}]},"ports":[{"position":"1-N","label":"L2Port","min":"1","ipv4-config":"none","ipv6-config":"none","name":"eth"},{"position":"0-0","label":"control","min":"0","ipv4-config":"dhcp","ipv6-config":"none","name":"eth"}]}

ValidateTemplate().validate(template_dict1)
ValidateTemplate().validate(template_dict2)

template1 = Template()
template2 = Template()

template1.parseDict(template_dict1)
template2.parseDict(template_dict2)

print json.dumps(template1.getDict())
print json.dumps(template2.getDict())
