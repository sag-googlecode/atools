import subprocess
import sys
import re

ip_prog = re.compile(r'\d+\.\d+\.\d+\.\d+')
def getLocalAddress(first = True):
	if sys.platform.startswith('win'):
		command = 'ipconfig'
	else:
		command = 'ifconfig'
	proc = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
	proc.wait()
	output = proc.stdout.read()
	addresses = ip_prog.findall(output)

	if first == True and len(addresses) > 0:
		return addresses[0]
	else:
		return addresses

if __name__ == '__main__':
	print getLocalAddress(first = False)
	print getLocalAddress()

