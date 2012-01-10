#!/usr/bin/python -B
# -*- coding: utf-8 -*-
###########################
# | . _ |_ _|_ _  _ |  _  #
# |_|(_|| | | |_)(_)|<(/_ #
#     _|      |           #
###########################
#- Atools, chunkSplitter.py allows you to pack strings in a way suck that they can be unpacked into chunks
# See included "License.txt"
from Queue import deque
import struct

#- Each chunkPacket will use 2 bytes (short int) to store it's chunk size, meaning a 2 byte overhead for each data chunk
class chunkPacket:
	def __init__(self, data):
		self.__data = data

	def __str__(self):
		return repr(self)

	def __repr__(self):
		return '<chunkPacket %s bytes at %s>' % (self.size(), hex(id(self)))

	def packedSize(self):
		return struct.pack('!h', len(self.__data))

	def packedData(self):
		return struct.pack('!%ss' % len(self.__data), self.__data)

	def get(self):
		return self.packedSize() + self.packedData()

	def data(self):
		return self.__data

	def size(self):
		return len(self.__data)


class chunkSplitter(deque):
	shortSize = struct.calcsize('!h')
	def __init__(self):
		deque.__init__(self)
		self.__buffer = str()

	def get(self):
		try:
			return self.popleft()
		except IndexError:
			return None

	def __str__(self):
		return repr(self)

	def __repr__(self):
		return str(list(self))

	def feed(self, data):
		assert type(data) == str or type(data) == unicode
		self.__buffer += data
		if len(self.__buffer) > self.shortSize:
			size = self.__buffer[:self.shortSize]
			try:
				parsedSize = struct.unpack('!h', size)[0]
			except Exception as i:
				print ':chunkSplitter: Error unpacking data (short size).. ignoring..'
				parsedSize = None
			if parsedSize:
				rest = data[self.shortSize:]
				if len(rest) >= parsedSize:
					try:
						parsedData = struct.unpack('!' + str(parsedSize) + 's', rest[:parsedSize])[0]
					except Exception as i:
						print ':chunkSplitter: Error unpacking data (actual data).. ignoring..'
						parsedData  = None
					if parsedData:
						self.append(parsedData)
						self.__buffer = rest[parsedSize:]


if __name__ == '__main__':
	b = chunkSplitter()
	packet = chunkPacket('Hello World!')
	print 'packet:', packet
	print 'size, data:', packet.size(), packet.data()
	b.feed(chunkPacket('Hello World!').get())
	b.feed(chunkPacket('Hello Mars!').get())
	b.feed(chunkPacket('Hello Moon!').get())

	print b.get(), b.get(), b.get()
