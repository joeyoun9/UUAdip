"""
# UTDewey package for processing raw data produced by the NCAR ISFF-ISS Vaisala Rawinsonde System
# current configureation is for the text output P.1 files which are assumed RAW from the sondes

Created by Joe Young March 2011 
Dept. of Atmospheric Sciences
University of Utah
Salt Lake City, Utah, USA

Created under the NSF funding for the PCAPS project 2010 - 2013
"""
import sys,time,datetime,calendar,array
import metcalcs.sounding as mc

# as with all packages for the UTDewey data system, this should simply be a function that returns 
# the data in the specialized format. Function MUST begin with the data request object (self)
# and the function is to be called 'run'

def run (self, cutoff=True,qc=True):
		# this method does not need any additional information, the soundings will be grabbed from the specified time period
		print "fetching NCAR Soundings!" #how fetching
		self.data.set("iss_soundings",[])
		num = -1
		for l_file in self.find_files('ncar_iss_rawinsondes','P.1',allow_repeats=False,aux=(not qc)):
			fname = l_file.split("/")[-1]
			ftime = calendar.timegm(time.strptime(fname[1:9]+fname[10:15]+"UTC","%Y%m%d%H%M%S%Z"))
			if ftime > self.data.end or ftime < self.data.begin:
				continue
			print fname
			# woohoo, we have the file, now just read it and return it!
			num = len(self.data.iss_soundings)
			self.data.iss_soundings.append({})
			tml = []
			pl = []
			tcl = []
			tdcl = []
			rhl = []
			wdirl = []
			wspdl = []
			vvell = []
			lonl = []
			latl = []
			gpl = []
			zl = []
			init = {"launch":ftime}
			#FIXME: please add actual initialization info to this init variable
			go = False
			for line in open(l_file):
				l = line.split()
				if not qc:
					if not l[1] == "S00": continue # gosh they make this easy!
					#IT SHOULD BE NOTED
					# that if S01 is read, that means temp/rh/pressure is ok, just GPS is bad
					# S11 means everything is bad
					# FIXME an option could be added to allow S01 observations
					# thus we have a datapoint! - and it is already QCd, dang!
					tm = calendar.timegm(time.strptime("20"+l[3]+l[4][:-3]+"UTC","%Y%m%d%H%M%S%Z")) + float(l[4][-3:])
					tml.append(tm - ftime) # append flight time, init object can hold launch time
					pl.append(float(l[5]))
					tcl.append(float(l[6]))
					rhl.append(float(l[7]))
					wdirl.append(float(l[8]))
					wspdl.append(float(l[9]))
					vvell.append(float(l[10]))
					lonl.append(float(l[11]))
					latl.append(float(l[12]))
					gpl.append(float(l[13]))
					zl.append(float(l[-1]))
					# whyyyy am i calculaing dew point?!! (Ngl can take RH!!!)
					tdcl.append(mc.sounding_dewpoint(float(l[6])+273.15 , float(l[7]) ) - 273.15 )
					# check for cutoff, if the last 3 elements of zl are all bigger than the prev, then cutoff
					if cutoff and len(zl) > 10 and zl[-4] > zl[-3] and zl[-3] > zl[-2] and zl[-2] > zl[-1] and zl[-1] > 4000:
						# let's make sure we dont cut off at the sfc b/c of bad data
						print "Cutoff Reached!"
						break
				else:
					# this is the QC'd file, so read it in - EOL Sounding Format 1.0
					if not go:
						# we are not yet at the data (following the -----) so we are in the header
						if l[0] == "-------":
							go = True # this signals that the next line is good!
						continue
					tml.append(float9(l[0])) # append flight time, init object can hold launch time
					pl.append(float9(l[4]))
					tcl.append(float9(l[5]))
					tdcl.append(float9(l[6]))
					rhl.append(float9(l[7]))
					wdirl.append(float9(l[11]))
					wspdl.append(float9(l[10]))
					vvell.append(float9(l[12]))
					lonl.append(float9(l[14]))
					latl.append(float9(l[15]))
					gpl.append(float9(l[13]))
					zl.append(float9(l[-1]))

			# and thats it, now create the object!
			self.data.iss_soundings[num]['info'] = init
			self.data.iss_soundings[num]['time'] = tml
			self.data.iss_soundings[num]['keys'] = range(len(tml))
			self.data.iss_soundings[num]['tc'] = tcl
			self.data.iss_soundings[num]['tdc'] = tdcl
			self.data.iss_soundings[num]['rh'] = rhl
			self.data.iss_soundings[num]['p'] = pl
			self.data.iss_soundings[num]['wdir'] = wdirl
			self.data.iss_soundings[num]['wspd'] = wspdl
			self.data.iss_soundings[num]['vvel'] = vvell
			self.data.iss_soundings[num]['lat'] = latl
			self.data.iss_soundings[num]['lon'] = lonl
			self.data.iss_soundings[num]['gp'] = gpl
			self.data.iss_soundings[num]['z'] = zl
		print "found ",num+1," ISS Sounding(s)!"

def float9(val):
	v = float(val)
	if v <= -999.:
		 v = float('nan')
	return v
