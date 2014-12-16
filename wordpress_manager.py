import sublime
import sublime_plugin
import os
import sys
import shutil
import json
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods.posts import GetPosts

# ======== Global Arguments ====================================================

rootDir = os.path.join(sublime.packages_path(), 'Wordpress Manager')
accountsDir = os.path.join(rootDir, 'accounts')
configName = 'default.wpm-config'

isDebug = True
# print overly informative messages?
isDebugVerbose = True

# timeout for a Sublime status bar messages [ms]
messageTimeout = 250

# Client of wordpress account
wpmClient = None

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
		global date
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
		if os.path.exists(accountsDir) is False:
			os.mkdir(accountsDir)
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
		global wpmClient
		account = os.path.join(accountsDir, self.accounts[index])
		config = os.path.join(account, configName)
		config_map = json.load(open(config))
		wpmClient = Client(config_map['url'], config_map['username'], config_map['password'])

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
	def run(self):
		self.posts_list = wpmClient.call(GetPosts())
		self.title_list = [p.title for p in self.posts_list]
		self.window.show_quick_panel(self.title_list, self.editPost)

	def editPost(self, index):
		post = self.posts_list[index]
		view = self.window.new_file()
		view.run_command('wpm_get_post', {'post': post})

class WpmGetPost(sublime_plugin.TextCommand):
	"""
	Edit a post entry.
	"""
	def run(self, edit, post):
		self.view.insert(edit, 0, post.content)

class WpmNewPost(sublime_plugin.WindowCommand):
	"""
	Create a new blog post for current account.
	"""
	def run(self, arg):
		pass
