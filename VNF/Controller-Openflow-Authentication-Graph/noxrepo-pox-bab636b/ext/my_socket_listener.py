#!/usr/bin/env python
'''
    Simple socket server using threads
'''

import socket
import sys

HOST = '130.192.225.156'
PORT = 8888 # Arbitrary non-privileged port

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'

#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

print 'Socket bind complete'

#Start listening on socket
s.listen(10)
print 'Socket now listening'

#now keep talking with the client
while 1:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])

    #Now receive data
    reply = conn.recv(4096)

    #print reply
    #Send some data to remote server
    message = "Auth Ok\r\n"
    try :
        #Set the whole string
        conn.sendall(message)
    except socket.error:
        #Send failed
        print 'Send failed'
        sys.exit()

    print 'Message send successfully'

s.close()