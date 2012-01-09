#! /usr/bin/python
# -*- coding: utf-8 -*-
###########################
# | . _ |_ _|_ _  _ |  _  #
# |_|(_|| | | |_)(_)|<(/_ #
#     _|      |           #
###########################
#- Atools, asocketManager.py provides the manager for all asocket's, required for asocket to function properly
# See included "License.txt"

from asocket import *
import select
from errno import *

class asocketManager:
	def __init__(self):
		self.__sockets = []
		self.__selectTime = 5

	def setSelectTime(self, time):
		self.__selectTime = time

	def getSelectTime(self):
		return self.__selectTime

	def add(self, socket):
		self.__sockets.append(socket)

	def getSocket(self, *args, **kwargs):
		socket = asocket(*args, **kwargs)
		self.add(socket)
		return socket

	def destroy(self, reason = 'Socket closed'):
		for socket in self.__sockets:
			socket.close(reason)

	def step(self):
		writeSockets = []
		readSockets = []
		for socket in self.__sockets:
			if socket.getBroken() or socket.getUnableToConnect():
				self.__sockets.remove(socket)
			else:
				if socket.getProtocol() == 'tcp' and socket.isConnected() == False and socket.isBound() == False:
					pass
				else:
					if len(socket._outgoingQueue) > 0:
						writeSockets.append(socket)
					if socket.isShuttingDown() and len(socket._outgoingQueue) == 0:
						socket.close('Socket shutdown')
					else:
						readSockets.append(socket)

			if socket._doingConnect:
				ret = socket.getSocket().connect_ex(socket._doingConnect)

				if ret == ECONNREFUSED or ret == ETIMEDOUT:
					#- Unable to connect, connection refused or timed out
					socket._unableToConnect = 'Connection refused'
					socket._doingConnect = None

				elif ret == EINPROGRESS or ret == EALREADY or ret == EWOULDBLOCK or ret == EINVAL:
					#- Still connecting, as we should
					pass

				elif ret == EISCONN or ret == 0:
					#- Connected
					socket._doingConnect = None
					socket._connected = True
				else:
					print 'asocket::unknown error, uncought connect_ex code:', ret, errorcode[ret]


		try:
			read, write, error = select.select(readSockets, writeSockets, [], self.getSelectTime())
		except Exception as i:
			if i[0] == 4:
				raise KeyboardInterrupt
			elif i[0] == WSAEINVAL:
				pass #- Winsock says we are connecting still? I suppose
			else:
				print 'asocket::unknown error, uncought select exception:', i, errorcode[i[0]]
			return

		for s in read:
			if s.getProtocol() == 'tcp' and s.isBound():
				#- listen for clients
				try:
					cs, ca = s.getSocket().accept()
				except Exception as i:
					if i[0] == 4:
						raise KeyboardInterrupt
					elif hasattr(i, 'errno'):
						if i.errno == 22:
							raise asocketError('Any bound server socket, must have a backlog! socket.listen(backlog=5)', asocketError.programmerError)
						elif i.errno == 24:
							raise asocketError('Too many open file descriptors. This is an OS limit.', asocketError.maxFilesError)
						else:
							print 'asocket::unknown error, uncought accept code', i.errno, errorcode[i.errno]
					else:
						raise i
					return

				ncs = asocket(protocol = 'tcp', socketObject = cs, address = ca, bufferSize = s.getBufferSize(), ipv6 = s.getIpv6())
				ncs._connected = True
				self.add(ncs)
				s._connectionQueue.append(ncs)

			else:
				try:
					if s.getProtocol() == 'tcp':
						data = s.getSocket().recv(s.getBufferSize())
					elif s.getProtocol() == 'udp':
						data = s.getSocket().recvfrom(s.getBufferSize())
				except Exception as i:
					data = ''
					if i.errno == ECONNABORTED:
						s._broken = 'Connection lost'
					elif i.errno == EBADF:
						s._broken = 'Connection lost'
					elif i.errno == 104:
						s._broken = 'Connection reset by peer'
					else:
						print 'asocket::unknown error, uncought read code', i.errno, errorcode[i.errno]

				if data:
					if s.getProtocol() == 'tcp':
						s._bytesRead += len(data)
						s._incomingQueue.append(data)
					elif s.getProtocol() == 'udp':
						useData = True
						if hasattr(s, '_localIp'):
							if s._localIp == data[1][0]:
								useData = False #- It's our own UDP packet!
						if useData:
							s._bytesRead += len(data[0])
							s._incomingQueue.append(data)
				else:
					if s.getBroken():
						pass
					else:
						s._broken = 'Connection lost'

		for s in write:
			if s.getProtocol() == 'tcp':
				if s.isConnected():
					data = s._outgoingQueue.popleft()
					s._bytesSent += len(data)
					s.getSocket().send(data)
					if s.isShuttingDown():
						if len(s._outgoingQueue) == 0:
							s.close('Socket shutdown')
			elif s.getProtocol() == 'udp':
				data, address = s._outgoingQueue.popleft()
				s._bytesSent += len(data)
				s.getSocket().sendto(data, address)
				if s.isShuttingDown():
					if len(s._outgoingQueue) == 0:
						s.close('Socket shutdown')



if __name__ == '__main__':
	mgr = asocketManager()

	s = mgr.getSocket('tcp', bufferSize = 1024, ipv6 = False)
	s.connect(getAddressByName('www.google.org')[0], 80)
	s.send('FAIL\r\n')


	informed = False
	while True:
		mgr.step()

		if s.isConnected() and informed == False:
			print 'Connected to:', s.getAddress()
			informed = True
		if s.getUnableToConnect():
			print 'Unable to connect!', s.getUnableToConnect()
			break

		if s.getBroken():
			print 'Socket broken,', s.getBroken()
			break

		data = s.get()
		if data:
			print 'Got data:', data
