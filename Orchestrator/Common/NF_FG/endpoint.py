'''
Created on Oct 1, 2014

@author: fabiomignini
'''


class EndpointManagement(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        pass
        
    def bridgedEndpoint(self, profile, endpoint_id, user_mac,  switch, interface):
        for endpoint in profile['profile']['endpoints']:
            if endpoint['id'] == endpoint_id:
                for flowrule in endpoint['endpoints_labels']['outgoing']['flowrules']:
                    for match in flowrule['flowspec']['matches']:
                        if match['sourceMAC'] == user_mac:
                            flowrule['flowspec']['type'] = 'bridged'
                            flowrule['flowspec']['switch'] = switch
                            flowrule['flowspec']['interface'] = interface  
                            break      
        return profile
    
    def greEndpoint(self, profile, endpoint_id, user_mac, localIP, localInterface, remoteIP):
        for endpoint in profile['profile']['endpoints']:
            if endpoint['id'] == endpoint_id:
                for flowrule in endpoint['endpoints_labels']['outgoing']['flowrules']:
                    for match in flowrule['flowspec']['matches']:
                        if match['sourceMAC'] == user_mac:
                            endpoint['type'] = 'gre'
                            endpoint['localIP'] = localIP
                            endpoint['interface'] = localInterface
                            endpoint['remoteIP'] = remoteIP      
                            break  
        return profile