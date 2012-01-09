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

We appreciate feedback,
The Lightpoke team, www.lightpoke.com
