import os

def run(**args):
	print "In dirlister moduele!!!"
	files = os.listdir(".")
#	print files
	return str(files)
