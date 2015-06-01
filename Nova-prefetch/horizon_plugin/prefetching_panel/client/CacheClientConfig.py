__author__ = 'webking'

import ConfigParser
import os


class CacheManagerConfig:
    mysqlhost=None
    mysqluser=None
    mysqlpass=None
    mysqldb=None

    def __init__(self,path):
        if not os.path.isfile(path):
            raise Exception("Invalid configuration file specified: "+path)

        config = ConfigParser.RawConfigParser()
        config.read(path)

        # Databse configuration
        self.mysqlhost = config.get('database', 'mysql_host')
        self.mysqldb = config.get('database', 'mysql_db')
        self.mysqluser = config.get('database', 'mysql_user')
        self.mysqlpass = config.get('database', 'mysql_pass')