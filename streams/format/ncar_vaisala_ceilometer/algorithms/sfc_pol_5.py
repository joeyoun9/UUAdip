#!/usr/bin/env python

from streams.format.ncar_vaisala_ceilometer.algorithms.sfc_pol_4 import alg as sp4
import numpy as np

def alg(self,**ceil_args):
	# start with getting the data from sp4
	hts,v,v2,t,z,m,d = sp4(self,**ceil_args)
	d = self.flip2d(d)
	m = self.flip2d(m)
	# now I want to start by computing a confidence in each value, and if the confidence is high, then pick the bs value at that point
	gradValues = []
	print d.shape,m.shape
	for tm in range(len(t)):
		ht = hts[tm]
		# find the y key assosciated with this height
		for zm in range(len(z)):
			if z[zm] == ht:
				break
		#zm should now be the key in height
		gradValues.append(d[tm][zm])
	mg = min(gradValues)
	outGrad = []
	for val in gradValues:
		pct = (val/mg) * -100. # the percentage of the max negative gradient	
		outGrad.append(pct)
	best_bs_keys = []
	for pct in range(99,39,-10):
		# search through the values to pick out where the gradient percentage is greater than this...
		for g in range(len(outGrad)):
			if outGrad[g] >= pct:
				ht = hts[g]
				for zm in range(len(z)):
					if z[zm] == ht:
						break
				best_bs_keys.append(m[g][zm+2]) # look 1 level above the level we found
	# evaluate these keys with decreasing emphasis as we go down the list...
	# this might be slow
	keys_plot_value = []

	# CREATE AN ISOPLETH AT THE VALUE IN BEST BS KEYS
	for bsval in best_bs_keys:# + [np.mean(m) - np.std(m)]:
		# for each key value, find the line 
		line = []
		for tm in range(len(t)):
			# looping through every time in the plot
			# now we should go up the column until we go above the value
			#bsval = min(m[tm]) + np.std(m[tm])
			for zm in range(len(m[tm])):
				if m[tm][zm] < bsval: # if the backscatter value is less than the key value, go (not concerned about el)
					line.append(z[zm])
					break
			if len(line) <= tm:
				line.append(float('nan')) 
		keys_plot_value.append(line)
	# lastly, pick a single line to follow, weighted by the higher numbers
	for key in range(len(keys_plot_value)):
		pass

	# CALCULATE AN ISOPLETH WITH A BACKGROUND ANALYSIS
	bg_vals = []
	for mul in range(1,150,1):
		bsval = np.mean(m) + (mul/100.) * np.std(m)
		line = []
		for tm in range(len(t)):
			# looping through every time in the plot
			# now we should go up the column until we go above the value
			#bsval = min(m[tm]) + np.std(m[tm])
			for zm in range(len(m[tm])):
				if m[tm][zm] < bsval and z[zm] > 50.: # if the backscatter value is less than the key value, go
					print m[tm][zm],len(m[tm]),zm
					line.append(z[zm])
					break
			if len(line) <= tm:
				line.append(float('nan'))
		bg_vals.append(line)
		
	# and now analyze background vals for the one with the fewest major drops
	# and analyze for mean error compared to hts, calculated from gradients
	ln_info = {'drop_count':[],'uber_alles':[],'outta_da_50s':[]}
	for line in bg_vals:
		ln_info['drop_count'].append({})
		ln_info['uber_alles'].append({})
		ln_info['outta_da_50s'].append({})
		#print 'corr:',np.correlate(hts,line)
		grads = np.gradient(np.array(line))
		ln_info['drop_count'][-1] = 0
		ln_info['uber_alles'][-1] = 0
		ln_info['outta_da_50s'][-1] = 0
		for v in grads:
			if np.absolute(v) > 400.:
				ln_info['drop_count'][-1] += 1
		for k in range(0,len(line),3): # go every 3 to make it a little more efficient...
			v = line[k]
			# compare this with every other line at this point
			for ln in bg_vals:
				ln_info['uber_alles'][-1] += v - ln[k]
		
	print ln_info
	min_drops = min(ln_info['drop_count'][:])
	max_uber = max(ln_info['uber_alles'])
	for l in range(len(bg_vals)):
		if ln_info['drop_count'][l] == min_drops:
			#then this guy is good mins wise!
			best_bg = bg_vals[l] 
			break
		if ln_info['uber_alles'][l] == max_uber:
			best_bg = bg_vals[l]
		
	# create a line that is the max value of the ubers
	max_t = []
	for l in range(len(t)):
		max_t.append(0)
		for ln in bg_vals:
			if ln[l] > max_t[-1]:
				max_t[-1] = ln[l]
			

	# lastly, use the keys_plot_value to factor in our decreasing emphasis
			
		

	# now where the gradient is highest, or at least where it is high, we can identify a backscatter minimum value
	# agains which we can test other profiles
	##print len(keys_plot_value[-1]),len(t),len(best_bg)
	d = self.flip2d(d)
	m = self.flip2d(m)
		

	return hts,best_bg,max_t,t,z,m,d,bg_vals
