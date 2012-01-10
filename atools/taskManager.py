#!/usr/bin/python -B
# -*- coding: utf-8 -*-
###########################
# | . _ |_ _|_ _  _ |  _  #
# |_|(_|| | | |_)(_)|<(/_ #
#     _|      |           #
###########################
#- Atools, taskMgr.py can manage several "tasks" which can be thought of as non-blocking individual loops, or as
#- functions that run every _blank_ frames-per-second
# See included "License.txt"
import time


class task:
	done = None
	cont = 1
	again = 2
	def __init__(self, time, method, extraArgs, sort):
		self.runningTime = 0
		self.time = time
		self.method = method
		self.extraArgs = extraArgs
		self.sort = sort


class taskManager:
	def __init__(self):
		self.tasklets = {}
		self.lastTime = time.time()

	def add(self, method, taskName, extraArgs = (), sort = 0):
		time = 0
		self.tasklets[taskName] = task(time, method, extraArgs, sort)

	def doMethodLater(self, time, method, taskName, extraArgs = (), sort = 0):
		self.tasklets[taskName] = task(time, method, extraArgs, sort)

	def step(self):
		newTime = time.time()
		elapsedTime = newTime - self.lastTime
		for taskName, task in self.tasklets.items():
			#- Call this task RIGHT now
			called = False
			if task.time <= 0:
				ret = task.method(*(task,) + task.extraArgs)
				called = True
			else:
				task.runningTime += elapsedTime
				if task.runningTime >= task.time:
					ret = task.method(*(task,) + task.extraArgs)
					called = True

			if called:
				if ret == task.cont:
					#- The task is still running
					#- task.cont is only returned for non-doMethodLater tasks
					#- so in the event that a doMethodLater task returns task.cont
					#- it will continue to run.. each frame
					#- otherwise you should have returned task.again
					task.time = 0 #- Assign the time to 0 that way it run's each frame
				elif ret == task.again:
					#- The task should be stop then started
					self.remove(taskName) #- Remove it
					self.doMethodLater(task.time, task.method, taskName, task.extraArgs, task.sort) #- Add it
				elif ret == task.done:
					#- The task is finished, kill it
					self.remove(taskName)
				else:
					raise Exception('Task "%s" must return task.cont, task.again, or task.done / None' % taskName)
		self.lastTime = newTime

	def remove(self, taskName):
		if taskName in self.tasklets:
			del self.tasklets[taskName]

	def removeAll(self):
		self.tasklets = {}


if __name__ == '__main__':
	taskMgr = taskManager()
	def this(task):
		print 'THIS!'
		return task.again
	taskMgr.add(this, 'this')
	taskMgr.doMethodLater(5.0, this, 'this')
	
	while True:
		taskMgr.step()
