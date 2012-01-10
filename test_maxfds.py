#!/usr/bin/python -B
# -*- coding: utf-8 -*-
###########################
# | . _ |_ _|_ _  _ |  _  #
# |_|(_|| | | |_)(_)|<(/_ #
#     _|      |           #
###########################
#- Atools, test_maxfds.py is simply to test the OS imposed limit of maximum file descriptors that can
#- be open at the same time. There are several articles about this on the internet.
#- Look at Readme.txt to see how to raise it above the OS imposed limit.
# See included "License.txt"
from atools import *

print 'Warning: this test will open 60,000 files, this should be okay if your machine is fast'
if raw_input('Continue? [y/n]: ') != 'y':
	exit()

try:
	asocket.setMaxFiles(60000, silent = False)
except asocket.error as i:
	print i
	print 'You need to run this script as root or admin'
	exit()


openFiles = []
while True:
	try:
		print len(openFiles)
		openFiles.append(open('test_maxfds.py', 'r'))
	except Exception as i:
		print i
		print 'Open files:', len(openFiles)
		break
