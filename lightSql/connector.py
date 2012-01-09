#!/usr/bin/python -B
# -*- coding: utf-8 -*-
###########################
# | . _ |_ _|_ _  _ |  _  #
# |_|(_|| | | |_)(_)|<(/_ #
#     _|      |           #
###########################
#- Atools, lightSql/connector.py provides a connection to a SQL-based backend
# See included "License.txt"
from mysqlConnector import mysqlConnector

class connectorError:
	connectionError = 0
	def __init__(self, error, code):
		self.error = error
		self.code = code

class connector:
	def __init__(self, backend = 'mysql', **backendKwargs):
		assert backend == 'mysql', 'Backend must match one of: "mysql"'
		if backend == 'mysql':
			self.backend = mysqlConnector(**backendKwargs)

	def installTable(self, table = None):
		if type(table) == list or type(table) == tuple:
			tables = table
		else:
			tables = [table]
		for t in tables:
			self.ensureTable(t.toSql())

	def ensureTable(self, tableQuery):
		name = tableQuery.split(' ')[2]
		rows = self.execute('show tables like "%s";' % name)
		if len(rows) == 0:
			self.execute(tableQuery)

	def execute(self, query, args = ()):
		return self.backend.execute(query, args)

	def connect(self):
		try:
			self.backend.connect()
		except Exception as i:
			raise connectorError(str(i), connectorError.connectionError)

	def close(self):
		self.backend.close()


if __name__ == '__main__':
	con = connector(backend='mysql', username="root", password="", database="lightSql", host="localhost", port=3306)
	try:
		con.connect()
	except connectorError as i:
		if i.code == connectorError.connectionError:
			print 'Unable to connect:', i.error
			exit()
	print 'Connected through backend!'
	print con.execute('show tables;')
