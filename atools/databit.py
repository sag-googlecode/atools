#!/usr/bin/python -B
# -*- coding: utf-8 -*-
###########################
# | . _ |_ _|_ _  _ |  _  #
# |_|(_|| | | |_)(_)|<(/_ #
#     _|      |           #
###########################
#- Atools, databit.py provides a way to convert simple tree lists to strings and back
# See included "License.txt"
from string import digits
import zlib

databitCompression = False
def setDatabitCompression(value):
	global databitCompression
	databitCompression = value

def getDatabitCompression():
	return databitCompression

setDatabitCompression(True)


class databit(list):
	def __init__(self, itemList = [], compress = None):
		if compress == None:
			compress = databitCompression
		self.compress = compress
		list.__init__(self, itemList)
		self.unpack = False
		if type(itemList) == str:
			self.unload(itemList)
			self.unpack = True

	def get(self):
		data = ''
		for i in self:
			data += '¥'
			if type(i) == bool:
				if i is True:
					data += '1✧1'
				else:
					data += '1✧0'
			elif type(i) == int:
				data += '2✧' + str(i)
			elif type(i) == float:
				data += '3✧' + str(i)
			elif type(i) == list:
				data += '4✧' + databit(i).get().replace('¥', '*-yEn-*')
			else:
				data += '5✧' + i.replace('¥', '*-yEn-*')
		if self.compress:
			data = zlib.compress(data, 9)
		return data

	def unload(self, data):
		if self.compress:
			data = zlib.decompress(data)
		l = []
		for peice in data.split('¥'):
			if peice:
			#	print peice, peice[4:]
				if peice.startswith('1'):
					if peice[4] == '0':
						item = False
					elif peice[4] == '1':
						item = True
				elif peice.startswith('2'):
					item = int(peice[4:])
				elif peice.startswith('3'):
					item = float(peice[4:])
				elif peice.startswith('4'):
					item = databit(peice[4:].replace('*-yEn-*', '¥'))
				elif peice.startswith('5'):
					item = str(peice[4:]).replace('*-yEn-*', '¥')
				else:
					raise Exception('Uknown identifier "%s", corrupt data' % repr(peice))
				l.append(item)

		self.__init__(l, self.compress)


if __name__ == '__main__':
	print databit(databit(['This', 'is', 'a', 'databit', 'test', True, False, 0.00000003037, 3037]).get())
	two = databit([
				['hi', 1, 2, 3],
				['ih', 3, 2, 1, '¥', '¥', '¥¥¥¥¥¥¥¥¥¥¥¥¥¥¥¥¥'],
				])
	print databit(two.get())
	print databit(databit([False]).get())
