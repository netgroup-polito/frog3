__author__ = 'webking'

import ConfigParser
import os

import Utils


class CacheManagerConfig:
    hostname=None
    basepath=None
    novaversion=1
    username=None
    password=None
    tenant=None
    auth_url=None
    mysqlhost=None
    mysqluser=None
    mysqlpass=None
    mysqldb=None
    diskquota=None # To be expressed in MB, <=0 represent no limits
    image_timeout=None
    db_poll_interval=None
    log_file=None
    enable_md5_checking=False
    log_level='INFO'

    def __init__(self,conf_file_path='/etc/nova_precache/compute_service/caching.conf'):
        if not os.path.isfile(conf_file_path):
            raise Exception("Invalid configuration file specified: %s" % conf_file_path)

        config = ConfigParser.RawConfigParser()
        config.read(conf_file_path)

        # General
        self.hostname = config.get('general', 'hostname')
        self.tenant = config.get('general', 'tenant')
        self.username = config.get('general', 'user')
        self.password = config.get('general', 'pass')
        self.auth_url = config.get('general', 'auth_url')
        self.image_timeout = config.getint('general','image_timeout')
        self.db_poll_interval = config.getint('general', 'db_poll_interval')
        self.log_file = config.get('general', 'log_file')
        self.enable_md5_checking = config.getboolean('general','enable_md5_checking')
        self.log_level = config.get('general','log_level')

        # Nova
        self.basepath = config.get('nova', 'base_path')
        if not os.path.exists(self.basepath):
            raise Exception("Image Basepath %s does not exists!" % self.basepath)


        self.novaversion = config.get('nova', 'nova_version')

        # Databse configuration
        self.mysqlhost = config.get('database', 'mysql_host')
        self.mysqldb = config.get('database', 'mysql_db')
        self.mysqluser = config.get('database', 'mysql_user')
        self.mysqlpass = config.get('database', 'mysql_pass')

        # Disk quota must be handled after [nova] basepath
        try:
            self.diskquota = config.getint('general', 'disk_quota')
            if self.diskquota<=0:
                self.diskquota= Utils.get_free_disk_space(self.basepath)
        except ConfigParser.NoOptionError:
            # If the option is missing, we assume as quota all the remaining space of the disk
            self.diskquota = Utils.get_free_disk_space(self.basepath)

