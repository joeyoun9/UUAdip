"""
# UTDewey package for processing NWS Rawinsondes, in v2.0 this only does KSLC, but it is more based on the 
# data format, and not necessarily the location of the data. 
# current configuration is for PTU and GPS files, to be time synched, as well, John Horel has processed
# some more high resolution / more raw formats, and those will be experimented with, possibly with sub operations
v2.0 of nws processing -- added support for John's versions of this data... I am not certain if this will bring great benefit

Created by Joe Young March 2011 
Dept. of Atmospheric Sciences
University of Utah
Salt Lake City, Utah, USA

Created under the NSF funding for the PCAPS project 2010 - 2013
"""
import sys,time,datetime,calendar,array,math
from math import atan2


# as with all packages for the UTDewey data system, this should simply be a function that returns 
# the data in the specialized format. Function MUST begin with the data request object (self)
# and the function is to be called 'run'

def run (self,station='KSLC',horel_proc=False):
	# nws balloons from KSLC, from the processed GPS/PTU files. No interpolation needed, just gotta look at the correct columns!
	# PTU = temp/pressure/rh/dewpoint(DP) and gpht
	# GPS = lat/lng/alt and u,v of winds
	# FIXME - station is KSLC now, but variable options should be there, plus a default should be defined in the XML
	#### FIXME - THERE ARE 3 INSTANCES WHERE WE NEED TO GO TO THE WYOMING SOUNDING FILES!!! 1DEC 12Z, 31JAN 12Z, 1FEB 00Z
	print "Getting NWS Soundings"
	# NOW we need to differentiate between horel_proc
	self.data.set("nws",[])
	files = self.find_files('nws_rawinsondes','PTU',allow_repeats=False) if not horel_proc else self.find_files('nws_rawinsondes',{
	'includes': ['KSLC','_smth.dat'],
	'excludes': ['._','cpin'] #NO CPIN!
	},aux=True,allow_repeats='time')
	num = -1
	# find the files in the time!
	for lfile in files:
		fname = lfile.split("/")[-1]
		num = len(self.data.nws)
		# init holder lists
		tml = []
		tcl = []
		pl = []
		rhl = []
		tdcl = []
		wdirl = []
		wspdl = []
		ul = []
		vl = []
		gpl = []
		zl = []
		latl = []
		lonl = []
		if not horel_proc:
			if not fname[-7:] == "PTU.txt":
				continue # we will process ptu and gps at the same time 
			ftime = calendar.timegm(time.strptime(str(fname[6:-10])+"UTC","%Y%m%d%H%Z")) # format without minutes expected!!
			# but wait! this is not the right time, get the launch time, which is the first time in the file...
			if ftime > self.data.end or ftime < self.data.begin:
				continue
			print fname
			self.data.nws.append({})

			checked = False
			for line in open(lfile):
				l = line.split()
				if len(l) ==0 or l[0] != "72572": continue # quick check for the right line :p
				# now assign values that can be assigned
				# !!! we cannot QC this data in this method since the second reading would
				# get totally thrown off if we delete values
				ptime = calendar.timegm([int(l[15]),int(l[16]),int(l[17]),int(l[18]),int(l[19]),int(l[20][:-3])] ) + float(l[20][-3:])
				if not checked and ( ptime < self.data.begin or ptime > self.data.end ):
					break
				elif not checked:
					## it passed the test!
						checked = True
				tml.append(ptime)
				tcl.append(float(l[33])) # listed as td, and is measured twice apparently
				rhl.append(float(l[29]))
				pl.append(float(l[22])) # also measured twice, but im only taking this one
				tdcl.append(float(l[-6]))
				gpl.append(float(l[42]))
			# check if it failed the time check for the internal flight time. if so, then dump it
			if not checked: 
				self.data.nws.pop(-1)
				continue
			for line in open(lfile[:-9]+"6pGPS.txt"):
				l = line.split()
				if len(l) ==0 or l[0] != "72572": continue # quick check for the right line
				latl.append(float(l[21]))
				lonl.append(float(l[24]))
				zl.append(float(l[27])) # this is also a geopotential height i think... oh well
				# compute wdir and wspd
				u = float(l[30])
				v = float(l[33])
				spd = (u**2 + v**2)**.5
				dir = math.degrees(atan2(u,v)) - 180
				ul.append(u)
				vl.append(v)
				wdirl.append(dir)
				wspdl.append(spd)
			# FIXME - need to do a small check, if the length of tml == length of others, if not, um, fail?
			if len(tml) != len(zl): 
				print "Um, crap, .PTU and .GPS files had different lengths... File:",lfile
				self.data.nws.pop(-1)
				continue
		else:
			#HOREL PROC - process John's modified data format...
			ftime = calendar.timegm(time.strptime(fname[5:-9]+"UTC","%Y%m%d%H%Z"))
			if ftime > self.data.end or ftime < self.data.begin:
				continue
			self.data.nws.append({})
			ln = 0
			success = True # define a variable to know whether or not to break the whole process on failure
			for line in open(lfile):
				ln += 1
				if ln == 1:
					l = line.split()
					init_lat = float(l[1])
					init_lon = float(l[2])
				# APPARENTLY ELIF DOES NOT WORK IN THIS LANGUAGE. DAMNIT.
				if ln == 2:
					l = line.split()
					init_time = calendar.timegm(time.strptime(l[5],"%Y%m%d%H%M%S")) #GRRRRRRR
					if init_time < self.data.begin or init_time > self.data.end:
						success = False
						break
					print "Reading NWS File:",fname
				if ln < 5: continue
				l = line.split() # should work for now, and i pray he does not change the format further... which i expect him to do.
				latl.append(init_lat)
				lonl.append(init_lon)
				tml.append(init_time)
				tcl.append(float(l[2]))
				pl.append(float(l[1]))
				rhl.append(float(l[4]))
				tdcl.append(float(l[3]))
				wdirl.append(float(l[12]))
				wspdl.append(float(l[11]))
				ul.append(float(l[13]))
				vl.append(float(l[14]))
				gpl.append(0)
				zl.append(float(l[0]))
				# and yes, he made all these extra variables, but i dont personally care for them now...
				#FIXME GRRRRRRRRRRRRR
			if not success:
				self.data.nws.pop(-1)
				continue


						
			
		self.data.nws[num]['info'] = {'launch':ftime} #FIXME - launch time is not technically not ftime!!	
		self.data.nws[num]['time'] = tml
		self.data.nws[num]['keys'] = range(len(tml))
		self.data.nws[num]['tc'] = tcl 
		self.data.nws[num]['p'] = pl
		self.data.nws[num]['rh'] = rhl
		self.data.nws[num]['tdc'] = tdcl
		self.data.nws[num]['wdir'] = wdirl
		self.data.nws[num]['wspd'] = wspdl
		self.data.nws[num]['u'] = ul
		self.data.nws[num]['v'] = vl
		self.data.nws[num]['gp'] = gpl
		self.data.nws[num]['z'] = zl
		self.data.nws[num]['lat'] = latl
		self.data.nws[num]['lon'] = lonl
	print "Found",num + 1,"NWS sounding(s)!"
