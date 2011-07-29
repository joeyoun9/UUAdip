#!/usr/bin/env python

import streams.ingest.ncar_vaisala_ceilometer as c
from streams.format.ncar_vaisala_ceilometer.algorithms.sfc_pol_3 import alg as sp3
import numpy as np
# PYTHON algorithm for extracting pollution depth from ceilometer datas

# gaussian smoother from swharden.com blog
def smoothListGaussian(list,strippedXs=False,degree=5):  
     window=degree*2-1  
     weight=np.array([1.0]*window)  
     weightGauss=[]  
     for i in range(window):  
         i=i-degree+1  
         frac=i/float(window)  
         gauss=1/(np.exp((4*(frac))**2))  
         weightGauss.append(gauss)  
     weight=np.array(weightGauss)*weight  
     smoothed=[0.0]*(len(list)-window)  
     for i in range(len(smoothed)):  
         smoothed[i]=sum(np.array(list[i:i+window])*weight)/sum(weight)  
     return smoothed 



def alg(self,ret=True,**ceil_args):
	# algorithm 4 just runs the whole dillio itself
	x,y,m = c.run(self,**ceil_args)
	# this algorithm will use numpy's gradient calculation to determine a first minimum
	m = self.flip2d(m)
	d = []
	d2 = []
	d3 = []
	for p in m:
		d.append(np.gradient(p))
		d2.append(np.gradient(d[-1])) # compute 2nd derivative
		d3.append(np.gradient(d2[-1])) # compute 3rd derivative
	
	# now i want to swype up, pick some strong points, and then swype back down
	zs = [[],[]]
	for p in range(len(d)):
		# first go up!
		zm = 0 # maximum height
		gm = 0 # maxumum gradient
		for z in range(len(d[p])):
			if y[z] < 55: continue
			# look for the maximum negative gradient value:
			g = d3[p][z]
			g2 = d2[p][z]
			if g > gm and np.absolute(g2) < .1: #max postive 3rd deriv. and nearly 0 2nd derivative
				# this is the most negative value
				zm = z
				gm = g
			# as a small vertical test, should the backscatter ever exceed -5.5, we are done
			# or if the vertical height is greater than 2000m
			if m[p][z] > -5.8 or m[p][z] < - 7.7:
				# limits are 2000m, -5.8 (high), and -7.7 low
				break
			
		# then go down! (starting from 500m above zm)
		gm2 = 0 # second gradient record
		zm2 = 0 # second elevation record
		start_z = zm+2 if zm+2 < len(d[p]) else len(d[p]) - 1
		for z in range(start_z,0,-1):
			if y[z] < 55: continue
			g = d[p][z]
			if g < gm2:
				zm2=z
				gm2=g
			# no vertical checks necessary
		zs[0].append(y[zm])
		zs[1].append(y[zm2])

	# now for giggles, i want to do a gaussian smooth of zs[0]
	l = smoothListGaussian(zs[0])


	print len(l)	

	return l,zs[0],x,y,self.flip2d(m),self.flip2d(d)
