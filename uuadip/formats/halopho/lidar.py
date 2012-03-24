"""
	Read in raw halophotonics lidar data
	Have options for specifying what kind of scan you want data from, but there are too many options
	for this code to truly be able to read every conceivable form of data
"""


def run(self, stare=True,log=True):
	"""
		read in and return the lidar data, 
		#FIXME - STARE MODE ONLY!!!
		stare :      should only stare (azimuth = 90 shots be used?)
		log   :      should data be returnd as a logbase 10 value

		# NO BINNING
	"""
	X = [] # times
	Y = [] # heights
	Z = [] # 2-D values

	
	for fd in self.find_files('v3','.hpl',allow_repeats=False):
		# well, now we are in a file...
		fname = fd.split('/')[-1]
		# try to use the filetime to judge if it can be used
		# file name: Wind_Profile_20_20110114_160614.hpl
		# time in this file (start) was 3 seconds later tan the indicated time...
		if fname[0] == '.': continue # dont want any open or swp files
		print "reading",fname
		
	

