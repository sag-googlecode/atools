#!/usr/bin/python -B
# -*- coding: utf-8 -*-
###########################
# | . _ |_ _|_ _  _ |  _  #
# |_|(_|| | | |_)(_)|<(/_ #
#     _|      |           #
###########################
#- Atools, test_broadcastClient.py is a simple test for running a broadcast UDP client using atools/asocket
#- It's important to note these broadcast tests will only function on two seperate IP's (two different computers)
# See included "License.txt"
from atools import *

#- Create a socket manager using the select backend
manager = asocketManager(backend = 'select')
#- Get a managed socket, pass in any parameters
client = manager.getSocket(protocol = 'udp', bufferSize = 1024)
client.setBroadcast()
client.bind(port = 2525)

print 'Broadcasting UDP messages to <broadcast>:%s' % (2525)
#- A simple main loop, calling manager.step each frame, that way each socket is updated, sends out and recieves data
while True:
	data = client.get()
	if data:
		data, address = data
		print 'Got:', data, address
		if data == 'anyone':
			print 'Saying hello to server..'
			client.sendTo('Hello man.. I am a client', ('<broadcast>', 2525))
		else:
			print 'Now quitting'
			exit()
	manager.step()

