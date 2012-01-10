#!/usr/bin/python -B
# -*- coding: utf-8 -*-
###########################
# | . _ |_ _|_ _  _ |  _  #
# |_|(_|| | | |_)(_)|<(/_ #
#     _|      |           #
###########################
#- Atools, test_taskMgr.py shows example usage of using atools/taskManager to help ease development
# See included "License.txt"
from atools import *
import conf

#- We need to create, and keep reference to the global taskManager
taskMgr = taskManager()

#- Here we make a simple task, all tasks take in one argument, 'task'
#- The task should return one of the following:
#- task.cont, the task will continue to run from here-on-out each frame
#- task.again, the task will be removed, and added again with the same initial paramaters
#- task.done (also None), the task is finished, and will be removed right away
def this(task):
	print 'THIS!'
	return task.again

#- Add the task to run each frame, also pass in a task name
#taskMgr.add(this, 'this')
#- Add the task to run every 5.0 seconds, also pass in a task name
taskMgr.doMethodLater(5.0, this, 'this')

print 'Wait five seconds..'

#- The main loop, simply call taskMgr.step each frame or iteration
while True:
	taskMgr.step()
