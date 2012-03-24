"""
	This python script UTDewey.py, written by Joe Young, March 2011
	
	Usage: request = DataRequest(string ProjectConfigFile, string Range, **kwargs) kwargs evaluate to 1 or 0, except location, which is a string
		
"""


import time
import os
import sys
import calendar
import array
import math 
from math import degrees, atan2
from time import strftime, gmtime
from datetime import tzinfo,timedelta,date


from . import tools
from tools.config_read import ConfigFile
import version as vers
from data import *

version = vers.get_version()
bounding_box = []
verbose = True
class DataFetch:
	"""All data requests will work through the DataRequest Object"""
	def __init__(cls, project, date_range, *args, **keywords ):
		# this will evaluate their request and will initialize the request object for the transmission at a later time
		cls.data = RequestDataObject()
		for kw in keywords:
			# there are several types of keyword I accept: the raw_file argument, means it copies the raw file if possible
			# the make_file argument specifies wether or not I simply spit out data, or do I save
			# save location argument is required for the make file argument	
			#		THESE THREE ARE LUMPED TOGETHER
			cls.data.set(kw,keywords[kw])
			cls[kw] = keywords[kw]
		# now check the keywords that they are acceptable
		if cls.data.raw_file and not cls.data.make_file:
			cls.data.make_file = 1
		if cls.data.make_file and not cls.data.location:
			cls.data.location = "."
		global verbose
		if verbose in args:
			cls.verbose = True
		else:
			cls.verbose = False
		"""
		## feature - if project = True, then we will check and see if a project has alerady been declared, and if so, use that
		if project == True and cls.project:
			project = cls.project
		# save the project name in the object so that it can be recalled if needed
		cls.project = project

		#### PROJECT INTERPRETATION 
		project_xml = project
			# get boundaries

		bounds = cls.__proj_dom.getElementsByTagName('boundaries')[0]
		lats = getText(bounds.getElementsByTagName('lat')[0].childNodes).split(",")
		lons = getText(bounds.getElementsByTagName('lon')[0].childNodes).split(",")
		elev = getText(bounds.getElementsByTagName('elev')[0].childNodes)

		# set the bounding box for use in the in_lat and in_lon functions
		global bounding_box 

		bounding_box = [[float(lats[0]),float(lats[1])],[float(lons[0]),float(lons[1])],float(elev)]
		cls.data.bounding_box = bounding_box # why wasnt it an internal variable in the first place?

		# for fun grab the name of the project
		cls.pname = getText(cls.__proj_dom.getElementsByTagName('name')[0].childNodes)
		cls.pid = getText(cls.__proj_dom.getElementsByTagName('id')[0].childNodes)
		"""

		cls.proj = ConfigFile(project,cls)
		cls.uudewey = vers.about() # colllect information about the package!
		
		print "Fetching data for ",cls.proj.abbrev,": "+cls.proj.name

		# data location information is fetched when individual feeds are queried
		# using the special function defined at the bottom of this page
		
		### NOW WE DEAL WITH THE DATE_RANGE which is a little more complicated
		if type(date_range) == list:
			# this is a list of dates, so assign the holders for the iterator, and move on!
			cls.time_list = date_range
			cls.args = args
			cls.kwargs = keywords
			cls.project = project
			return 
		d = date_range.split()
		# beginning date is assumed to be the first element, and end date should be the last
		cls.data.set('begin', d[0])
		if d[0].isdigit() and d[-1].isdigit():
			# then it is a number, and there is another!
			if len(d) > 1:
				cls.data.set('end',d[-1])
			elif len(d[0]) == 8:
				cls.data.begin = cls.data.begin+"00" # add hour zeroes to the beginning
				cls.data.set('end',False)###d[0]+"23") # if given one day, then we will go from 0-23z on that day
				# if given one day, we will go through 0 z the next day, which is easily done by adding 1440 minutes to the day
				# while working in epoch time
			else:
				print "If you wish to look at only one time (not really recommended) then please enter that time as a range YMD to YMD"
				exit()
		else:
			begin,end = cls.proj.findevent(date_range)
			cls.data.set('begin',begin)
			cls.data.set('end',end)


		# now that we have set dates, we need to figure out what the date is, and convert to epoch
		if len(cls.data.begin) == 8:
			# there is no hour, attach a 00
			cls.data.begin = cls.data.begin+"00"
			cls.data.begin = cls.data.end+"00"
		begin = time.strptime(cls.data.begin+"UTC","%Y%m%d%H%Z")
		if not cls.data.end:
			end = time.gmtime(calendar.timegm(begin) + 24*60*60) # add 24 hours
		else:
			end = time.strptime(cls.data.end+"UTC","%Y%m%d%H%Z")
		print time.asctime(begin)," to ",time.asctime(end)
		cls.data.begin = calendar.timegm(begin)
		cls.data.end = calendar.timegm(end)
		# save the time objects also so they can be used again
		cls.data.begintime = begin
		cls.data.endtime = end
		# now create the datestring property!
		cls.dateString = strftime("%d %b %Y %H%M UTC",gmtime(cls.data.begin))+" - "+strftime("%d %b %Y %H%M UTC",gmtime(cls.data.end))
		cls.dateInput = date_range


	def update(cls, project, time, *args, **kwargs):
		# the update function allows a prompt user to change the parameters of a request without entirely starting over
		cls.__init__(project, time, *args, **kwargs)
		#FIXME

	def next(cls):
		# iterate over input array of project values - next must be called to initialize the process
		if len(cls.time_list) > 0:
			time = cls.time_list.pop(0)
		else: return False
		cls.__init__(cls.project,time,*cls.args,**cls.kwargs)
		return True

	DO = Data
	# pack the data object in with the request object, just to make it easier to access
	def get(cls, package, **kwargs):
		# BACKWARDS COMPATABILITY
		return cls.read(package,**kwargs)

	def read(cls, package, **kwargs):
		"""
			read() will call the package [package] from streams.ingest,
			and pass all the keyword arguments **kwargs to that ingestor function 
		"""
		#FIXME - check if hte data stream is part of this project
		if cls.proj.c_version < 3:
			exec "import uudewey.readers."+package+" as c"
			return c.run(cls, **kwargs) # pass arguments directly to the run function in the module!!

		pkg = cls.proj.findsource(package, find='package')
		cls.nowPkg = package #FIXME - this will not work if requests are somehow simultaneous...
		#exec "import "+pkg+" as c"
		__import__(pkg) # ooh! all newfangled!
		c = sys.modules[pkg]
		# BACKWARDS COMPATIBILITY
		if 'read' not in dir(c):
			return c.run(cls, **kwargs) # pass arguments directly to the run function in the module!!

		return c.read(cls,**kwargs)
		# the function can either return directly, or it will put data in the data object.
		# every time this is called it will make another import, howe
	
	def write(cls, package, **kwargs):
		"""
			This method will call the write method of the format's module
			Version 3 required
		"""
		if cls.proj.c_version < 3:
			print "Version 3 or greater projects are required for the write method"
			exit()
		pkg = cls.proj.findsource(package,find='package')
		cls.nowPkg = package
		__import__(pkg)
		c = sys.modules[pkg]
		c.write(cls,**kwargs)



	files = {}

	def find_files (cls, stream, ext, aux=False, allow_repeats=True, clear_stale = False, aux_key=0):
		# NEW - ext can be a list or dict... it can be everything!!
		if not clear_stale:
			if stream in cls.files:
				return cls.files[stream]
		# this function replaces the data_location internal function by both finding the data location, and the files
		# the extension is now a required input
		# allow repeats means that we allow the same filename to be recorded from multiple locations, if not, we take the first one we see
		if cls.proj.c_version < 3:
			streams = cls.proj.findsource(stream) 
			for st in streams:
				if tools.getText(st.getElementsByTagName('type')[0].childNodes) == stream:
					del streams # a tidly bit of cleaning
					# we have to read the search attriute, if it is 1, then searching is required
					###search = int(st.getAttribute('search')) == 1 # so it returns True/False
					src_id = 'aux' if aux else 'location'
					break
			dir_info = st.getElementsByTagName(src_id)
			if aux and aux_key < len(dir_info):
				# then all is good
				source = dir_info[aux_key]
			elif aux:
				#hmm, we did not find the key, return an error!!
				print "AHH! that aux_key was not definied, you should add another <aux> tag in your project config file"
				print "Key:",aux_key,'Max Aux Key:',len(dir_info) - 1
				exit()
				return False;
			else:
				source = dir_info[0]
			source = tools.getText(source.childNodes) # search is not important... the method will work great either eay
		else:
			source = cls.proj.findsource(cls.nowPkg) # aux is not a valid code in the version 3
			
		out = [] #init the output dir
		# Using the recursive searching code, we will find the files as specified.
		cls.allow_rep = allow_repeats
		out = cls.__dig_in(source, ext)
		cls.log("found",len(out),"files with '",ext,"' example:",out[0])
		# FIXME now we really need to sort the files, since they are going to be in all rediculous orders, and that is not nice
		# sorting by filename will be best.
		out = sorted(out) # this seems to work for now...
		# make a cache, since the network tends to be slow, so if it is called multiple times, it can be run
		cls.files[stream] = out # can get stale if this runs too long...
		return out


	def __dig_in (cls, dr, ext):
		# this is the recursive sub function that will keep digging, and will return any files it finds
		cls.rtp = False # initialize this since we use it in logic later, so have it set
		if cls.allow_rep == False or cls.allow_rep == 'time' or cls.allow_rep == 'size':
			if cls.allow_rep:
				cls.rtp = cls.allow_rep
				cls.something = [] #FIXME - when you fix the times-this is something you need to check
			cls.allow_rep = []
		out = []
		dr = dr + "/" if not dr[-1] == "/" else dr

		files = os.listdir(dr)
		for fl in files:
			if os.path.isdir(dr+fl):
				# it is a new dir, so dig in further!
				out = out + cls.__dig_in(dr+fl+"/",ext)
				continue
			elif type(ext) == str and ext not in fl:
				continue
			elif type(ext) == list:
				# do the same ext checkm but since it is a list, check that every element of the list is present...
				good = True
				for s in ext:
					if s not in fl: good = False
				if not good: continue
			elif type(ext) == dict:
				# well, if it needs more special searching, then here we go
				ks = ext.keys()
				good = True
				if 'includes' in ks:
					for s in ext['includes']:
						if s not in fl: good = False
				if 'excludes' in ks:
					for s in ext['excludes']:
						if s in fl: good = False
				if 'length' in ks:
					if len(fl) != ext['length']: good = False
				if not good: continue

			#whew, done checking...
			# check if we need to check repeats, and if we do, then check
			if type(cls.allow_rep) == list:
				if fl in cls.allow_rep and not cls.rtp: continue
				if cls.rtp and fl in cls.allow_rep:
					# we are supposed to check time or size, FIXME - i didnt make it work right now.
					continue
				cls.allow_rep.append(fl)
			out.append(dr+fl)
					
		return out


	def log (cls , *message) :
		# this will check verbose, and if it is declared, print the message to std out
		log = sys.stdout
		if cls.verbose and message:
			log.write(str(message)+"\n")
			#print " ".join(message)



	def in_lat (cls, lat ):
		if lat > cls.proj.bounds[0][0] and lat < cls.proj.bounds[0][1]:
			return True
		else:
			print "Failed in_lat test!",lat
			return False

	def in_lon (cls, lon ):
		if lon > cls.proj.bounds[1][0] and lon < cls.proj.bounds[1][1]:
			return True
		else:
			print "Failed in_lon test!",lon
			return False

	funcs = tools

	# define a flipping function, sice I seem to use it somewhat frequently - can be imported elsewhere as well!
	def flip2d(cls, wrong):
		import numpy as np
		#UPDATED 1 - 6- 2011: wrong[0] instead of wrong[1]. Thus, all columns must be the same length as col 0!
		right = np.zeros((len(wrong[0]),len(wrong))) 
		# since Z is always full, but X can vary with the span parameter, it is best to use obCount
		i = 0
		for r in wrong:
			c = 0
			for v in r:
				right[c][i] = v #index failure means wrong[0] does not tell the full story about this array
				c+=1
			i+=1
		return right	
					
class RequestDataObject:
	def __init__(cls):
		cls.raw_file = False
		cls.make_file = False
		cls.location = '.'
	def set(cls,key,value):
		# ensure the key is not a method of the data object
		#FIXME
		cls.__dict__[key] = value


