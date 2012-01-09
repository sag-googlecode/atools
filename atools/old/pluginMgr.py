#! /usr/bin/python
###########################
# | . _ |_ _|_ _  _ |  _  #
# |_|(_|| | | |_)(_)|<(/_ #
#     _|      |           #
###########################
#- Atools, pluginMgr.py provides a way to load a folder of python modules as plugins
# See included "License.txt"
import inspect
import sys
import glob
import os

def myImport(name):
	mod = __import__(name)
	components = name.split('.')
	for comp in components[1:]:
		mod = getattr(mod, comp)
	reload(mod)
	return mod

class pluginMgr:
	def __init__(self, folder, panda3d = False, gb = None, log = None):
		self.panda3d = panda3d
		if panda3d:
			if base.appRunner:
				from direct.stdpy import file as pfile #file._vfs import isDirectory
				self.isdir = pfile._vfs.isDirectory
				folder = '/mf/' + folder
			else:
				self.isdir = os.path.isdir
		else:
			self.isdir = os.path.isdir

		if gb == None:
			self.gb = inspect.stack()[1][0].f_builtins
		else:
			self.gb = gb

		if log:
			self.log = log
		else:
			self.log = self.prnt

		self.folder = folder
		self.loaded = []
		self.loadFolder(folder)
		self.load()

	def prnt(self, msg):
		print msg

	def getLoaded(self):
		return self.loaded

	def loadFolder(self, path):
		modulePaths = []
		for f in glob.glob(path + '/*'):
			ptm = f.replace('/', '.')
			if self.panda3d:
				if base.appRunner:
					ptm = ptm[len('.mf.'):]

			if '__init__' in ptm:
				continue
			# no __init__ files

			# strip the ending .something from the path to module
			place = 1
			for c in reversed(ptm):
				if c == '.':
					break
				else:
					place += 1
			ptm = ptm[:-place]
			# ptm now has no ending .something

			modulePaths.append(ptm)

		# Remove duplicates
		modulePaths = set(modulePaths)

		for ptm in modulePaths:
			try:
				tmp = myImport(ptm)
			except Exception as i:
				self.log('pluginMgr -> [%s] -> ' % i + ptm)
				continue
			for k in self.gb:
				tmp.__builtins__[k] = self.gb[k]
			if self.panda3d:
				if base.appRunner:
					tmp.dataKey = 'p_' + ptm[len(path[len('/mf/'):])+1:]
				else:
					tmp.dataKey = 'p_' + ptm[len(path)+1:]
			else:
				tmp.dataKey = 'p_' + ptm[len(path)+1:]
			tmp.ptm = ptm
			tmp.path = path
			self.loaded.append(tmp)

	def load(self):
		for plug in self.loaded:
			try:
				plug.load()
				self.log('pluginMgr -> [Loaded] -> ' + plug.ptm)
			except Exception as i:
				self.log('pluginMgr -> Fail[%s] -> ' % i + plug.ptm)

	def unload(self):
		for plug in self.loaded:
			try:
				plug.unload()
				self.log('pluginMgr -> [Unloaded] -> ' + plug.ptm)
				del plug
			except Exception as i:
				self.log('pluginMgr -> Fail[%s] -> ' % i + plug.ptm)
		self.loaded = []

	def restart(self):
		self.unload()
		self.loadFolder(self.folder)
		self.load()

if __name__ == '__main__':
	import time
	plugins = pluginMgr('plugins')
	print 'Plugins should be OK. Wait 10 secs.'
	time.sleep(10)
	plugins.restart()
	print 'Plugins should have unloaded and loaded again'
