'''
Created on Oct 2, 2014

@author: fabiomignini
'''

class Manifest(object):
    def __init__(self, manifest):
        self.name = manifest['name']
        self.vnfType = manifest['vnf-type']
        self.uri = manifest['uri']
        self.memorySize = manifest['memory-size']
        self.rootFileSystemSize = manifest['root-file-system-size']
        self.ephemeralFileSystemSize = manifest['ephemeral-file-system-size']
        self.swapDiskSize = manifest['swap-disk-size']
        self.CPUrequirements = CPURequirement(manifest['CPUrequirements']['platformType'],
                                              manifest['CPUrequirements']['socket'])
        
        self.ports = []
        for port in manifest['ports']:
            self.port = Port(port['position'],
                             port['label'],
                             port['min'],
                             port['ipv4-config'],
                             port['ipv6-config'],
                             port['name'])
            self.ports.append(self.port)
            
        if 'expandable' in manifest:
            self.expandable = manifest['expandable']
        else:
            self.expandable = None
            
    def getJSON(self):
        manifest = {}
        manifest['name'] = self.name
        manifest['vnf-type'] = self.vnfType
        manifest['uri'] = self.uri
        manifest['memory-size'] = self.memorySize
        manifest['root-file-system-size'] = self.rootFileSystemSize
        manifest['ephemeral-file-system-size'] = self.ephemeralFileSystemSize
        manifest['swap-disk-size'] = self.swapDiskSize
        manifest['CPUrequirements'] = {}
        manifest['CPUrequirements']['platformType'] = self.CPUrequirements.platformType
        manifest['CPUrequirements']['socket'] = self.CPUrequirements.socket
        manifest['ports'] = []
        if self.expandable is not None:
            manifest['expandable'] = self.expandable
        for port in self.ports:
            j_port = {}
            j_port['name'] = port.name
            j_port['position'] = port.position
            j_port['label'] = port.label
            j_port['min'] = port.min
            j_port['ipv4-config'] = port.ipv4_config
            j_port['ipv6-config'] = port.ipv6_config
            manifest['ports'].append(j_port)
        return manifest
        
        
class CPURequirement(object):
    def __init__(self, platformType, socket):
        self.platformType = platformType
        self.socket = socket
        pass
    
class Port(object):
    def __init__(self, position, label, minimum, ipv4_config, ipv6_config, name):
        self.position = position
        self.label = label
        self.min = minimum
        self.ipv4_config = ipv4_config
        self.ipv6_config = ipv6_config
        self.name = name
        
        
