#!/usr/bin/env python
"""
A resource for modifying profile data for plotting on a time series. 
Logically, this takes a time as the primary time, and then plots data from that time

This will also return a small time-keyed scale value list, so that a reference legend may be plotted
in matplotlib this will have to be done as a completely independent subplot, but that is not incredibly complicated

This script does a very simple task, but it is designed to be highly flexible. However, its power is in it's simplicity, so
some logic, such as that of seperating dewpoint and temperature lines is not done here, and thus the logic must be done outside.

As well, the power in this code lies in it's abilit to handle various forms of data, such as temperatures, to relative humidity profiles

June 2011 - Joe Young, U of Utah Atmos. Sci. SLC, UT, USA
"""

# default conversions dictionary, seconds per whole unit of whatever we are talking about, user modifyable if re-passed to the function
default_time_conversions = {
	'tc' : 1000,
	'tf' : 800,
	'rh' : 900,
}

def c2t (self,t,v,var,conversions=default_time_conversions,z=False,offset=False,colorbar_degrees=10,skew_distance=15):
	if z:
		from metcalcs.sounding import skewz
	else:
		skewz = lambda x,y: x # create skewz as a meaningless function
		z = [0 for x in range(len(v))] # create a dummy Z
	if offset:
		# the offset will be an amount in the unit of v, and shows how much we should adjust time
		# OR offset can be a list, in which case, the offset value will be the distance between the point[0] on that list
		if type(offset) == list:
			offset = v[0] - offset[0]
			print offset
		t += offset * conversions[var]
	prof = []
	v0 = skewz(v[0],z[0]) # the first temperature = the first time, t
	for k,val in enumerate(v):
		dt = (skewz(val,z[k]) - v0) * conversions[var] # now we know the dt to be used
		prof.append(t + dt)

	# provide a colorbar dataset!

	# and create skew lines!!
	## colorbar is simply colorbar_degrees away from the core axis
	# prof is now a profile of times valued to the values specified
	return prof

# prof_height is a function which will take a profile, and will return the point above and/or below a certian elevation
def prof_height (self,v,z,length=99999.,bottom=0.):
	# self is the request obj, v is the variable profile, and z are the corresponding heights AMSL
	prof = []
	prof_z = []
	prof_zreal = []
	for k,v in enumerate(v):
		if z[k] - bottom < length and z[k] >= bottom:
			prof.append(v)
			prof_z.append(z[k] - bottom)
			prof_zreal.append(z[k])
	return prof,prof_z,prof_zreal
