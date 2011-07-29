#!/usr/bin/env python


"""
	This python script UTDewey.py, written by Joe Young, March 2011
	
	Updates from 2.0.0: Many functionality adjustments have been made, including increased complexity of file searhces:
		-- increased ability to factor in multiple elements of a file name
		-- size and data evaliation, to be able to fetch  the largest and/or newest of the files with the same name that are found
	-- NWS processing adds support for John Horel's processed NWS sondes - Jury will be out on wether or not they are truly better...
	-- plot artist mpl timeticks will plot nice times for localtime too, and not only follow UTC formatting
		-- as well, major ticks without labels will be supported
		-- major times will be plotted if they occur at the beginnning or end -- OPTIONAL
	-- ceilometer will produce gradient data
	-- streams.format package will begin to be developed with some codes to synthesize sounding post-fetch processing
	-- streams.format CAN also contain some of the libraries used for advaned processing, such as gradient evaluation and whatnot\
	-- main DataRequest can accept a list of times, and can be iterated with the next() method.
	10 may 2011

	This is a project-inspecific code set which uses some remote specified XML files of the apropriate type
	to ingest numerous various datasets and return formatted and fundamentally QC'd versions from the raw data
	
	the data manager will read in the config XML, and will define variables. then when sub-requests are made
	it will load the proper package for that request, and get the data.

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

from xml.dom.minidom import parse

from . import version as vers


version = vers.get_version()
bounding_box = []
verbose = True
class DataFetch:
	"""All data requests will work through the DataRequest Object"""
	def __init__(self, project, date_range, *args, **keywords ):
		# this will evaluate their request and will initialize the request object for the transmission at a later time
		self.data = RequestDataObject()
		for kw in keywords:
			# there are several types of keyword I accept: the raw_file argument, means it copies the raw file if possible
			# the make_file argument specifies wether or not I simply spit out data, or do I save
			# save location argument is required for the make file argument	
			#		THESE THREE ARE LUMPED TOGETHER
			self.data.set(kw,keywords[kw])
			self[kw] = keywords[kw]
		# now check the keywords that they are acceptable
		if self.data.raw_file and not self.data.make_file:
			self.data.make_file = 1
		if self.data.make_file and not self.data.location:
			self.data.location = "."
		global verbose
		if verbose in args:
			self.verbose = True
		else:
			self.verbose = False
		## feature - if project = True, then we will check and see if a project has alerady been declared, and if so, use that
		if project == True and self.project:
			project = self.project
		# save the project name in the object so that it can be recalled if needed
		self.project = project
		#### PROJECT INTERPRETATION 
		project_xml = project
		while True:
			try:
				self.__proj_dom = parse(project_xml)
				break
			except ValueError:
				print "Nuts. Looks like there is something wrong with your project config file: ",project_xml
				sys.exit()
		# get boundaries
		bounds = self.__proj_dom.getElementsByTagName('boundaries')[0]
		lats = getText(bounds.getElementsByTagName('lat')[0].childNodes).split(",")
		lons = getText(bounds.getElementsByTagName('lon')[0].childNodes).split(",")
		elev = getText(bounds.getElementsByTagName('elev')[0].childNodes)
		global bounding_box # set the bounding box for use in the in_lat and in_lon functions
		bounding_box = [[float(lats[0]),float(lats[1])],[float(lons[0]),float(lons[1])],float(elev)]
		self.data.bounding_box = bounding_box # why wasnt it an internal variable in the first place?
		# for fun grab the name of the project
		self.pname = getText(self.__proj_dom.getElementsByTagName('name')[0].childNodes)
		self.pid = getText(self.__proj_dom.getElementsByTagName('id')[0].childNodes)
		print "Fetching data for ",self.pid,": "+self.pname
		# data location information is fetched when individual feeds are queried
		# using the special function defined at the bottom of this page
		
		### NOW WE DEAL WITH THE DATE_RANGE which is a little more complicated
		if type(date_range) == list:
			# this is a list of dates, so assign the holders for the iterator, and move on!
			self.time_list = date_range
			self.args = args
			self.kwargs = keywords
			self.project = project
			return 
		d = date_range.split()
		# beginning date is assumed to be the first element, and end date should be the last
		self.data.set('begin',d[0])
		if d[0].isdigit() and d[-1].isdigit():
			# then it is a number, and there is another!
			if len(d) > 1:
				self.data.set('end',d[-1])
			elif len(d[0]) == 8:
				self.data.begin = self.data.begin+"00" # add hour zeroes to the beginning
				self.data.set('end',False)###d[0]+"23") # if given one day, then we will go from 0-23z on that day
				# if given one day, we will go through 0 z the next day, which is easily done by adding 1440 minutes to the day
				# while working in epoch time
			else:
				print "If you wish to look at only one time (not really recommended) then please enter that time as a range YMD to YMD"
				exit()
		else:
			# if it is something else, then we will search the project events for what is written
			events = self.__proj_dom.getElementsByTagName("event")
			found = False
			for event in events:
				# we are looping through iops, get the begin and end times, and if we are still in one, fetch it!
				id = getText(event.getElementsByTagName('id')[0].childNodes) ## the id is a 2 digit number corresponding to iop##
				if id == date_range:
					self.data.set("begin", getText(event.getElementsByTagName("begin")[0].childNodes))
					self.data.set("end", getText(event.getElementsByTagName("end")[0].childNodes))
					found = True
					break
			if not found:
				print """I could not figure out your time range: """+date_range+""" (or it was too large) 
	Please use the format: 'YYYYMMDDHH to YYYYMMDDHH' OR 'YYYYMMDD' OR 'IOP##'. 
	Inputs other than these values will not be interpreted.
				"""
				exit()

		# now that we have set dates, we need to figure out what the date is, and convert to epoch
		if len(self.data.begin) == 8:
			# there is no hour, attach a 00
			self.data.begin = self.data.begin+"00"
			self.data.begin = self.data.end+"00"
		begin = time.strptime(self.data.begin+"UTC","%Y%m%d%H%Z")
		if not self.data.end:
			end = time.gmtime(calendar.timegm(begin) + 24*60*60) # add 24 hours
		else:
			end = time.strptime(self.data.end+"UTC","%Y%m%d%H%Z")
		print time.asctime(begin)," to ",time.asctime(end)
		self.data.begin = calendar.timegm(begin)
		self.data.end = calendar.timegm(end)
		# save the time objects also so they can be used again
		self.data.begintime = begin
		self.data.endtime = end
		# now create the datestring property!
		self.dateString = strftime("%d %b %Y %H%M UTC",gmtime(self.data.begin))+" - "+strftime("%d %b %Y %H%M UTC",gmtime(self.data.end))
		self.dateInput = date_range


	def update(self, project, time, *args, **kwargs):
		# the update function allows a prompt user to change the parameters of a request without entirely starting over
		self.__init__(project, time, *args, **kwargs)
		#FIXME

	def next(self):
		# iterate over input array of project values - next must be called to initialize the process
		if len(self.time_list) > 0:
			time = self.time_list.pop(0)
		else: return False
		self.__init__(self.project,time,*self.args,**self.kwargs)
		return True


	def get(self, package, **kwargs):
		""" get() will call the package [package] from streams.ingest, and pass all the keyword arguments **kwargs to that ingestor function """
		#FIXME - check if hte data stream is part of this project

		exec "import streams.ingest."+package+" as c"
		return c.run(self, **kwargs) # pass arguments directly to the run function in the module!!
		# the function can either return directly, or it will put data in the data object.
		# every time this is called it will make another import, howe




	files = {}

	def find_files (self, stream, ext, aux=False, allow_repeats=True, clear_stale = False, aux_key=0):
		# NEW - ext can be a list or dict... it can be everything!!
		if not clear_stale:
			if stream in self.files:
				return self.files[stream]
		# this function replaces the data_location internal function by both finding the data location, and the files
		# the extension is now a required input
		# allow repeats means that we allow the same filename to be recorded from multiple locations, if not, we take the first one we see
		streams = self.__proj_dom.getElementsByTagName("stream")
		for st in streams:
			if getText(st.getElementsByTagName('type')[0].childNodes) == stream:
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
		source = getText(source.childNodes) # search is not important... the method will work great either eay
		out = [] #init the output dir
		# Using the recursive searching code, we will find the files as specified.
		self.allow_rep = allow_repeats
		out = self.__dig_in(source, ext)
		self.log("found",len(out),"files with '",ext,"' example:",out[0])
		# FIXME now we really need to sort the files, since they are going to be in all rediculous orders, and that is not nice
		# sorting by filename will be best.
		out = sorted(out) # this seems to work for now...
		# make a cache, since the network tends to be slow, so if it is called multiple times, it can be run
		self.files[stream] = out # can get stale if this runs too long...
		return out


	def __dig_in (self, dr, ext):
		# this is the recursive sub function that will keep digging, and will return any files it finds
		self.rtp = False # initialize this since we use it in logic later, so have it set
		if self.allow_rep == False or self.allow_rep == 'time' or self.allow_rep == 'size':
			if self.allow_rep:
				self.rtp = self.allow_rep
				self.something = [] #FIXME - when you fix the times-this is something you need to check
			self.allow_rep = []
		out = []
		dr = dr + "/" if not dr[-1] == "/" else dr

		files = os.listdir(dr)
		for fl in files:
			if os.path.isdir(dr+fl):
				# it is a new dir, so dig in further!
				out = out + self.__dig_in(dr+fl+"/",ext)
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
			if type(self.allow_rep) == list:
				if fl in self.allow_rep and not self.rtp: continue
				if self.rtp and fl in self.allow_rep:
					# we are supposed to check time or size, FIXME - i didnt make it work right now.
					continue
				self.allow_rep.append(fl)
			out.append(dr+fl)
					
		return out


	def log (self , *message ) :
		# this will check verbose, and if it is declared, print the message to std out
		if self.verbose and message:
			print message
			#print " ".join(message)



	def in_lat (self, lat ):
		if lat > bounding_box[0][0] and lat < bounding_box[0][1]:
			return True
		else:
			print lat
			return False

	def in_lon (self, lon ):
		if lon > bounding_box[1][0] and lon < bounding_box[1][1]:
			return True
		else:
			return False
	# define a flipping function, sice I seem to use it somewhat frequently - can be imported elsewhere as well!
	def flip2d(self, wrong):
		import numpy as np
		#UPDATED 1 - 6- 2011: wrong[0] instead of wrong[1]. Thus, all columns must be the same length as col 0!
		right = np.zeros((len(wrong[0]),len(wrong))) # since Z is always full, but X can vary with the span parameter, it is best to use obCount
		i = 0
		for r in wrong:
			c = 0
			for v in r:
				right[c][i] = v
				c+=1
			i+=1
		return right	
					
class RequestDataObject:
	def __init__(self):
		self.raw_file = False
		self.make_file = False
		self.location = '.'
	def set(self,key,value):
		# ensure the key is not a method of the data object
		#FIXME
		self.__dict__[key] = value


# SOME UTILITIES AS WELL

def dump(obj):
  for attr in dir(obj):
    print "obj.%s = %s" % (attr, getattr(obj, attr))
	




def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)
