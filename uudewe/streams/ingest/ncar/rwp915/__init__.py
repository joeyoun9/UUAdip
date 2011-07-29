#!/usr/bin/env python
"""
	ncar_iss_915_rwp module will read in 915MHz RWP data
"""

import sys,time,datetime,calendar,array,os,math
import numpy as np

import mpl_toolkits.basemap as b

def run (self,max_height=30000,variable='w'):
	# oh its amazing
	x = array.array('i')
	y = []
	u = []
	v = []
	z = [] # in case of backscatter
	print "Reading 915MHz Radar Wind Profiler"
	for file_dir in self.find_files('ncar_iss_915_rwp','prof915h',allow_repeats=False):
		# EACH NETCDF FILE IS AN OBSERVATION!!!
		fname = file_dir.split("/")[-1]
		obtime = calendar.timegm(time.strptime(fname.split(".")[1]+fname.split(".")[2]+"UTC",'%Y%m%d%H%M%S%Z'))
		# ok, begin/end check
		if obtime < self.data.begin or obtime > self.data.end: continue
		self.log("Reading",fname,obtime)
		nc = b.NetCDFFile(file_dir)
		if variable == 'w':
			wdr = nc.variables['wdir'].data
			wsp = nc.variables['wspd'].data
			ht = nc.variables['height'].data
			for key in range(len(wdr)):
				# new observation - initialize holders
				y = [] # inefficient, but effective
				x.append(obtime)
				vh = []
				uh = []
				for k in range(len(wdr[key])):
					h = ht[key][k]
					if h > max_height: break
					y.append(h)
					sp = wsp[key][k]
					dr = wdr[key][k]
					if sp == 9999. or dr == 9999.:
						sp = dr = float('NaN')
					# now they have to be converted to u,v
					vh.append(sp*math.cos(math.radians(dr)))
					uh.append(sp*math.sin(math.radians(dr)))
				u.append(uh)
				v.append(vh)
		else:
			if variable not in nc.variables.keys():
				print "That is not a valid variable"
				print "Here are the availalbe variables:",nc.variables.keys()
				return False
			else:
				# get the backscatter!
				# keys available are snrw,snr1,snr3,snr2,snr4
				snr = nc.variables[variable].data
				ht = nc.variables['height'].data
				for k in range(len(ht)):
					y = []
					x.append(obtime)
					zh = []
					for kw in range(len(snr[k])):
						h= ht[k][kw]
						if h > max_height: break
						y.append(h)
						if variable in ['wspd','wdir'] and snr[k][kw] >= 9999:
							zh.append(np.nan)
						else:
							zh.append(snr[k][kw])
					z.append(zh)
		nc.close()
	if variable == 'w':
		# lastly, you have to flip the u,v arrays, so they are actually shaped right
		u=self.flip2d(u)
		v=self.flip2d(v)
		return x,y,u,v
	else:
		z = self.flip2d(z)
		return x,y,z
