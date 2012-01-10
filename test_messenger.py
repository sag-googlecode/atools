#!/usr/bin/python -B
# -*- coding: utf-8 -*-
###########################
# | . _ |_ _|_ _  _ |  _  #
# |_|(_|| | | |_)(_)|<(/_ #
#     _|      |           #
###########################
#- Atools, test_messenger.py shows example usage of using atools/layeredMessenger to send messages inside of your application to other parts of it
# See included "License.txt"
from atools import *

#- Create a keep a reference to the global layeredMessenger object
messenger = layeredMessenger()

#- Get a child, children of the messenger can send/recieve events
a = messenger.child()

#- Define a 
def this(arg1, arg2):
	print 'THIS!'
	print arg1, arg2

#- Accept an event called 'callme' and 'callme2', on these 
a.accept('callme', this)
a.accept('callme2', this)

#- Ignore an event called 'callme2', on this child
a.ignore('callme2')


#- Get a child, children of the messenger can send/recieve events
b = messenger.child()

#- Send an event, with arguments, to other children of the messenger listening for the event
b.send('callme', ['hello', 'world'])
b.send('callme2', ['hello', 'world'])

