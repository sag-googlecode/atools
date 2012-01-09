#!/usr/bin/python -B
# -*- coding: utf-8 -*-
###########################
# | . _ |_ _|_ _  _ |  _  #
# |_|(_|| | | |_)(_)|<(/_ #
#     _|      |           #
###########################
#- Atools, asocketManager.py manages several asockets, using a specified backend (select, poll, epoll)
# See included "License.txt"
from asocket import *
from select import *

class _selectBackend:
	def __init__(self, manager):
		self.__manager = manager

	def step(self):
		selectTime = self.__manager._selectTime
		readList = []
		writeList = []

		actualSockets = self.__manager.getSockets()
		for socket in actualSockets:
			socket._doConnect() #- It already knows if it's connecting

			if socket.isBroken() or socket.isUnableToConnect():
				self.__manager.removeSocket(socket)

			if socket.isBroken() == False:
				readList.append(socket)
			if socket.hasOutgoingData():
				writeList.append(socket)

		read, write, error = select(readList, writeList, [], 0)
		if len(read) > 0:
			client = socket._doAccept()
			if client:
				self.__manager.addSocket(client)
			socket._doRead()
		if len(write) > 0:
			socket._doWrite()


class _pollBackend:
	def __init__(self, manager):
		self.__manager = manager


class _epollBackend:
	def __init__(self, manager):
		self.__manager = manager


class asocketManager:
	def __init__(self, backend = 'select'):
		assert backend == 'select' or backend == 'poll' or backend == 'epoll'
		self.__backend = backend
		if backend == 'select':
			self.__handler = _selectBackend(self)
		elif backend == 'poll':
			self.__handler = _pollBackend(self)
		elif backend == 'epoll':
			self.__handler = _epollBackend(self)
		self._selectTime = 0
		self.__asockets = []

	def step(self):
		self.__handler.step()

	def addSocket(self, socket):
		self.__asockets.append(socket)

	def removeSocket(self, socket):
		self.__asockets.remove(socket)

	def setSelectTime(self, time):
		self._selectTime = time
	
	def getSelectTime(self):
		return self._selectTime

	def getSockets(self):
		return self.__asockets

	def getHandler(self):
		return self.__handler

	def getBackend(self):
		return self.__backend

	def getSocket(self, *args, **kwargs):
		newSocket = asocket(*args, **kwargs)
		self.addSocket(newSocket)
		return newSocket


if __name__ == '__main__':
	handler = asocketManager(backend = 'select')
	handler.setSelectTime(1.0) #- Only works if the backend is select..
	while True:
		handler.step()
