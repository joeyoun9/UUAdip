#!/usr/bin/env python
"""
	ncar_iss_915_rwp.moment module will read in 915MHz RWP moment data
"""

import sys,time,datetime,calendar,array,os,math
import numpy as np

import mpl_toolkits.basemap as b

def run (self,max_height=30000,variable='sigNoiseRatio',vertical_only = False):
	# oh its amazing
	x = array.array('i')
	y = []
	z = [] # in case of backscatter
	print "Reading 915MHz Radar Wind Profiler - Moment Data"
	print "This is not NIMA QC'd data, USE CAUTION"
	for file_dir in self.find_files('ncar_iss_915_rwp','prof915mom',aux='true',allow_repeats=False):
		# EACH NETCDF FILE IS AN OBSERVATION!!!
		fname = file_dir.split("/")[-1]
		obtime = calendar.timegm(time.strptime(fname.split(".")[1]+fname.split(".")[2]+"UTC",'%Y%m%d%H%M%S%Z'))
		# ok, begin/end check - these files represent 30 minutes?
		if obtime < self.data.begin or obtime > self.data.end: 
			continue #FIXME - must account for the next couple hours too...
		self.log("Reading",fname,obtime)
		nc = b.NetCDFFile(file_dir)
		# fetch what the missing value is, so we can detect it in the data later
		missing = nc.missing_value
		if variable not in nc.variables.keys():
			print "That is not a valid variable"
			print "Here are the availalbe variables:",nc.variables.keys()
			return False
		else:
			# well, so they did give us a variable, so fetch!
			# thse files have dimensions in both height and time, so
			data = nc.variables[variable].data
			ht = nc.variables['height'].data
			tm = nc.variables['time'].data
			el = nc.variables['elevation'].data # elevation, as in, of the beam
			# now, there are many profiles per file, so we loop through those
			for t in range(len(tm)):
				if missing in data[t]:
					#print "bah! no data"
					continue
				if vertical_only and not el[t] > 89.5:
					continue
				ob_time = obtime + tm[t]
				x.append(ob_time)
				yh = []
				zh = []
				for k in range(len(ht[t])):
					h = ht[t][k]
					if h > max_height: break
					yh.append(h)
					zh.append(data[t][k])
				z.append(zh)
				y.append(yh)
		nc.close()
	z = self.flip2d(z)
	return x,y,z
