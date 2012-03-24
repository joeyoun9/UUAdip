"""

	config_read.py a script for standardizing the reading of project config files.
	provides a number of functions which are used by the DataFetch to get the information from the config file

	This is version 3.0, however, it reads version information (or the lack thereof) to better determine the information
	
	Used by both __init__ and find_files
	
"""

from __init__ import getText
from xml.dom.minidom import parse
import os

import sys

class ConfigFile:
	"""
		The config file object, which initializes simply with the location of the project config file
	"""
	# define some values
	__dom_ = False	
	bounds = False
	name = False
	abbrev = False
	cache = False
	data_fetch = False

	def __init__(cls, location, fetch):
		"""
			Crete the ConfigFile object, and scan the file for information
		"""
		if not location:
			print "Project configuration file location is required"
			exit()
		## FIXME (future) - if project = True, then we will check and see if a project has alerady been declared, and if so, use that

		# import the file, and fail nicely
		while True:
			try:
				cls.__dom_ = parse(location)
				break
			except ValueError:
				print "Nuts. Looks like there is something wrong with your project config file: ",location
				exit()
		# now it is imported
		cls.name = getText(cls.__dom_.getElementsByTagName('name')[0].childNodes)
		cls.abbrev = getText(cls.__dom_.getElementsByTagName('id')[0].childNodes)
		cls.data_fetch = fetch #this object has information about the packages, needed later

		bounds = cls.__dom_.getElementsByTagName('boundaries')[0]
		lats = getText(bounds.getElementsByTagName('lat')[0].childNodes).split(",")
		lons = getText(bounds.getElementsByTagName('lon')[0].childNodes).split(",")

		cls.bounds = [
			[float(lats[0]),float(lats[1])],[float(lons[0]),float(lons[1])],
			getText(bounds.getElementsByTagName('elev')[0].childNodes)]
		

		# now that the basics are ingested, we should check the version
		if len(cls.__dom_.getElementsByTagName('version')) < 1:
			# then there is no version, we assume version 2
			"""
				compile the list of files from version 2 formatting
			"""
			version = 2
		else:
			version = int(getText(cls.__dom_.getElementsByTagName('version')[0].childNodes))
		cls.c_version = version
		# check for cache information - used by compile.py 
		cache = cls.__dom_.getElementsByTagName('cache')
		if len(cache) == 1:
			cls.cache = getText(cls.__dom_.getElementsByTagName('cache')[0].childNodes)

	def findsource(cls, stream, find='location'):
		"""
			identify the source from the version - to comply with the already established practice
			 IF VERSION 2 - THEN SIMPLY find and return all 'stream' objects
		""" 
		if not find == 'location':
			# then we are not finding the location
			if cls.c_version < 3:
				return stream # the location will be a guide to where we should search, since this should be just the stream
		if cls.c_version < 3:
			return cls.__dom_.getElementsByTagName('stream')
		# stream will be the name of the data (like dugway_ct25k) the value we should return is the source of that data
		# as well as the type
		
		streams =  cls.__dom_.getElementsByTagName('stream')
		if find=='all':
			# then they are requesting to see ALL the streams - used by compile
			return streams
		for s in streams:
			if getText(s.getElementsByTagName('name')[0].childNodes) == stream:
				# then this (s) is our object!
				if find == 'package':
					typ = getText(s.getElementsByTagName('type')[0].childNodes)
					return cls.data_fetch.uudewey.packages.locations[typ]
					# this should fail if they type has no package... #FIXME - fail better
					"""
					if '$' in string:
						# if the string begins with $. that means we are referring
						# to a local reader/translator/whatnot package
						if 'UUD_EXTPACKAGES' in os.environ.keys:
							
							exit()
					return 'uudewey.readers.'+pkg
					"""
				else:
					return getText(s.getElementsByTagName('location')[0].childNodes)
		# if we got here, then the stream they listed was not an available one, so return a list of available streams
		print "oops, the stream identified as '",stream,"' was not located, here are the available streams from the project config file:"
		for s in streams:
			print getText(s.getElementsByTagName('name')[0].childNodes)
	
	def findevent(cls, needle):
		"""
			find if a specified event is in the events category, and if not, then return text saying so
			This should be called only after the code has concluded that it is a non-date stamp
		"""
					# if it is something else, then we will search the project events for what is written
		events = cls.__dom_.getElementsByTagName("event")
		found = False
		for event in events:
			# we are looping through iops, get the begin and end times, and if we are still in one, fetch it!
			id = getText(event.getElementsByTagName('id')[0].childNodes) ## the id is a 2 digit number corresponding to iop##
			if id == needle:
				return getText(event.getElementsByTagName("begin")[0].childNodes), getText(event.getElementsByTagName("end")[0].childNodes)
				found = True
				break
		if not found:
			print """I could not figure out your time range: """+needle+""" (or it was too large) 
	Please use the format: 'YYYYMMDDHH to YYYYMMDDHH' OR 'YYYYMMDD' OR 'Event ID*'. 
	Inputs other than these values will not be interpreted.

	*Event id is specified as an <event> tag in the project config KML. See jsyoung.us to learn more
			"""
			exit()

