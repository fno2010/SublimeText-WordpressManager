import sublime, sublime_plugin
import wordpress_xmlrpc
import os
import shutil
import json

# ======== Global Arguments ====================================================

rootDir = os.path.join(sublime.packages_path(), 'Wordpress Manager')
accountsDir = os.path.join(rootDir, 'accounts')
configName = 'default.wpm-config'

# ======== Messaging ===========================================================

# Shows a message into Sublime's status bar
#
# @type  text: string
# @param text: message to status bar
def statusMessage(text):
	sublime.status_message(text)


# Schedules a single message to be logged/shown
#
# @type  text: string
# @param text: message to status bar
#
# @global messageTimeout
def dumpMessage(text):
	sublime.set_timeout(lambda: statusMessage(text), messageTimeout)


# Prints a special message to console and optionally to status bar
#
# @type  text: string
# @param text: message to status bar
# @type  name: string|None
# @param name: comma-separated list of connections or other auxiliary info
# @type  onlyVerbose: boolean
# @param onlyVerbose: print only if config has debug_verbose enabled
# @type  status: boolean
# @param status: show in status bar as well = true
#
# @global isDebug
# @global isDebugVerbose
def printMessage(text, name=None, onlyVerbose=False, status=False):
	message = "FTPSync"

	if name is not None:
		message += " [" + name + "]"

	message += " > "
	message += text

	if isDebug and (onlyVerbose is False or isDebugVerbose is True):
		print (message.encode('utf-8'))

	if status:
		dumpMessage(message)


# Issues a system notification for certian event
#
# @type text: string
# @param text: notification message
def systemNotify(text):
	try:
		import subprocess

		text = "FTPSync > " + text

		if sys.platform == "darwin":
			""" Run Grown Notification """
			cmd = '/usr/local/bin/growlnotify -a "Sublime Text 2" -t "FTPSync message" -m "'+text+'"'
			subprocess.call(cmd,shell=True)
		elif sys.platform == "linux2":
			subprocess.call('/usr/bin/notify-send "Sublime Text 2" "'+text+'"',shell=True)
		elif sys.platform == "win32":
			""" Find the notifaction platform for windows if there is one"""

	except Exception as e:
		printMessage("Notification failed")
		handleExceptions(e)


# Creates a process message with progress bar (to be used in status bar)
#
# @type  stored: list<string>
# @param stored: usually list of connection names
# @type progress: Progress
# @type action: string
# @type action: action that the message reports about ("uploaded", "downloaded"...)
# @type  basename: string
# @param basename: name of a file connected with the action
#
# @return string message
def getProgressMessage(stored, progress, action, basename = None):
	base = "FTPSync [remotes: " + ",".join(stored) + "] "
	action = "> " + action + " "

	if progress is not None:
		base += " ["

		percent = progress.getPercent()

		for i in range(0, int(percent)):
			base += "="
		for i in range(int(percent), 20):
			base += "--"

		base += " " + str(progress.current) + "/" + str(progress.getTotal()) + "] "

	base += action

	if basename is not None:
		base += " {" + basename + "}"

	return base

# ======== Definition of Commands ==============================================

class WpmHelloCommand(sublime_plugin.TextCommand):
	"""
	A test command for plugin.
	print 'hello, wordpress_manager'
	"""
	def run(self, edit):
		printMessage("hello, wordpress_manager")

class WpmNewAccount(sublime_plugin.WindowCommand):
	"""
	Create a new account to connect wordpress.
	"""
	def run(self):
		self.window.show_input_panel('Enter Account Name:', '', self.create, None, None)
		return

	def create(self, account):
		account_dir = os.path.join(accountsDir, account)
		if os.path.exists(account_dir) is True:
			printMessage("Account Exists, Cannot Create!")
			return

		default = os.path.join(rootDir, configName)
		os.mkdir(account_dir)
		config = os.path.join(account_dir, configName)
		shutil.copyfile(default, config)
		self.window.open_file(config)

class WpmConnectAccount(sublime_plugin.WindowCommand):
	"""
	Connect a wordpress account.
	"""
	def run(self):
		self.accounts = os.listdir(accountsDir)
		self.window.show_quick_panel(self.accounts, self.connect)

	def connect(self, index):
		account = os.path.join(accountsDir, self.accounts[index])
		config = os.path.join(account, configName)
		config_map = json.load(open(config))
		print config_map

class WpmDisconnectAccount(sublime_plugin.WindowCommand):
	"""
	Disconnect a wordpress account.
	"""
	def run(self, arg):
		pass

class WpmChangeAccount(sublime_plugin.WindowCommand):
	"""
	Change to another wordpress account.
	"""
	def run(self, arg):
		pass

class WpmModifyAccount(sublime_plugin.WindowCommand):
	"""
	Modify the config of an account.
	"""
	def run(self, arg):
		pass

class WpmGetPosts(sublime_plugin.WindowCommand):
	"""
	Get a list of all posts from current account.
	"""
	def run(self, arg):
		pass

class WpmEditPost(sublime_plugin.WindowCommand):
	"""
	Edit a post entry.
	"""
	def run(self, arg):
		pass

class WpmNewPost(sublime_plugin.WindowCommand):
	"""
	Create a new blog post for current account.
	"""
	def run(self, arg):
		pass
