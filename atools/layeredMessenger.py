#!/usr/bin/python -B
# -*- coding: utf-8 -*-
###########################
# | . _ |_ _|_ _  _ |  _  #
# |_|(_|| | | |_)(_)|<(/_ #
#     _|      |           #
###########################
#- Atools, layeredMessenger.py provides a basic messenger for sending/recieving messages within the core of your program
# See included "License.txt"

class childMessenger:
	def __init__(self, parent):
		self.parent = parent
		self.boundEvents = {}

	def accept(self, name, command):
		self.boundEvents[name] = command
		if name in self.parent.events:
			self.parent.events[name].append(command)
		else:
			self.parent.events[name] = []
			self.parent.events[name].append(command)

	def send(self, name, args = []):
		if name in self.parent.events:
			for command in self.parent.events[name]:
				command(*args)
				#self.doCallback(command, args)

	def ignore(self, name):
		if name in self.boundEvents:
			command = self.boundEvents[name]
			if command in self.parent.events[name]:
				self.parent.events[name].remove(command)

	def ignoreAll(self):
		for name in self.boundEvents:
			command = self.boundEvents[name]
			if name in self.parent.events:
				if command in self.parent.events[name]:
					self.parent.events[name].remove(command)


class layeredMessenger:
	def __init__(self):
		self.events = {}

	def child(self):
		return childMessenger(self)


if __name__ == '__main__':
	messenger = layeredMessenger()

	a = messenger.child()
	def this(arg1, arg2):
		print 'THIS!'
		print arg1, arg2
	a.accept('callme', this)

	a.accept('callme2', this)
	a.ignore('callme2')


	b = messenger.child()
	b.send('callme', ['hello', 'world'])
	b.send('callme2', ['hello', 'world'])

