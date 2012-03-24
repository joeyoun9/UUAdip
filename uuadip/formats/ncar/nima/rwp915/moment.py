#!/usr/bin/env python
"""
	ncar_iss_915_rwp.moment module will read in 915MHz RWP moment data
"""

import sys,time,datetime,calendar,array,os,math
import numpy as np

import mpl_toolkits.basemap as b

def run (self,max_height=30000,variable='power',vertical_only = True,beam=False):
	# oh its amazing
	x = array.array('i')
	y = []
	z = [] # in case of backscatter
	print "Reading 915MHz Radar Wind Profiler - Moment Data - NIMA QC'd"
	if vertical_only and not beam:
		beam = 1
	for file_dir in self.find_files('ncar_iss_915_rwp','.mom.nc',aux='true',allow_repeats=False, aux_key=1):
		# EACH NETCDF FILE IS AN OBSERVATION!!!
		fname = file_dir.split("/")[-1]
		obtime = calendar.timegm(time.strptime(fname.split(".")[1]+'000000'+"UTC",'%Y%m%d%H%M%S%Z'))
		# ok, begin/end check - these files represent 14 hours
		if obtime + 86400 < self.data.begin or obtime - 86400 > self.data.end: 
			continue #FIXME - must account for the next couple hours too...
		self.log("Reading",fname,obtime)
		nc = b.NetCDFFile(file_dir)
		# fetch what the missing value is, so we can detect it in the data later
		if variable not in nc.variables.keys():
			print "That is not a valid variable"
			print "Here are the availalbe variables:",nc.variables.keys()
			return False
		else:
			# well, so they did give us a variable, so fetch!
			# thse files have dimensions in both height and time, so
			data = nc.variables[variable].data
			rng = nc.variables[variable].valid_range
			ht = nc.variables['heights'].data
			tm = nc.variables['time'].data
			el = nc.variables['beamNum'].data # beamNum - 1-5 for what it is showing
			# now, there are many profiles per file, so we loop through those
			for t in range(len(tm)):
				if beam and not el[t] == beam:
					continue
				ob_time = obtime + tm[t]
				if ob_time < self.data.begin or ob_time > self.data.end:
					continue
				x.append(ob_time)
				yh = []
				zh = []
				for k in range(len(ht[t])):
					h = ht[t][k]
					if h > max_height: break
					yh.append(h)
					val = data[t][k]
					# now check that it is within the valid range
					if val < rng[0] or val > rng[1]:
						zh.append(np.nan)
					else:
						zh.append(val)
				z.append(zh)
				y.append(yh)
		nc.close()
	z = self.flip2d(z)
	# and now create the data object
	data = self.DO(['time','height'],'pcaps.xml...',self)
	data.setdim('time',x)
	data.setdim('height',y)
	data.new(variable,fill = z)

	return data
