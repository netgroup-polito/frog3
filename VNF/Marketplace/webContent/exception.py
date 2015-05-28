'''
Created on May 23, 2015

@author: fabiomignini
'''
class Unauthorized(Exception):
    def __init__(self, message):
        self.message = message
        
    def get_mess(self):
        return self.message
