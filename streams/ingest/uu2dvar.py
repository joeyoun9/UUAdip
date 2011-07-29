#!/usr/bin/env python
"""
	ncar_iss_915_rwp module will read in 915MHz RWP data
"""

import sys,time,datetime,calendar,array,os,math,UTDewey

import mpl_toolkits.basemap as b

def run (self,product):
	# oh its amazing
	x = array.array('i')
	y = []
	u = []
	v = []
	print "Reading UU2dvar data"
	for file_dir in self.find_files('uu2dvar','.nc',allow_repeats=False):
		# EACH NETCDF FILE IS AN OBSERVATION!!!
		fname = file_dir.split("/")[-1]
		obtime = calendar.timegm(time.strptime(fname.split("_")[0]+"UTC",'%Y%m%d%H%Z'))
		# ok, begin/end check
		if obtime < self.data.begin or obtime > self.data.end: continue
		self.log("Reading",fname,obtime)
		nc = b.NetCDFFile(file_dir)
		UTDewey.dump(nc)
		lats = nc.variables['latitude'].data
		lons = nc.variables['longitude'].data
		var = nc.variables[product].data
		nc.close()
		# Hella FIXME - revise once we know how to use this data...
		return lats,lons,var

