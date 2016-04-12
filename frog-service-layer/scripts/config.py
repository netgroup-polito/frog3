'''
Created on Oct 1, 2014

@author: fabiomignini
'''
import ConfigParser, os, inspect


class Configuration(object):
    
    _instance = None
    #(fmignini) Not too meaningful use this var, I should change his name with something else like inizialized = False 
    _AUTH_SERVER = None
    
    def __new__(cls, *args, **kwargs):
        
        if not cls._instance:
            cls._instance = super(Configuration, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance 
    
    def __init__(self):
        if self._AUTH_SERVER is None:
            self.inizialize()
    
    def inizialize(self): 
        config = ConfigParser.RawConfigParser()
        base_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0])).rpartition('/')[0]
        config.read(base_folder+'/Configuration/service_layer.conf')
        self._AUTH_SERVER = config.get('authentication', 'server')
        
    @property
    def AUTH_SERVER(self):
        return self._AUTH_SERVER

