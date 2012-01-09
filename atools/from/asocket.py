#! /usr/bin/python
# -*- coding: utf-8 -*-
###########################
# | . _ |_ _|_ _  _ |  _  #
# |_|(_|| | | |_)(_)|<(/_ #
#     _|      |           #
###########################
#- Atools, asocket.py provides a non-blocking TCP and UDP socket with multicast support
# See included "License.txt"

from Queue import deque
from errno import *
from sys import exit
import socket
import sys
import os


def getLocalIps():
	if sys.platform.startswith('win'):
		command = 'ipconfig'
		windows = True
	elif 'lin' in sys.platform:
		command = '/sbin/ifconfig'
		windows = False
	else:
		command = 'ifconfig'
		windows = False

	text = os.popen(command).read()
	ips = []
	for line in text.splitlines():
		if windows:
			pass
		else:
			if ('inet' in line) and ('inet6' not in line):
				line = line[line.index(':')+1:]
				line = line[:line.index(' ')]
				if line == '127.0.0.1':
					pass
				else:
					ips.append(line)

	if len(ips) > 0:
		return ips
	else:
		return None


def getLocalIp():
	ips = getLocalIps()
	if ips:
		return ips[0]
	else:
		return None


def requireLocalIp():
	ip = getLocalIp()
	if ip:
		return ip
	else:
		print 'Unable to detect local IP address, will now exit'
		exit()


def getAddressByName(name = 'localhost'):
	l = socket.gethostbyname_ex(name)[2]
	return list(set(l))


class asocketError(Exception):
	programmerError = 0
	addressInUse = 1
	permissionDenied = 2
	maxFilesError = 3
	def __init__(self, text, value):
		self.__text = text
		self.__value = value

	def getValue(self):
		return self.__value

	def __str__(self):
		return str(self.__text)

	def __repr__(self):
		return repr(self.__text)


class asocket:
	def __init__(self, protocol = 'tcp', bufferSize = 1024, ipv6 = False, socketObject = None, address = None):
		self.__protocol = protocol
		self.__socket = socketObject
		self.__address = address
		self.__bufferSize = bufferSize
		self.__ipv6 = ipv6

		self._outgoingQueue = deque()
		self._incomingQueue = deque()
		self._connectionQueue = deque()
		self._bytesSent = 0
		self._bytesRead = 0
		self.__connected = False
		self.__bound = False
		self._doingConnect = None
		self._unableToConnect = ''
		self._connected = False
		self.__shuttingDown = False
		self.__boundPort = None
		self._localIp = None
		self._broken = None

		if self.__socket == None:
			try:
				assert self.__protocol == 'tcp' or self.__protocol == 'udp'
			except AssertionError:
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
		if type(data) == str or type(data) == unicode:
			self._outgoingQueue.append(data)
		else:
			raise asocketError('argument to send, data, must be of type str or unicode', asocketError.programmerError)

	def sendTo(self, data, address):
		if self.__protocol == 'tcp':
			raise asocketError('tcp socket has no attribute sendTo, use send instead', asocketError.programmerError)
		if type(data) == str or type(data) == unicode:
			if type(address) == list or type(address) == tuple:
				if len(address) == 2:
					if type(address[0]) == str or type(address[0]) == unicode:
						if type(address[1]) == int:
							#- Success!
							pass
						else:
							raise asocketError('Port in (host, port) tuple must be of type int', asocketError.programmerError)
					else:
						raise asocketError('Host in (host, port) tuple must be of type str or unicode', asocketError.programmerError)
				else:
					raise asocketError('Address (host, port) tuple must be of length two!', asocketError.programmerError)
			else:
				raise asocketError('argument to sendTo, address, must be of type tuple or list', asocketError.programmerError)
		else:
			raise asocketError('argument to sendTo, data, must be of type str or unicode', asocketError.programmerError)

		#- If success..
		self._outgoingQueue.append((data, address))

	def connect(self, host, port, timeout = False):
		if self.__protocol == 'udp':
			raise asocketError('udp socket has no attribute connect, use sendTo instead', asocketError.programmerError)
		if timeout == False:
			self.__socket.setblocking(False)
		else:
			self.__socket.settimeout(timeout)
		self._doingConnect = (host, port)
		self._unableToConnect = ''
		self.__address = (host, port)

	def setBroadcast(self):
		if self.__protocol == 'tcp':
			raise asocketError('tcp socket has no attribute setBroadcast', asocketError.programmerError)
		self._localIp = requireLocalIp()
		self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

	def bind(self, host = '', port = 3037):
		try:
			self.__socket.bind((host, port))
			self.__bound = True
			self.__boundPort = port
		except Exception as i:
			if i.errno == EADDRINUSE:
				raise asocketError('Unable to bind port %s, address in use' % port, asocketError.addressInUse)
			elif i.errno == EACCES:
				raise asocketError('Permission denied', asocketError.permissionDenied)
			elif i.errno == EINVAL:
				raise asocketError('You must call bind(), then listen() and in that order only.', asocketError.programmerError)
			else:
				print 'asocket::unknown error, uncought bind code:', i.errno, errorcode[i.errno]

	def listen(self, backlog=5):
		if self.__protocol == 'udp':
			raise asocketError('udp socket has no attribute listen, use sendTo instead', asocketError.programmerError)
		self.__socket.listen(backlog)

	def get(self):
		#FIXME!! FIXME FIXME!
		#add support for (data, address) udp packets!
		try:
			return self._incomingQueue.popleft()
		except IndexError:
			return None

	def accept(self):
		try:
			return self._connectionQueue.popleft()
		except IndexError:
			return None

	def close(self, reason = 'Socket closed'):
		self.__socket.close()
		self._broken = reason

	def fileno(self):
		return self.__socket.fileno()

	def shutdown(self):
		self.__shuttingDown = True

	def isConnected(self):
		return self._connected

	def isBound(self):
		return self.__bound

	def isShuttingDown(self):
		return self.__shuttingDown

	def getPeerName(self):
		return self.__socket.getpeername()

	def getBoundPort(self):
		return self.__boundPort

	def getSocket(self):
		return self.__socket

	def getAddress(self):
		return self.__address

	def getIpv6(self):
		return self.__ipv6

	def getBufferSize(self):
		return self.__bufferSize

	def getProtocol(self):
		return self.__protocol

	def getBytesSent(self):
		return self._bytesSent

	def getBytesRead(self):
		return self._bytesRead

	def getBroken(self):
		return self._broken

	def getUnableToConnect(self):
		return self._unableToConnect
