'''
Created on Oct 2, 2014

@author: fabiomignini
'''

class Template(object):
    def __init__(self, name = None, expandable = False, vnf_type = None,
                uri = None, memory_size = 0, root_file_system_size = 0, 
                ephemeral_file_system_size = 0, swap_disk_size = 0,
                cpu_requirements = None, ports = None):
        self.name = name
        self.expandable = expandable
        self.vnf_type = vnf_type
        self.uri = uri
        self.memory_size = memory_size
        self.root_file_system_size = root_file_system_size
        self.ephemeral_file_system_size = ephemeral_file_system_size
        self.swap_disk_size = swap_disk_size
        self.cpu_requirements = cpu_requirements
        self.ports = ports or []
                 
    def parseDict(self, template_dict):
        if 'name' in template_dict:
            self.name = template_dict['name']
        if 'expandable' in template_dict:
            self.expandable = template_dict['expandable']
        if 'vnf-type' in template_dict:
            self.vnf_type = template_dict['vnf-type']
        if 'uri' in template_dict:
            self.uri = template_dict['uri']
        self.memory_size = template_dict['memory-size']
        if 'root-file-system-size' in template_dict:
            self.root_file_system_size = template_dict['root-file-system-size']
        if 'ephemeral-file-system-size' in template_dict:
            self.ephemeral_file_system_size = template_dict['ephemeral-file-system-size']
        if 'swap-disk-size' in template_dict:
            self.swap_disk_size = template_dict['swap-disk-size']
        cpu_req = CPURequirement()
        cpu_req.parseDict(template_dict['CPUrequirements'])
        self.cpu_requirements = cpu_req
        for port_dict in template_dict['ports']:
            port = Port()
            port.parseDict(port_dict)
            self.ports.append(port) 

    def getDict(self):
        template_dict = {}
        if self.name is not None:
            template_dict['name'] = self.name
        if self.vnf_type is not None:            
            template_dict['vnf-type'] = self.vnf_type
        if self.uri is not None:
            template_dict['uri'] = self.uri
        if self.memory_size is not None:    
            template_dict['memory-size'] = self.memory_size
        if self.root_file_system_size is not None:
            template_dict['root-file-system-size'] = self.root_file_system_size
        if self.ephemeral_file_system_size is not None:
            template_dict['ephemeral-file-system-size'] = self.ephemeral_file_system_size
        if self.swap_disk_size is not None:
            template_dict['swap-disk-size'] = self.swap_disk_size
        if self.expandable is not None:
            template_dict['expandable'] = self.expandable
        template_dict['CPUrequirements'] = self.cpu_requirements.getDict()
        ports_dict = []
        for port in self.ports:
            ports_dict.append(port.getDict())
        if ports_dict:
            template_dict['ports'] = ports_dict
        return template_dict
    
    def checkExpansion(self):
        """
        return True if the VNF is a new graph
        """
        if self.expandable == True:
            return True
        return False
    
class CPURequirement(object):
    def __init__(self, platform_type = None, socket = None):
        self.platform_type = platform_type
        self.socket = socket
        
    def parseDict(self, cpu_requirement):
        if 'platformType' in cpu_requirement:
            self.platform_type = cpu_requirement['platformType']
        if 'socket' in cpu_requirement:
            self.socket = cpu_requirement['socket']
    
    def getDict(self):
        cpu_requirements = {}
        if self.platform_type is not None:
            cpu_requirements['platformType'] = self.platform_type
        if self.socket is not None:             
            cpu_requirements['socket'] = self.socket
        return cpu_requirements
    
class Port(object):
    def __init__(self, position = None, label = None, minimum = None, ipv4_config = None, ipv6_config = None, name = None):
        self.position = position
        self.label = label
        self.min = minimum
        self.ipv4_config = ipv4_config
        self.ipv6_config = ipv6_config
        self.name = name
    
    def parseDict(self, port_dict):
        self.position = port_dict['position']
        self.label = port_dict['label']
        self.min = port_dict['min']
        if 'ipv4-config' in port_dict:
            self.ipv4_config = port_dict['ipv4-config']
        if 'ipv6-config' in port_dict:
            self.ipv6_config = port_dict['ipv6-config']
        self.name = port_dict['name']
    
    def getDict(self):
        port_dict = {}
        if self.name is not None:
            port_dict['name'] = self.name
        if self.position is not None:             
            port_dict['position'] = self.position
        if self.label is not None:
            port_dict['label'] = self.label
        if self.min is not None:
            port_dict['min'] = self.min
        if self.ipv4_config is not None:
            port_dict['ipv4-config'] = self.ipv4_config
        if self.ipv6_config is not None:            
            port_dict['ipv6-config'] = self.ipv6_config
        return port_dict