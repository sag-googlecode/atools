#!/usr/bin/python -B
# -*- coding: utf-8 -*-
###########################
# | . _ |_ _|_ _  _ |  _  #
# |_|(_|| | | |_)(_)|<(/_ #
#     _|      |           #
###########################
#- Atools, lightSql/mysqlConnector.py provides a MySQLdb-based backend for lightSql/connector.py
# See included "License.txt"

class mysqlConnector:
	def __init__(self, username = 'root', password = '', database = 'lightSql', host = 'localhost', port = 3306):
		self.getSql()
		self.username = username
		self.password = password
		self.database = database
		self.host = host
		self.port = port
		self.cursor = None
		self.db = None

	def getSql(self):
		try:
			import MySQLdb as sql
		except ImportError:
			print "\n#- You must install MySQLdb for python, search google."
			print "#- Or sourceforge website at: \"http://sourceforge.net/projects/mysql-python/\" "
			print "#- Or 'sudo apt-get install python-mysqldb'"
			print "#- Otherwise you're out of luck.\n"
			raise
		return sql

	def setDatabase(self, name):
		sql = self.getSql()
		self.database = name
		try:
			self.getCursor().execute('USE %s;' % name)
			self.getCursor().fetchall()
		except sql.Error as e:
			if e[0] == 1049:
				self.getCursor().execute('CREATE DATABASE %s;' % name)
				self.getCursor().execute('USE %s;' % name)
				self.getCursor().fetchall()
			else:
				raise

	def removeDatabase(self, name):
		sql = self.getSql()
		try:
			self.getCursor().execute('DROP DATABASE %s;' % name)
		except sql.Error as e:
			if e[0] == 1008:
				pass
			else:
				raise

	def execute(self, query, args = ()):
		self.getCursor().execute(query, args)
		return self.getCursor().fetchall()

	def getCursor(self):
		return self.cursor

	def connect(self):
		sql = self.getSql()
		try:
			self.db = sql.connect(user = self.username, passwd = self.password, host = self.host, port = self.port)
			self.cursor = self.db.cursor()
		except sql.Error as e:
			raise
		self.setDatabase(self.database)

	def close(self):
		self.db.close()
		self.db = None
		self.cursor = None
