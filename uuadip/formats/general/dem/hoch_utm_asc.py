"""
	A non-standard importable processor for ASCII Digital Elevation Models of the format
	provided by sebastian, in UTM coordinates. 

	These files contain no actually referensible information as to precise earthly location, be warned...

"""

import numpy as np

def run(self):
	"""
		This is the standard module, however this package is currently intended to be imported and run on it's own
	"""
	print "Sorry, this package is not currently designed for running via uudewey, please import it and call it's methos individually"

def read(src):
	print "Reading",src
	f = open(src,'r')

	# now set a variable wich will then be contoured

	d = False
	x = False
	y = False
	stats = {}

	curr_y = 0
	nan = float('nan')
	x_set = False
	print 'reading!'
	for line in f:
		if len(line) < 100:
			print line
			p = line.split()
			# record the information
			stats[p[0]] = float(p[1])
			continue
		if type(d) == bool:
			# then it is time to tset d
			x = np.arange(stats['xllcorner'],stats['ncols']*stats['cellsize']+stats['xllcorner'],stats['cellsize'])
			y = np.arange(stats['nrows']*stats['cellsize']+stats['yllcorner'],stats['yllcorner'],-1*stats['cellsize'])
			d = np.empty((stats['nrows'],stats['ncols']))
		curr_x = 0
		#y.append(curr_y)# append the current y index, since we will only go through it once
		# well, this is a data line, each box is def
		for k in line.split():
			
			curr_x += 1
			# fill in the values of x if there are not any saved
			#if not x_set:
			#	x.append(curr_x)
	
			if float(k) == stats['nodata_value']:
				d[curr_y,curr_x-1] = nan
				continue
	
			# well, save the value,
			d[curr_y,curr_x-1] = float(k)
	
		# well, x should have been set at this point
		curr_y += 1
		x_set = True

	return x,y,d

def gridsub(x1,y1,d1,x2,y2,d2):
	"""
		replace values on grid 1 with values from grid 2 where they line up and are not nan
		
	"""
	# start by determining where they overlap, by seeing where the x begins and ends in both
	# then loop through those areas, and check and replace if found
	hrange = [x2[0],x2[-1]]
	vrange = [y2[-1],y2[0]]
	# DETERMINE THE CORRESPONDING COORDINATES FOR EACH GRID TO EACH GRID
	# find x start for d1 and d2
	# REQUIRES A PERFECT GRID IN BOTH!!!
	x1s = -1
	x2s = False
	for x in range(len(x1)):
		if x1[x] == hrange[0]:
			x1s = x
			x2s = 0 # presumably this means the start is here
			break
	if x1s < 0:
		# well, then it appears that x1s is off the edge of the map, so, find the corresponding
		print " initial x dimension is off the map"
		for x in range(len(x2)):
			if x2[x] == x1[0]: # if it equals the lowest value of x1:
				x1s = 0
				x2s = x
	if x1s < 0:
		print "Um, d2 is not located within d1, sorry"
		return d1 # fail nice
	
	# now the same for y
	y1s = -1
	y2s = False
	for x in range(len(y1)):
		if y1[x] == vrange[1]:
			y1s = x
			y2s = 0 # presumably this means the start is here
			break
	if y1s < 0:
		# well, then it appears that x1s is off the edge of the map, so, find the corresponding
		print " initial y dimension is off the map"
		for x in range(len(y2)):
			if y2[x] == y1[-1]: # if it equals the lowest value of y1:
				y1s = 0
				y2s = x
	if y1s < 0:
		print "Um, d2 is not located within d1, sorry"
		return d1 #fail nice

	# well, now we know where to start, so let's go!
	print "starting points: ",x1s,y1s,x2s,y2s
	y2k = y2s
	for y in range(y1s,len(y1)):
		x2k = x2s
		y2k += 1
		# but we still have to check for termination
		if y2k >= len(y2):
			# then we are beyond the end, break (below the lowest value)
			break
		for x in range(x1s, len(x1)):
			# x and y should now be the values of d1 to replace
			x2k += 1
			if x2k >= len(x2):
				break
			if not np.isnan(d2[y2k,x2k]):
				# woohoo, a value! - set the initial value to this
				d1[y,x] = d2[y2k,x2k]

	return d1

def lincross(x0,y0,x1,y1,x,y,d):
	"""
		return a linear cross section of heights between the two points,
		two lists are returned, the values, and the points along the longer axis
	
		start is a tuple (x,y) of the starting point, and end is the same for the end
		d is the gridded dataset for the elevations 
	"""
	out = []

	# first determine the nearest actual coordinates with rounding
	x0 = findkey(x0,x)
	y0 = findkey(y0,y)
	x1 = findkey(x1,x)
	y1 = findkey(y1,y)
	# now calculate the distance traveled in each direction, to get both the equation for the slope
	# and so i can know which is the traversing direction, and which is the searching direction
	dx = x1 - x0
	dy = y1 - y0
	print x0,x1,y0,y1
	#FIXME - if dx or dy are 0, then we may have a problem? 
	if dx > dy:
		# direction = x
		slim = [x0,x1]
		search = x
		traverse = y
		mult = dy/dx #dy/dx
		add = y0 
		func = dvalx
	else:
		# direction = y
		slim = [y0,y1]
		search = y
		traverse = x
		mult = dx/dy #dx/dy
		add = x0
		func = dvaly
	# define the equation to find the instantaneous value along the traversing direction

	# loop, calculate, and round to get the nearest point in the traversing direction
	ds = -1 # for calculating the point
	for s in range(len(search)):
		if s < slim[0] or s > slim[1]:
			continue
		# now we are within the limit
		ds += 1
		t = int(round(add + mult * ds)) # finding the nearest point by rounding
		out.append(func(t,s,d))
		
	return out
	
def dvalx(v1,v2,d):
	return d[v1,v2]

def dvaly(v1,v2,d):
	return d[v2,v1]

def findkey(v,l):
	# a simple function to find the key, however this also finds the closest key
	inc = True
	if (l[0] > l[1]):
		inc = False
	for k in range(len(l)):
		kv = l[k]
		if kv == v:
			# well great! then we just return l
			return k
		# but, it is never that simple
		# check directionality, if descending, use
		if kv > v and inc:
			# then determine which is closer, kv, or l[k-1]
			if k == 0: 
				return 0
			else:
				# now calculate the difference between
				if v - kv > v - l[k-1]:
					return k-1
				else:
					return k
		elif kv < v and not inc:
			# then determine which is closer, kv, or l[k-1]
			if k == 0: 
				return 0
			else:
				# now calculate the difference between
				if v - kv > v - l[k-1]:
					return k-1
				else:
					return k

