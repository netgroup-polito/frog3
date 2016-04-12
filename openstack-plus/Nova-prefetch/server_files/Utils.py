__author__ = 'webking'
import os
import statvfs


def get_free_disk_space(path):
        s = os.statvfs(path)
        freebytes = s[statvfs.F_BSIZE] * s[statvfs.F_BAVAIL]
        return freebytes / (1024*1024)