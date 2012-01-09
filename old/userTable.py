from lightSql import *
import hashlib
import string

class error:
	banned = 0
	usernameTooLong = 1
	usernameTooShort = 2
	passwordTooLong = 3
	passwordTooShort = 4
	emailTooLong = 5
	emailTooShort = 6
	usernameBadCharacters = 7
	passwordBadCharacters = 8
	emailBadCharacters = 9
	usernameTaken = 10
	emailTaken = 11
	usernameAndPasswordMatch = 12

	def __init__(self, msg, value):
		self.msg = msg
		self.value = value

	def __str__(self):
		return self.msg

class userTable(lightTable):
	error = error
	def __init__(self):
		lightTable.__init__(self, name = 'userTable')
		self.username = self.getChar()
		self.password = self.getChar()
		self.email = self.getChar()
		self.banned = self.getBool()
		self.admin = self.getBool()
		self.banReason = self.getChar(default = '')

	def login(self, username, textPassword = '', hashPassword = ''):
		if textPassword:
			pwHash = hashlib.sha512(textPassword).hexdigest()
		elif hashPassword:
			pwHash = hashPassword
		else:
			return False #- Null string, wtf3
		res = lightManager['SELECT id FROM userTable WHERE username=%s AND password=%s', username, pwHash]
		if len(res) == 0: #- 0 rows returned
			return False
		else:
			uid = res[0][0]
			if self.getBanned(uid):
				reason = self.getBanReason(uid)
				if reason == '':
					reason = 'Account is banned'
				raise error(reason, error.banned)
			else:
				return uid

	def userExists(self, username):
		res = self.get('id', 'username', username)
		if len(res) == 0:
			return False
		else:
			return res[0]

	def emailExists(self, email):
		res = self.get('id', 'email', email)
		if len(res) == 0:
			return False
		else:
			return res[0]

	def passwordExists(self, textPassword = '', hashPassword = ''):
		if textPassword:
			pwHash = hashlib.sha512(password).hexdigest()
		elif hashPassword:
			pwHash = hashPassword
		else:
			return False #- Null string, wtf3
		res = self.get('id', 'password', pwHash)
		if len(res) == 0:
			return False
		else:
			return res[0]

	def register(self, username, password, email):
		if len(username) > 25:
			raise error('Username must be under 25 characters!', error.usernameTooLong)
		if len(username) < 3:
			raise error('Username must be more than 3 characters!', error.usernameTooShort)

		if len(password) > 25:
			raise error('Password must be under 25 characters!', error.passwordTooLong)
		if len(password) < 3:
			raise error('Password must be more than 3 characters!', error.passwordTooShort)

		if len(email) > 70:
			raise error('Email must be under 70 characters!', error.emailTooLong)
		if len(email) < 3:
			raise error('Email must be more than 3 characters!', error.emailTooShort)

		valid = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
		for c in username:
			if (c in valid) == False:
				raise error('Username contains invalid characters.', error.usernameBadCharacters)

		for c in password:
			if (c in valid) == False:
				raise error('Password contains invalid characters.', error.passwordBadCharacters)

		for c in email:
			if (c in valid) == False:
				raise error('Email contains invalid characters.', error.emailBadCharacters)

		if username == password:
			raise error('Username and password must be different!', error.usernameAndPasswordMatch)

		if self.userExists(username):
			raise error('Username already taken', error.usernameTaken)
		if self.emailExists(email):
			raise error('Email already in use', error.emailTaken)

		pwHash = hashlib.sha512(password).hexdigest()
		lightManager['INSERT INTO userTable(banReason, username, password, email) VALUES("", %s, %s, %s)', username, pwHash, email]
		return self.userExists(username)

	def get(self, value, where, equals):
		valid = ['id', 'count(id)', 'username', 'password', 'email', 'banned', 'admin', 'banReason']
		assert value in valid, 'get(value, ...) is an incorrect value!'
		assert where in valid, 'get(value, where=blah, ...) is an incorrect value!'

		query = 'SELECT %s FROM userTable WHERE %s=' % (value, where)
		return lightManager[query + '%s', equals]

	def getUsername(self, uid):
		return self.get('username', 'id', uid)[0][0]

	def getPassword(self, uid):
		return self.get('password', 'id', uid)[0][0]

	def getEmail(self, uid):
		return self.get('email', 'id', uid)[0][0]

	def getBanReason(self, uid):
		return self.get('banReason', 'id', uid)[0][0]

	def getBanned(self, uid):
		ret = self.get('banned', 'id', uid)[0][0]
		if ret == 1:
			return True
		elif ret == 0:
			return False

	def getNumRegistered(self):
		ret = self.get('count(id)', 'banned', 0)
		if ret:
			return ret[0][0]
		else:
			return 0

	def getLastRegistered(self):
		ret = lightManager['SELECT id from userTable where banned=0 ORDER BY id DESC limit 1']
		if ret:
			return ret[0][0]
		else:
			return False

	def getUserFromEmail(self, email):
		ret = lightManager['SELECT id from userTable where email=%s', email]
		if ret:
			return ret[0][0]

	def getAdmin(self, uid):
		ret = self.get('admin', 'id', uid)[0][0]
		if ret == 1:
			return True
		elif ret == 0:
			return False

	def setPassword(self, uid, password):
		if len(password) > 25:
			raise error('Password must be under 25 characters!', error.passwordTooLong)
		if len(password) < 3:
			raise error('Password must be more than 3 characters!', error.passwordTooShort)

		valid = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
		for c in password:
			if (c in valid) == False:
				raise error('Password contains invalid characters.', error.passwordBadCharacters)

		pwHash = hashlib.sha512(password).hexdigest()
		lightManager['UPDATE userTable set password=%s WHERE id=%s', pwHash, uid]

	def setEmail(self, uid, email):
		if len(email) > 70:
			raise error('Email must be under 70 characters!', error.emailTooLong)
		if len(email) < 3:
			raise error('Email must be more than 3 characters!', error.emailTooShort)

		valid = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
		for c in email:
			if (c in valid) == False:
				raise error('Email contains invalid characters.', error.emailBadCharacters)

		lightManager['UPDATE userTable set email=%s WHERE id=%s', email, uid]

	def setBanned(self, uid, banned, reason = ''):
		assert type(banned) == bool, 'call to setBanned(uid, value, ...) value must be True or False'
		assert type(reason) == str, 'call to setBanned(uid, value, reason) reason must be str'
		if banned == True:
			banned = 1
		else:
			banned = 0
		lightManager['UPDATE userTable set banned=%s WHERE id=%s', banned, uid]
		if reason:
			lightManager['UPDATE userTable set banReason=%s WHERE id=%s', reason, uid]

	def setAdmin(self, uid, admin):
		assert type(admin) == bool, 'call to setBanned(uid, value) value must be True or False'
		if admin == True:
			admin = 1
		else:
			admin = 0
		lightManager['UPDATE userTable set admin=%s WHERE id=%s', admin, uid]
