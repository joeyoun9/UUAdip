#!/usr/bin/env python
"""
A resource for converting between RASS timeseries, and temperature profiles
Joe Young - June 2011
Dept. of Atmospheric Sciences, Univ. of Utah, SLC, UT, USA
"""

from scipy.stats import nanmean

def r2p (self,span,T,Z,V):
	"""
	Function to do the work, reiqres a defined function as the file is just a module, __init__() doesn't cut it
	
	inputs:
	
	self	:	the request obeject profiles will be saved to
	span	:	the amount of time, in minutes, between profiles
			proiles are thus an average of the other values, and thus this is the averaging length.
			Times of plots are the middle of the indicated averaging period.
	T,Z	: 	time and height
	V	:	2-D array of values for the specified time and height.
	
	It is valid to note that this processing could be done more easily by the ingestor, 
	however for expandability, this is the method used. someday a version will be written that can be used by the ingestor
	"""

	
	# like the ceilometer, start by defining bins based on the start and end times
	# these bins will begin at start time, and the last bin may be abbreviated
	time = float(self.data.begin)
	bins = {}
	span = float(span) * 60. # span is in minutes, convert it to seconds so it makes sense with epoch
	span_fr = span / 2.
	while time < self.data.end:
		bins[time + span_fr] = []
		time += span

	# bins are defined, now put the profiles within the bins!
	V = self.flip2d(V)
	for t in range(len(T)):
		# loop through all profile times
		time = T[t]
		# identify the bin this time falls into
		for b in bins.keys():
			if b + span_fr > time and b - span_fr <= time:
				break
		# now b is the key! - append the vertical profile to the bin!
		bins[b].append(V[t])
	
	# and now average the bins, and produce a final value
	self.data.set('rass_prof',[])
	for t,b in enumerate(bins):
		self.log('averaging bin',t)
		if len(bins[b]) == 0:
			continue # do not save a profile!

		self.data.rass_prof.append({})
		prof = []
		for z in self.flip2d(bins[b]):
			# looping through the entire list of b, level by level
			val = nanmean(z)
			prof.append(val)
		self.data.rass_prof[-1]['tv'] = prof
		self.data.rass_prof[-1]['init'] = {'time': b}
	
