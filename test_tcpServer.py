#!/usr/bin/python -B
# -*- coding: utf-8 -*-
###########################
# | . _ |_ _|_ _  _ |  _  #
# |_|(_|| | | |_)(_)|<(/_ #
#     _|      |           #
###########################
#- Atools, test_tcpServer.py is a simple test for running a TCP server using atools/asocket
# See included "License.txt"
from atools import *
import conf

#- Create a socket manager using the select backend
manager = asocketManager(backend = conf.backend)
#- Get a managed socket, pass in any parameters
server = manager.getSocket(protocol = 'tcp', bufferSize = 1024)
server.bind(port = 2525) #- Bind a specific port

print 'Listening for TCP connections on %s:%s' % (asocket.getLocalAddress(), 2525)
#- A simple main loop, calling manager.step each frame, that way each socket is updated, sends out and recieves data
clients = []
while True:
	client = server.accept()
	if client:
		clients.append(client)
		print 'Heyy we got a client: %s:%s' % client.getPeerAddress()
		client.send('Sorry I gotta cut you off..')
		client.shutdown('I killed him') #- No longer recieve data from this client, the message can be retieved via getBroken

	for client in clients:
		if client.isBroken():
			print 'Lost client:', client.getBroken()
			clients.remove(client)

	manager.step()

