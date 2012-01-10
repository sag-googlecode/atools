Thank you for downloading atools, the non-blocking python socket library!

Visit our google code project at:
	http://code.google.com/p/atools/

See the license:
	License.txt

Why is there no setup script?
	Atools is meant to be a small and simple library, it's written in pure python for this reason exactly
	We highly advise that you simply copy the subfolder "atools" into your project's root directory
	From there, you can simply use "from atools import *" and be done.

	If you find this inconvienant, feel free to hit us up with a message and we might supply a setup script.
	We avoided supplying one as atools consistantly has a changing API, things are consistantly getting better
	and we thought that having atools installed to your system -- May cause version mismatches a ton.
	Instead we recommend that you ship the version of atools your program is built against with your program.

Why does lightSql use the python-mysql module?
	As it is, the MYSQL protocol is actually changing all the time, and so they reccomend that nobody use
	their own implimentation of the protocol, and instead use the one they've already implimented in C.

	This however does bring up issues for Python developers sometimes, this means that mysql can only be
	used on machines where the mysql module is installed, and that this part is less portable, since it's
	compiled into machine code.

	At one point we had planned to impliment the MYSQL-protocol ourselves, however considering that it's
	always changing, we figgured this would bring in version issues, lightSql would be tied to only one
	version of MYSQL, bad things would happen.

Why am I being limited to around 1000 open sockets (file descriptors)?
	It could be one of these:
		You OS has an per-process limit of how many file descriptors can be open.
		You're using the select backend, which can only handle about 1024 sockets.

	To fix these:
		OS limit:
			atools/asocket provides a way to set the OS limit of number of files open
			used as such:

			"from atools import *"
			"asocket.setMaxFiles(60000, silent = True)"

			65536 is the maximum possible, however you may only be allowed to change the limit
			to a certain amount (on my machine I can only go to 4096) without having root or admin
			priviledges, if this is the case, it will raise an exception.
			If silent is True (default) no exception will be raised, it will be printed.
			If silent is False, the exception will be raised.

			Warning: Your OS also needs file descriptors open too, if you use all of them,
			other programs might crash. I would advice leaving your OS plenty.
			For this reason, I would just round the number off, and use 60,000 as a max.

		Backend limits:
			Make sure you're using a backend other than select, since it can only handle about 1024 sockets.
			Use either poll, or epoll, depending on what's available


We appreciate feedback,
The Lightpoke team, www.lightpoke.com
