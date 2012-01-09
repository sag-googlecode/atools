#!/usr/bin/python -B
# -*- coding: utf-8 -*-
###########################
# | . _ |_ _|_ _  _ |  _  #
# |_|(_|| | | |_)(_)|<(/_ #
#     _|      |           #
###########################
#- Atools, hashRing.py provides a hash ring modified from http://amix.dk/blog/post/19367
# See included "License.txt"
from hashlib import md5

class hashRing():
	def __init__(self, nodes = None, replicas = 3):
		"""
		`nodes` is a list of objects that have a proper __str__ representation.
		`replicas` indicates how many virtual points should be used pr. node,
		replicas are required to improve the distribution.
		"""
		self.replicas = replicas

		self.ring = dict()
		self._sorted_keys = []

		if nodes:
			for node in nodes:
				self.addNode(node)

	def addNode(self, node):
		"""Adds a `node` to the hash ring (including a number of replicas).
		"""
		for i in xrange(0, self.replicas):
			key = self.genKey('%s:%s' % (node, i))
			self.ring[key] = node
			self._sorted_keys.append(key)
		self._sorted_keys.sort()

	def removeNode(self, node):
		"""Removes `node` from the hash ring and its replicas.
		"""
		for i in xrange(0, self.replicas):
			key = self.genKey('%s:%s' % (node, i))
			del self.ring[key]
			self._sorted_keys.remove(key)

	def getNode(self, key):
		"""Given a string key a corresponding node in the hash ring is returned.

		If the hash ring is empty, `None` is returned.
		"""
		return self.getNodePos(key)[0]

	def getNodePos(self, key):
		"""Given a string key a corresponding node in the hash ring is returned
		along with it's position in the ring.

		If the hash ring is empty, (`None`, `None`) is returned.
		"""
		if not self.ring:
			return None, None

		key = self.genKey(key)

		nodes = self._sorted_keys
		for i in xrange(0, len(nodes)):
			node = nodes[i]
			if key <= node:
				return self.ring[node], i

		return self.ring[nodes[0]], 0

	
	def getNodes(self, key):
		"""Given a string key it returns the nodes as a generator that can hold the key.

		The generator is never ending and iterates through the ring
		starting at the correct position.
		"""
		if not self.ring:
			yield None, None

		node, pos = self.get_node_pos(key)
		for key in self._sorted_keys[pos:]:
			yield self.ring[key]

		while True:
			for key in self._sorted_keys:
				yield self.ring[key]

	def genKey(self, key):
		"""Given a string key it returns a long value,
		this long value represents a place on the hash ring.

		md5 is currently used because it mixes well.
		"""
		m = md5()
		m.update(key)
		return long(m.hexdigest(), 16)

if __name__ == '__main__':
	h = hashRing()
	for i in range(500):
		h.addNode('my.serv.ip%s' % i)
	print h.getNode('my.client.ip1')
	print h.getNode('my.client.ip2')
	print h.getNode('my.client.ip3')
	print h.getNode('my.client.ip4')
	print h.getNode('my.client.ip5')

