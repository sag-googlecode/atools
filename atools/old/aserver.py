# -*- coding: utf-8 -*-
###########################
# | . _ |_ _|_ _  _ |  _  #
# |_|(_|| | | |_)(_)|<(/_ #
#     _|      |           #
###########################
#- Atools, aserver.py provides a simple to use socket server, with optional UDP support
# See included "License.txt"
from asocket import *
from prettyPrint import *
import traceback
import time

class aserver:
	def __init__(self, port, setupUdp = True, udpIp = '', keepSafe = False, *args, **kwargs):
		self.keepSafe = keepSafe
		self.socket = socket(mode='tcp', *args, **kwargs)
		if setupUdp:
			self.udp = socket(mode='udp', *args, **kwargs)
		self.port = port
		try:
			self.socket.bind('', self.port)
			self.udp.bind(udpIp, self.port)
		except socket.error as i:
			#if i.value == asocket.error.addressInUse, asocket.error.permissionDenied, asocket.error.unknownError
			self.doCallback(self.unableToBind, [str(i)])
		self.socket.listen() #- asocket 0.9 provides auto backlog=5, as a default

		self.clients = []
		self.running = True
		self._exitLater = False
		self.subLoops = []
		self.startTime = time.time()

		if self.socket.panda3d:
			self.taskName = 'aserver-step-%s' % self
			taskMgr.add(self.pstep, self.taskName)

	def getUptime(self):
		currentTime = time.time()
		return currentTime - self.startTime

	def doCallback(self, cmd, args = []):
		if self.keepSafe:
			try:
				cmd(*args)
			except Exception as i:
				print 'Class inheriting from aserver has keepSafe on and failed to handle [%s][%s] properly' % (repr(cmd), repr(args))
				print traceback.format_exc()
				print 'Will now continue to run happily..'
		else:
			cmd(*args)

	def log(self, msg):
		if hasattr(self, 'name'):
			msg = self.name + ' ' + msg
		prettyPrint(msg)

	def addClient(self, newClient):
		self.clients.append(newClient)
		newClient.address = newClient.getPeerName()
		self.doCallback(self.handleClientConnect, [newClient])

	def getClients(self):
		return self.clients

	def shutdown(self):
		self._exitLater = True

	def stopServer(self):
		for client in self.clients:
			client.close()
		if self.socket.panda3d:
			taskMgr.remove(self.taskName)
		self.running = False

	def pstep(self, task):
		self.step()
		return task.cont

	def step(self):
		try:
			self.socketStep()
			for n in self.subLoops:
				self.doCallback(n)
			if self._exitLater:
				if len(self.getClients()) == 0:
					self._exit()
		except KeyboardInterrupt:
			self.keyboardInterrupt()

	def _exit(self):
		exit()

	def addLoop(self, call):
		self.subLoops.append(call)

	def socketStep(self):
		try:
			newClient = self.socket.accept()
		except socket.error as i:
			if i.value == socket.error.unknownError:
				newClient = None
				print 'Aserver: an unknown error accepting client, [%s].' % i
			elif i.value == socket.error.maxFilesError:
				newClient = None #- Max file descriptors reached
			else:
				print i
			return
		if newClient:
			self.clients.append(newClient)
			self.doCallback(self.handleClientConnect, [newClient])

		for client in self.getClients():
			try:
				client.step()
			except socket.error as i:
				if i.value == socket.error.unflushedData:
					print 'Aserver: got bad unflushed data, ignoring.'
				elif i.value == socket.error.unknownError:
					print 'Aserver: an unknown error steping client, ignoring.'

			if self._exitLater:
				client.shutdown()

			data = client.get()
			if data:
				self.doCallback(self.handleClientData, [client, data])

			if client.getBroken():
				try:
					self.clients.remove(client)
				except ValueError:
					pass
				self.doCallback(self.handleClientDeath, [client, client.getBroken()])

	def sendToAll(self, data):
		for client in self.getClients():
			client.send(data)

	def run(self):
		try:
			while self.running:
				self.step()
		except KeyboardInterrupt:
			self.keyboardInterrupt()
