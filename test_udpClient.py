#!/usr/bin/python -B
# -*- coding: utf-8 -*-
###########################
# | . _ |_ _|_ _  _ |  _  #
# |_|(_|| | | |_)(_)|<(/_ #
#     _|      |           #
###########################
#- Atools, test_udpClient.py is a simple test for running a UDP client using atools/asocket
# See included "License.txt"
from atools import *
import conf

#- Create a socket manager using the select backend
manager = asocketManager(backend = conf.backend)
#- Get a managed socket, pass in any parameters
client = manager.getSocket(protocol = 'udp', bufferSize = 1024)

print 'Sending UDP messages to localhost:%s' % (2525)
#- A simple main loop, calling manager.step each frame, that way each socket is updated, sends out and recieves data
while True:
	client.sendTo('Hello man.. I am a client', ('localhost', 2525))
	data = client.get()
	if data:
		data, address = data
		print 'Got:', data, address
		print 'Now quitting'
		exit()
	manager.step()

