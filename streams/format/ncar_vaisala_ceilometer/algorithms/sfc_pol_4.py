#!/usr/bin/env python

import streams.ingest.ncar_vaisala_ceilometer as c
from streams.format.ncar_vaisala_ceilometer.algorithms.sfc_pol_3 import alg as sp3
# PYTHON algorithm for extracting pollution depth from ceilometer datas


def alg(self,ret=True,**ceil_args):
	# algorithm 4 just runs the whole dillio itself
	x,y,m,d = c.run(self,ddz_extra=True,**ceil_args)
	# algorithm 4, will use algorithm 3 as a first guess, and then run again 
	# takes the top 5 values of alg3 to define the height range for the next ones
	junk,hts = sp3(self,d,x,y)
	# pick out the top 5 values
	maxs = []
	max_pts = []
	hts_max = []
	for i in range(5):
		val = max(hts)
		max_pts.append(val)
		for k in range(len(hts)):
			if hts[k] == val:
				maxs.append(k)
				hts.pop(k)
				break
	# now we have the top 5 values
	ave = sum(max_pts)/len(max_pts)
	newm = self.flip2d(d)
	# now, as a bad assumption, ave is the new range +/- 400m is where we search, top down now
	for t in range(len(x)):
		p = newm[t]
		max_v = 100
		ht_v = 0
		for k in range(150): # start at 1500m...
			z = 150 - k - 1 # go backwards!
			el = y[z]
			if len(hts_max) > 0 and (el > hts_max[-1] + 400  or el < hts_max[-1] - 400): continue
			val = p[z]
			if val < max_v:
				max_v = val
				ht_v = y[z]
		hts_max.append(ht_v)
	return hts_max,maxs,max_pts,x,y,m,d
			

