"""
	Version.py is a standard pacakge module for python, however this one 
	works differently, because, i am not properly trained.

	This controls what the version number is, as well, it provides all
	desired information about the module.
"""

import os,sys
import pkgutil

def get_version():
	return 3.091


class about:
 def __init__(cls):
	"""
		Return all the information about the package
		namely, version information, and available packages
		INCLUDING the newly founded env variable additional packages!
		-- for packages, find out if they are standardized??
		-- if so, tell inputs, formats, and output information/options.
	"""
	#  START WITH FINDING ALL THE PACKAGES AVAILABLE - sice this is really the only variable
	cls.packages = pkg()

	if 'UUD_EXTPACKAGES' in os.environ.keys():
		# woohoo! there is a specified external packages directory!
		# now check if this is already in they pythonpath... if not, add it.
		loc = os.environ['UUD_EXTPACKAGES']
		if loc not in os.environ['PYTHONPATH']:
			# then add it to the pythonpath
			# we will do it silently, i think it will be done every time, no biggie.
			sys.path.append(loc)
		modules = find_mods(loc,'')
		# loop through, and save these as $.module name
		for m in modules:
			cls.packages.locations["$"+m] = m[1:] # cut off that first period

	# determine all the pacakages available... somehow..
	#import uudewey.readers as ur
	code_base = os.environ['UUDPATH']+"/uudewey/formats"#''
	mod = find_mods(code_base,'')
	for m in mod:
		cls.packages.locations[m[1:]] = 'uudewey.formats'+m
	#print dir(ur)

class pkg:
	"""
		A simple package object
	"""
	locations = {}

def find_mods(code_base,ext):
	"""
		Find all named modules cascading within a subdirectory!
	"""
	out = []
	mods = [name for _, name, _ in pkgutil.iter_modules([code_base])]
	# now check if these mods are sub mods themselves
	for mod in mods:
		new_ext = ext+"."+mod
		new_base = code_base+"/"+mod
		sub_mods = find_mods(new_base,new_ext)
		if sub_mods == []:
			out.append(new_ext)
		else:
			#so there were sub modules! this was a package
			out += sub_mods
	return out
