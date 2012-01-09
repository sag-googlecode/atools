#!/usr/bin/python -B
# -*- coding: utf-8 -*-
###########################
# | . _ |_ _|_ _  _ |  _  #
# |_|(_|| | | |_)(_)|<(/_ #
#     _|      |           #
###########################
#- Atools, test_udpServer.py is a simple test for running a UDP server using atools/asocket
#- It's important to note these broadcast tests will only function on two seperate IP's (two different computers)
# See included "License.txt"
from atools import *

#- Create a socket manager using the select backend
manager = asocketManager(backend = 'select')
#- Get a managed socket, pass in any parameters
server = manager.getSocket(protocol = 'udp', bufferSize = 1024)
server.setBroadcast()
server.bind(port = 2525) #- Bind a specific port

print 'broadcasting UDP messages to <broadcast>:%s' % (2525)
#- A simple main loop, calling manager.step each frame, that way each socket is updated, sends out and recieves data
while True:
	server.sendTo('anyone', ('<broadcast>', 2525))
	data = server.get()
	if data:
		data, address = data
		print 'Got:', data, address
		server.sendTo('Hey thanks for that..', address)
	manager.step()

