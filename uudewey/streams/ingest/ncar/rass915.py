"""
UTDewey package for ingesting raw NetCDF NCAR ISS 915MhZ RASS data
Current configuration is for rass provided by EOL for PCAPS project.

Created by Joe Young April 2011
Dept. of Atmospheric Sciences
University of Utah
Salt Lake City, Utah

Created from NSF funcing for the PCAPS project 2010 - 2013
"""

import sys,time,datetime,calendar,array,os,UTDewey
from numpy import absolute,append,nanmax,nanmin,nan

import mpl_toolkits.basemap as b

def run (self,variable='tv',plot_levels=15, first_cutoff=2.5):
	"""
		ingest 915MhZ RASS

	"""
	# initialize output lists
	X = array.array('i')
	Y = array.array('f')
	T = []
	self.data.set('rass915',UTDewey.requestDataObject())
	print "Finding RASS Files";
	for file_dir in self.find_files('ncar_iss_915_rass','nc',allow_repeats=False):
		# EACH NETCDF FILE IS AN OBSERVATION!!!
		fname = file_dir.split("/")[-1]
		obtime = calendar.timegm(time.strptime(fname.split(".")[1]+fname.split(".")[2]+"UTC",'%Y%m%d%H%M%S%Z'))
		# ok, begin/end check
		if obtime < self.data.begin or obtime > self.data.end: continue
		self.log("Reading",fname,obtime)
		nc = b.NetCDFFile(file_dir)
		#print UTDewey.dump(nc.variables)
		# lets play with mehods
		if variable not in nc.variables.keys():
			print variable,"Is not a valid RASS variable..."
			# be ince and return the valid variables
			print "Here are the valid variables: ",nc.variables.keys()
			return False
		vals = nc.variables[variable].data # bad assumption that this is the data i care about, SNRtv also there
		# FIXME - a check that the bottom value is within range of the preious bottoms, get a max delta Tv?
		hts = nc.variables['height'].data
		hld = []
		for val in vals[0]:
			if val == 9999.: val= nan
			hld.append(val)
		# check if the surface value is > 5C greater than the second value, if so, assign nan to the sfc
		if variable == 'tv' and absolute(hld[0] - hld[1]) >= first_cutoff:
			hld[0] = nan
		T.append(hld)
		X.append(obtime)
		Y = hts[0] #FIXME - what if there is a zero, or some other number of vertical pts?
		nc.close()
	# naturally, this is the wrong orientation.. since each vertical profile is added as a horizontal row.
	T = self.flip2d(T)

	# create the convenience plotting object
	# Convenience information - return a variable which contains the plotting levels for the ceilometer plots
	high_v = nanmax(T)
	low_v = nanmin(T)
	inc = absolute(high_v - low_v) / plot_levels
	self.data.rass915.set('plot_levels',[low_v + x*inc for x in range(plot_levels)])
	return X,Y,T	

		
