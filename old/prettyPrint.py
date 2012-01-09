#! /usr/bin/python
# -*- coding: utf-8 -*-
###########################
# | . _ |_ _|_ _  _ |  _  #
# |_|(_|| | | |_)(_)|<(/_ #
#     _|      |           #
###########################
#- Atools, prettyPrint.py provides a way to print to terminal in color (only on unix based terminal's)
# See included "License.txt"
import sys

if sys.platform == 'win32':
	red = ''
	green = ''
	blue = ''
	bold = ''
	faint = ''
	reset = ''
	dead = ''
else:
	red = '\033[91m'
	green = '\033[92m'
	blue = '\033[34m'
	bold = '\033[1m'
	faint = '\033[2m'
	reset = '\033[0m'
	dead = '\033[5m'


def prettyPrint(msg):
	msg = msg.replace('<green>', green)
	msg = msg.replace('</green>', reset)

	msg = msg.replace('<blue>', blue)
	msg = msg.replace('</blue>', reset)

	msg = msg.replace('<red>', red)
	msg = msg.replace('</red>', reset)

	msg = msg.replace('<bold>', bold)
	msg = msg.replace('</bold>', reset)

	print msg + reset


if __name__ == '__main__':
	prettyPrint('<green> green </green> <bold><green> bold green </bold></green> blanko')
	prettyPrint('<blue> green </blue> <bold><blue> bold green </bold></blue> blanko')
	prettyPrint('<red> green </red> <bold><red> bold green </bold></red> blanko')

