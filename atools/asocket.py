#!/usr/bin/python -B
# -*- coding: utf-8 -*-
###########################
# | . _ |_ _|_ _  _ |  _  #
# |_|(_|| | | |_)(_)|<(/_ #
#     _|      |           #
###########################
#- Atools, asocket.py provides a non-blocking TCP and UDP socket with multicast support
# See included "License.txt"
from Queue import deque
import subprocess
import socket
import errno
import sys
import re


ip_prog = re.compile(r'\d+\.\d+\.\d+\.\d+')
def getLocalAddress(first = True):
	if sys.platform.startswith('win'):
		command = 'ipconfig'
	else:
		command = 'ifconfig'
	proc = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
	proc.wait()
	output = proc.stdout.read()
	addresses = ip_prog.findall(output)

	if first == True:
		if len(addresses) > 0:
			return addresses[0]
		else:
			return None
	else:
		return addresses


class asocketError(Exception):
	programmerError = 0
	addressInUse = 1
	permissionDenied = 2
	maxFilesError = 3
	def __init__(self, text, value = -1):
		self.__text = text
		self.__value = value

	def getValue(self):
		return self.__value

	def __str__(self):
		return str(self.__text)

	def __repr__(self):
		return repr(self.__text)


class asocket:
	def __init__(self, protocol = 'tcp', bufferSize = 1024, backlog = 5, ipv6 = False, socketObject = None):
		self.__protocol = protocol
		self.__bufferSize = bufferSize
		self.__backlog = backlog
		self.__ipv6 = ipv6
		self.__socket = socketObject

		self.__outgoingQueue = deque()
		self.__incomingQueue = deque()
		self.__connectionQueue = None
		self.__bytesSent = 0
		self.__bytesRead = 0
		self.__localIp = None
		self.__bound = None
		self.__broken = ''
		self.__connected = False
		self.__connecting = None
		self.__isUnableToConnect = False
		self.__shuttingDown = ''

		if self.__socket == None:
			if (self.__protocol == 'tcp' or self.__protocol == 'udp') == False:
				raise asocketError('Incorrect protocol specified for asocket, use "tcp" or "udp"', asocketError.programmerError)
			if self.__ipv6:
				inet = socket.AF_INET6
			else:
				inet = socket.AF_INET

			if self.__protocol == 'tcp':
				proto = socket.SOCK_STREAM
			elif self.__protocol == 'udp':
				proto = socket.SOCK_DGRAM

			self.__socket = socket.socket(inet, proto)

	def send(self, data):
		if self.__protocol == 'udp':
			raise asocketError('udp socket has no attribute send, use sendTo instead', asocketError.programmerError)
		if (type(data) == str or type(data) == unicode) == False:
			raise asocketError('argument to send, data, must be of type str or unicode', asocketError.programmerError)
		if data == '':
			return
		self.__outgoingQueue.append(data)

	def sendTo(self, data, address):
		if self.__protocol == 'tcp':
			raise asocketError('tcp socket has no attribute sendTo, use send instead', asocketError.programmerError)
		if (type(data) == str or type(data) == unicode) == False:
			raise asocketError('argument to sendTo, data, must be of type str or unicode', asocketError.programmerError)
		if (type(address) == list or type(address) == tuple) == False:
			raise asocketError('argument to sendTo, address, must be of type tuple or list', asocketError.programmerError)
		if len(address) != 2:
			raise asocketError('Address (host, port) tuple must be of length two!', asocketError.programmerError)
		if (type(address[0]) == str or type(address[0]) == unicode) == False:
			raise asocketError('Host in (host, port) tuple must be of type str or unicode', asocketError.programmerError)
		if type(address[1]) != int:
			raise asocketError('Port in (host, port) tuple must be of type int', asocketError.programmerError)

		if data == '':
			return
		self.__outgoingQueue.append((data, address))
		self._doWrite() #- We can do this right now because we know we're UDP and this is non-blocking

	def connect(self, host, port):
		if self.__protocol == 'udp':
			raise asocketError('udp socket has no attribute connect, use sendTo instead', asocketError.programmerError)
		self.__connecting = (host, port)

	def setBroadcast(self):
		if self.__protocol == 'tcp':
			raise asocketError('tcp socket has no attribute setBroadcast', asocketError.programmerError)
		ip = getLocalAddress()
		if ip == None:
			raise asocketError('Unable to detect local IP address via ipconfig or ifconfig')
		self.__localIp = ip
		self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

	def bind(self, host = '', port = 3037):
		try:
			if self.__socket.getsockname()[1] != 0 or self.__bound:
				raise asocketError('Socket already bound! Only call bind once per socket!', asocketError.programmerError)
			self.__socket.bind((host, port))
			if self.__protocol == 'udp':
				pass
			else:
				self.__socket.listen(self.__backlog)
			self.__bound = (host, port)
			self.__connectionQueue = deque()
		except socket.error as i:
			if i.errno == errno.EACCES:
				raise asocketError('Permission denied', asocketError.permissionDenied)
			elif i.errno == errno.EADDRINUSE:
				raise asocketError('Unable to bind port %s, address in use' % port, asocketError.addressInUse)
			else:
				raise

	def get(self):
		try:
			return self.__incomingQueue.popleft()
		except IndexError:
			return None

	def _doConnect(self):
		if self.__connecting:
			ret = self.__socket.connect_ex(self.__connecting)
			if ret == errno.ECONNREFUSED or ret == errno.ETIMEDOUT:
				self.__connected = False
				self.__connecting = None
				self.__unableToConnect = True
			elif ret == errno.EINPROGRESS or ret == errno.EALREADY or ret == errno.EWOULDBLOCK or ret == errno.EINVAL:
				#- Still connecting as we should
				pass
			elif ret == errno.EISCONN or ret == 0:
				self.__connected = True
				self.__connecting = None
				self.__unableToConnect = False

	def _doWrite(self):
		if len(self.__outgoingQueue) > 0:
			data = self.__outgoingQueue.popleft()
			if self.__protocol == 'udp':
				data, address = data
				self.__bytesSent += len(data)
				self.__socket.sendto(data, address)
			elif self.__connected:
				bytesActuallySent = self.__socket.send(data)
				leftOvers = data[bytesActuallySent:]
				if leftOvers:
					self.__outgoingQueue.extendleft([leftOvers])
				self.__bytesSent += bytesActuallySent

		if self.__shuttingDown:
			if len(self.__outgoingQueue) == 0:
				self.close(self.__shuttingDown)
				self.__shuttingDown = ''

	def _doRead(self):
		if self.__connected == False and self.__protocol != 'udp':
			return
		try:
			if self.__protocol == 'udp':
				data, addr = self.__socket.recvfrom(self.__bufferSize)
			else:
				data = self.__socket.recv(self.__bufferSize)
		except socket.error as i:
			if i.errno == errno.ECONNABORTED or i.errno == errno.EBADF:
				self.close('Connection lost')
			elif i.errno == errno.ECONNRESET:
				self.close('Connection reset by peer')
			else:
				raise

		if data:
			if self.__protocol == 'udp':
				useData = True
				if self.__localIp:
					if self.__localIp == addr[0]:
						useData = False #- It's our own UDP packet!
				if useData:
					self.__bytesRead += len(data)
					self.__incomingQueue.append((data, addr))
			else:
				self.__bytesRead += len(data)
				self.__incomingQueue.append(data)
		else: #- It could be an empty TCP message, which sometimes happens when the other end dies, if it is goodbye!
			if self.__broken:
				pass
			else:
				self.close('Connection lost')

	def _setConnected(self):
		self.__connected = True

	def _setIsUnableToConnect(self, value):
		self.__isUnableToConnect = value

	def _doAccept(self):
		if self.__bound == None or self.__protocol == 'udp':
			return
		try:
			cs, ca = self.__socket.accept()
		except socket.error as i:
			raise
		ncs = asocket(protocol = self.__protocol, socketObject = cs, bufferSize = self.__bufferSize, ipv6 = self.__ipv6)
		ncs._setConnected()
		self.__connectionQueue.append(ncs)
		return ncs

	def accept(self):
		if self.__bound == None:
			raise asocketError('Unable to accept connections when socket is non-bound, try using bind first')
		try:
			return self.__connectionQueue.popleft()
		except IndexError:
			return None

	def fileno(self):
		return self.__socket.fileno()

	def close(self, reason = 'Socket closed'):
		self.__socket.close()
		self.__broken = reason
		self.__connected = False

	def shutdown(self, reason = 'Socket shutdown'):
		self.__shuttingDown = reason

	def hasOutgoingData(self):
		return len(self.__outgoingQueue) > 0

	def getSocket(self):
		return self.__socket

	def getAddress(self):
		return self.__socket.getsockname()

	def getPeerAddress(self):
		if self.__connected:
			return self.__socket.getpeername()
		elif self.__connecting:
			return self.__connecting
		else:
			return None

	def isConnected(self):
		return self.__connected

	def isConnecting(self):
		if self.__connecting:
			return True
		else:
			return False

	def isUnableToConnect(self):
		return self.__isUnableToConnect

	def isShuttingDown(self):
		if self.__shuttingDown:
			return True
		else:
			return False

	def isBound(self):
		if self.__bound:
			return True
		else:
			return False

	def getBound(self):
		return self.__bound

	def isBroken(self):
		if self.__broken:
			return True
		else:
			return False

	def getBroken(self):
		return self.__broken


if __name__ == '__main__':
	from asocketManager import *
	handler = socketHandler(backend = 'select')

	myServerSocket = asocket(protocol = 'tcp')
#	myServerSocket.bind(port = 3037)
	myServerSocket.connect('www.google.com', 80)

	handler.addSocket(myServerSocket)
	sentData = False

	while True:
		handler.step()
		data = myServerSocket.get()
		if myServerSocket.isConnecting():
			print 'Connecting..'
		if myServerSocket.isUnableToConnect():
			print 'Unable to connect!'
		if myServerSocket.isConnected() and sentData == False:
			print 'Connected!'
			sentData = True
			myServerSocket.send('GET\r\n')
		if data:
			print 'DATA', repr(data[:160])
			exit()
	#	newClient = myServerSocket.accept()
	#	print newClient.getAddress()

#	import ssl
#	s = asocket(socketObject = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM)))
#	s.bind(port = 3535)
#	s.shutdown()
	'''
	while True:
		try:
			ret = s.getSocket().connect_ex(('www.google.com', 80))
		except Exception as i:
			print i
		if ret == 0: break;
		print ret, errno.errorcode[ret]
#	s.getSocket().recv(1024)
	'''
