'''
Created on Oct 25, 2014

@author: fabiomignini
'''

from Common.NF_FG.nf_fg import NF_FG

class ServiceGraph(object):
    """
    Represent the service Graph
    """
    def __init__(self, graph):
        self.graph = graph
        
    def getNF_FG(self):
        return NF_FG(self.graph)
        
