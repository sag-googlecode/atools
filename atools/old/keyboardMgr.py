#!/usr/bin/python
###########################
# | . _ |_ _|_ _  _ |  _  #
# |_|(_|| | | |_)(_)|<(/_ #
#     _|      |           #
###########################
#- Atools, keyboardMgr.py provides a pure non-blocking cross-platform way to read the console
#- keyboard input. It should work in most *nix terminals, mainly tested in Bash and on windows
# See included "License.txt"
import sys, os
from select import select
if sys.platform.startswith('win'):
	import msvcrt
else:
	import termios
	import tty

def getTerminalSize():
	if sys.platform.startswith('win'):
		from ctypes import windll, create_string_buffer
		h = windll.kernel32.GetStdHandle(-12)
		csbi = create_string_buffer(22)
		res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)

		#return default size if actual size can't be determined
		if not res: return 80, 25 

		import struct
		(bufx, bufy, curx, cury, wattr, left, top, right, bottom, maxx, maxy)\
		= struct.unpack("hhhhHhhhhhh", csbi.raw)
		width = right - left + 1
		height = bottom - top + 1

		return width, height
	else: #- Odds are it's posix
		#- Non supported? hmm
		try:
			width = os.popen('tput cols', 'r').readline()
			height = os.popen('tput lines', 'r').readline()
			return int(width), int(height)
		except:
			return (80, 24)

class keyboardMgr:
	def __init__(self, lines = True):
		self.lines = lines
		self.ready = False
		self.buffer = ''

	def clearLine(self):
		x = getTerminalSize()[0]
		sys.stdout.write('\b' * x)
		sys.stdout.write(' ' * x)
		sys.stdout.write('\n')
		sys.stdout.flush()

	def clearScreen(self):
		x, y = getTerminalSize()
		sys.stdout.write('\b' * x * y)
		sys.stdout.write(' ' * x * y)
		sys.stdout.write('\n')
		sys.stdout.flush()

	def step(self):
		char = ''
		if sys.platform.startswith('win'):
			if msvcrt.kbhit():
				char = msvcrt.getch()
		else:
			oldSettings = termios.tcgetattr(sys.stdin)
			try:
				tty.setcbreak(sys.stdin.fileno())
				read, write, error = select([sys.stdin], [], [], 0)
				if read:
					char = sys.stdin.read(1)
					sys.stdout.write(char)
					sys.stdout.flush()
			finally:
				termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldSettings)

		self.buffer += char
		if self.lines:
			if char == '\n' or char == '\r':
				self.ready = True
		else:
			self.ready = True

	def get(self):
		if self.ready:
			cp = str(self.buffer)
			self.ready = False
			self.buffer = ''
			return cp
		else:
			return ''


if __name__ == '__main__':
	mgr = keyboardMgr()
	while True:
		mgr.step()
		line = mgr.get()
		if line:
			if line == 'clear\n':
				mgr.clearLine()
			elif line == 'cs\n':
				mgr.clearScreen()
			else:
				print repr(line)
