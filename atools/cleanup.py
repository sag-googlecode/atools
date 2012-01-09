#!/usr/bin/python -B
# -*- coding: utf-8 -*-
###########################
# | . _ |_ _|_ _  _ |  _  #
# |_|(_|| | | |_)(_)|<(/_ #
#     _|      |           #
###########################
#- Atools, cleanup.py provides a command-line interface to remove the current directory and any
#- sub directories of .pyc files, and (gedit) ~ files. It's a cleanup script.
# See included "License.txt"
from glob import glob
from os.path import isdir
from os import remove

check = [
		'.pyc',
		'~',
		]

def cleanup(path):
	for i in check:
		if path.endswith(i):
			#print 'Removing %s' % path
			remove(path)

def cleanDir(path):
	for i in glob(path):
		if isdir(i):
			cleanDir('%s/*' % i)
		else:
			cleanup(i)

cleanDir('./*')
print '::::: ./* and all sub-directories have been cleaned.'
for i in check:
	print '::::: Cleaned of: %s' % i
