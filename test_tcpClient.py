#!/usr/bin/python -B
# -*- coding: utf-8 -*-
###########################
# | . _ |_ _|_ _  _ |  _  #
# |_|(_|| | | |_)(_)|<(/_ #
#     _|      |           #
###########################
#- Atools, test_tcpClient.py is a simple test for running a TCP client using atools/asocket
# See included "License.txt"
from atools import *

#- Create a socket manager using the select backend
manager = asocketManager(backend = 'select')
#- Get a managed socket, pass in any parameters
client = manager.getSocket(protocol = 'tcp', bufferSize = 1024)

#- Connect on a host, port, while this is non-blocking, unfortunetly the DNS lookup is blocking
#- So take this with a grain of salt: you might want to use IP addresses unless you want to impliment a non-blocking
#- DNS resolver
client.connect('www.google.com', 80)

#- A simple main loop, calling manager.step each frame, that way each socket is updated, sends out and recieves data
hasSaidConnected = False
while True:
	if client.isUnableToConnect():
		print 'Unable to connect to %s:%s!' % client.getPeerAddress()
		exit()
	if client.isConnected() and hasSaidConnected == False:
		print 'Connected to %s:%s!' % client.getPeerAddress()
		hasSaidConnected = True
		client.send('GET\r\n')
	if client.isConnecting():
		print 'Connecting to %s:%s... one iteration..' % client.getPeerAddress()
	data = client.get()
	if data:
		print 'Got response from %s:%s.. first 60 bytes are:' % client.getPeerAddress()
		print repr(data[:60])
		print 'Now quitting'
		exit()
	manager.step()

