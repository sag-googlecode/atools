#!/usr/bin/python -B
# -*- coding: utf-8 -*-
###########################
# | . _ |_ _|_ _  _ |  _  #
# |_|(_|| | | |_)(_)|<(/_ #
#     _|      |           #
###########################
#- Atools, test_c10kClient.py is a mass-connection opener
#- http://www.kegel.com/c10k.html
# See included "License.txt"
from atools import *
import conf

print 'Warning: this test will open 2048 connections, this could hurt your network'
if raw_input('Continue? [y/n]: ') != 'y':
	exit()

asocket.setMaxFiles(2048, silent = False) #- Giggles

#- Create a socket manager using the select backend
manager = asocketManager(backend = conf.backend)

clients = []

googleIp = asocket.getHostByName('www.google.com')
maxFilesHit = False
previousNumConnected = 0
while True:
	if maxFilesHit == False:
		for i in range(256): #- Hehe 5 steps and max files for select..
			#- Get a managed socket, pass in any parameters
			try:
				client = manager.getSocket(protocol = 'tcp', bufferSize = 1024)
				client.connect(googleIp, 80, doLookup = False)
				clients.append(client)
			except asocket.error as i:
				if i.getValue() == asocket.error.maxFilesError:
					print 'Hit max files', len(clients)
					maxFilesHit = True
				else:
					raise

	numConnected = 0
	for client in clients:
		if client.isUnableToConnect():
			print 'Unable to connect to %s:%s!' % client.getPeerAddress()
	#	if client.isConnecting():
	#		print 'Connecting to %s:%s... one iteration..' % client.getPeerAddress()
		if client.isConnected():
			numConnected += 1
	
	if numConnected != previousNumConnected:
		print '%s connected currently' % numConnected
		previousNumConnected = numConnected

	#	data = client.get()
	#	if data:
	#		print 'Got response from %s:%s.. data:' % client.getPeerAddress()
	#		print repr(data)
	#		print 'Now quitting'
	#		exit()
	manager.step()

