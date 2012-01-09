#!/usr/bin/python -B
# -*- coding: utf-8 -*-
###########################
# | . _ |_ _|_ _  _ |  _  #
# |_|(_|| | | |_)(_)|<(/_ #
#     _|      |           #
###########################
#- Atools, lightSql/table.py provides a connection to a SQL-based backend
# See included "License.txt"

class sqlType:
	def __init__(self, value, canBeEmpty = False, default = None):
		self.value = value
		if default == None or default == '':
			pass
		else:
			self.value = self.value + ' DEFAULT %s' % default
		if canBeEmpty == False:
			self.value = self.value + ' NOT NULL'

	def __str__(self):
		return '<sqlType "%s" at 0x%s>' % (self.value, id(self))

	def __repr__(self):
		return str(self)

	def toSql(self):
		return self.value

class table:
	def __init__(self, name = None):
		self._inOrder = []
		if name == None:
			self._name = self.getClassName()
		else:
			self._name = name
		self.id = self.getId()
		self._links = []

	def getName(self):
		return self._name

	def getClassName(self):
		name = self.__class__.__name__
		return name

	def getChar(self, size = 255, canBeEmpty = False, default = None):
		assert (size > 0) and (size <= 255), 'Size for charField must 0-255'
		i = sqlType('VARCHAR(%s)' % size, canBeEmpty, default)
		self._inOrder.append(i)
		return i

	def getText(self, canBeEmpty = False, default = None):
		i = sqlType('TEXT', canBeEmpty, default)
		self._inOrder.append(i)
		return i

	def getBlob(self, canBeEmpty = False, default = None):
		i = sqlType('BLOB', canBeEmpty, default)
		self._inOrder.append(i)
		return i

	def getInt(self, canBeEmpty = False, default = None):
		i = sqlType('INT', canBeEmpty, default)
		self._inOrder.append(i)
		return i

	def getFloat(self, canBeEmpty = False, default = None):
		i = sqlType('DOUBLE', canBeEmpty, default)
		self._inOrder.append(i)
		return i

	def getBool(self, canBeEmpty = False, default = 0):
		i = sqlType('TINYINT(1)', canBeEmpty, default)
		self._inOrder.append(i)
		return i

	def getId(self, canBeEmpty = False):
		i = sqlType('INT AUTO_INCREMENT PRIMARY KEY', canBeEmpty)
		self._inOrder.append(i)
		return i

	def getLink(self, otherEnd, canBeEmpty = False):
		i = sqlType('INT', canBeEmpty)
		self._inOrder.append(i)
		self._links.append((otherEnd, i))
		return i

	def __str__(self):
		return self.toSql()

	def toSql(self):
		query = 'CREATE TABLE %s (' % self._name

		itemNames = {}
		for i in dir(self):
			item = getattr(self, i)
			if hasattr(item, '__class__'):
				if item.__class__ == sqlType:
					itemNames[item] = i

		new = []
		for pos, item in enumerate(self._inOrder):
			if item in itemNames:
				itemName = itemNames[item]
				query += '%s %s, ' % (itemName, item.toSql())
				new.append(item)
		self._inOrder = new
		query = query.rstrip(', ')

		for pos, i in enumerate(self._links):
			otherEnd, item = i
			query += ', FOREIGN KEY(%s) REFERENCES %s(id), ' % (itemNames[item], otherEnd._name)
		query = query.rstrip(', ')
		query += ');'
		return query


if __name__ == '__main__':
	class userTable(table):
		def __init__(self):
			table.__init__(self)
			self.id = self.getId()
			self.username = self.getChar(size=25)
			self.password = self.getChar(size=25)
			self.level = self.getInt()
			self.experience = self.getInt()
			self.bio = self.getChar(size=255)

	print userTable()

