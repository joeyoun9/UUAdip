"""
# UTDewey package for processing raw data produced by the NCAR ISFF-ISS Vaisala Celiometer
# current configuration is for the CL31 Ceilometer, and it's raw data format

Created by Joe Young March 2011 
Dept. of Atmospheric Sciences
University of Utah
Salt Lake City, Utah, USA

Created under the NSF funding for the PCAPS project 2010 - 2013
"""

import sys
import time
import datetime
import calendar
import array
import os
import math

import uudewey

# import numpy nicely
try:
	import numpy as np
	from scipy.stats import nanmean,nanstd
except:
	print "This requires NumPy and SciPy to run, please visit numpy.scipy.org to get it"
	sys.exit()
# as with all packages for the UTDewey data system, this should simply be a function that returns 
# the data in the specialized format. Function MUST begin with the data request object (self)
# and the function is to be called 'run'
def run (self, ddz=False, average=False, span=10, compute_raw=True, box_average=False,upper_limit = 1e6, 
		lower_limit=1, max_height=3500, ceil_buffer=300, scaled=False, 
		make_file=False, make_file_name="ceilometer_raw.DAT", make_file_raw=False,still_plot=False,
		ddz_extra=False,clouds=False,no_bs=False,exp_filter=False,nans2val=False,nm=False,nm_pct=30,
		plot_levels=45, stdev=False, minimum=False):
	#FIXME return the computed cloud heights too!!!
	# this one is going to be a haus to process, but not too much code
	# read in the ceilometer data files and parse them to being within the times needed
	# then return them in a consistent format
	#################### Operation specifics, before we get started
	#	1. this will determine the files within the time range (that contain the data)
	#	2. files will be read, and each 'point'/observation within the date range will be recorded
	#	3.a if averaging is on, then means will be calculated
	#	3.b if ddz is on, then ddz will be calculated, if neither is on, raw will be returned
	#	4. data is returned as a triplet of X(times),Y(heights),Z(values); Z is a len(x)*len(y) array
	# 1) - PLUS - the mean values and d/dz values are returned. 
	#	5. IF SPAN - the X values will correspond to jumped span values, and not to the Z values

	X = array.array('i')
	times = array.array('i') # with no span, this will be the same as x, but it will be deleted soon
	Z = []
	self.data.set('cl31',uudewey.RequestDataObject())
	current_bin = 2
	nm_pct = float(nm_pct) / 100.
	if span:
		span = float(span)
		# spans are bins of [span] minutes, so create the bins span minutes apart
		span_index = array.array('i')
		# calculate the begin and end times for every bin? - begin at self.data.start, no buffer time
		span_time = self.data.begin + span*60. / 2. # we need the spans to be defined as the middle of the bin...
		# a span should be defined at beginning and end if we are not printing this out, because then it will plot all the way to the edge
		if not make_file:
			# also declare a buffer of 1/2 span*60 to have a full average
			ceil_buffer = span*60. / 2.
			X.append(self.data.begin)
			Z.append([])
		while span_time < self.data.end:
			# create a bin identified by the span_time - this will be rounded to the nearest integer if necessary
			# FIXME - make times floats
			X.append(int(span_time))
			Z.append([]) #np.array([],ndmin=2) # obesrvations are each a key (obtime) which has a array.array('f') as the value
			span_time += span * 60.
		# as well, if we are not printing, then make a span box at the end as well!
		if not make_file:
			X.append(self.data.end)
			Z.append([])
	
		#########span_time = ( span / 2 ) * 60 + self.data.begin - ceil_buffer
	if clouds:
		# we are collecting cloud info, so set the variable!
		self.data.cl31.set('clouds',{1:{},2:{},3:{}})
	Y = array.array('f')
	y_ed = False
	GATE_HEIGHT = 10 #m #FIXME THIS IS SPECIFIC TO THIS CEILOMETER FOR PCAPS, READ FILE FOR MORE GENERIC
	TILT_DEG = 1	#degreees #FIXME THIS IS SPECIFIC TO THIS CEILOMETER, SO READ FILE TO BE MORE GENERIC
	SCALING_FACTOR = 1e9 #scale applied to the values from the ceilometer
	if not scaled:
		lower_limit = lower_limit / SCALING_FACTOR
		upper_limit = upper_limit / SCALING_FACTOR
	obCount = 0 # this will count the lines in case ther is a span specified, see the note above X.append(...)
	now_bin = False
	for file_and_dir in self.find_files('ncar_iss_vaisala_ceilometer','.DAT',allow_repeats=False):
		# grab the date from the file:
		fname = file_and_dir.split("/")[-1]
		if '.swp' in fname : continue # avoid opening swp files...
		ftime = calendar.timegm(time.strptime("201"+fname[1:-4]+"UTC","%Y%m%d%H%Z"))
		start = False
		# files last for 6 hours, so if the end of the file is within the time, then it is still good
		if ftime + 6*3600+ceil_buffer < self.data.begin or ftime > self.data.end+ceil_buffer:
			continue
		print "Reading file: ",fname
		# well now we need to process each one of these files, only for the obs within the time though
		for line in open(file_and_dir).readlines():
			if not len(Y) == 0: y_ed = True # set it so we dont rewrite Y
			if len(line) < 900:
				if "-20" in line:
					info_lines = []
					#obTime = md.date2num(datetime.datetime(int(line[1:5]),
					#	int(line[6:8]),int(line[9:11]),int(line[12:14]),
					#	int(line[15:17]),int(line[18:20]))) #HHMMSS
					obtime = calendar.timegm( [ int(line[1:5]) , int(line[6:8]),
						int(line[9:11]) , int(line[12:14]) , int(line[15:17]),
						int(line[18:20]  ) ] )
					obtime = calendar.timegm(time.strptime(line.strip()+"UTC","-%Y-%m-%d %H:%M:%S%Z"))
					tm = line
					#  NOTE: THERE IS A [X] BUFFER ON EACH END OF THIS DATA
					# now we need to check if the obtime is within the time/date range
					if obtime < self.data.begin - ceil_buffer:
						# then we need to keep going until we are ready!
						start = False
					# check if we are at the end...
					elif obtime > self.data.end + ceil_buffer: break # stop going through this file...
					else: 
						start = True
						times.append(obtime) 
						
						# if span, we are simply going to break the entire period into bins 
						# [span] minutes in duration, beginning at self.data.begin
						if span:
							now_bin = 0 if not now_bin else now_bin
							# figure out what bin we are currently in!
							for i in range(current_bin - 1,lenr(X)): # it is somewhere betweent the current length of Z and the length of X
								if obtime >= X[i] - (span / 2.) * 60. and obtime < ( X[i] + (span/ 2.) * 60. ) :
									# this should never go on for too long...
									now_bin = i
									break
							# to avoid double running with the buffer bins
							#if now_bin == -1 and lenr(Z) > 1: break # we are done?
							# for logging purposes, make it so...
							if not now_bin == current_bin:
								self.log("span",now_bin,'of',len(X) - 1,obtime)
							current_bin = now_bin

							# thus the current location for depositing observations is Zi[current_bin][ob]
							# we can append this ob on (so it is key -1) so it can be simply written to

							Z[current_bin].append(array.array('f'))
									
								#self.data.ceil.clouds[1][current_bin].append(float('nan'))
								#self.data.ceil.clouds[2][current_bin].append(float('nan'))
								#self.data.ceil.clouds[3][current_bin].append(float('nan'))
							###span_time = span * 60 + obtime
							###span_index.append(len(times) - 1)
							##X.append(obtime) - obtime is appended at the beginning with an idealized bin profile
						elif not span:
							current_bin = -1 #len(X)
							X.append(obtime)
							Z.append([])
							Z[current_bin].append(array.array('f'))
						obCount += 1
						if clouds:
							# append a new bin holder on to the clouds array
							if current_bin not in self.data.cl31.clouds[1].keys():
								# well then we need to make the darn bin
								self.data.cl31.clouds[1][current_bin] = []
								self.data.cl31.clouds[2][current_bin] = []
								self.data.cl31.clouds[3][current_bin] = []

				if not start: continue
				# for now, we just append these guys to a list``
				info_lines.append(line)

               			continue
			if not start: continue

			#DATA LINE!! #######################################################

			# first analyze the info_lines
			if clouds:
				# get cloud information!
				cl = info_lines[2].split() # the third line is always cloud info
				layers = int(cl[0][0]) if not cl[0][0] == "/" else 0
				if layers == 0: 
					pass
					##SUSPECT OBSERVATION - pop a value from [b?]
					#Z[current_bin].pop(-1)
					#continue
				else:
				 for layer in range(3):
					# read up to layer X
					if layer + 1 <= layers and layers < 4:
						# good layer, fetch!
						self.data.cl31.clouds[layer+1][current_bin].append(float(cl[layer+1]))
					elif layers == 4:
						# full obscuration, no cloud layers
						self.data.cl31.clouds[1][current_bin].append(0.)
						self.data.cl31.clouds[2][current_bin].append(float('nan'))
						self.data.cl31.clouds[3][current_bin].append(float('nan'))
						break # break looping through layers
					else:
						# bad layer, add a nan
						self.data.cl31.clouds[layer+1][current_bin].append(float('nan'))
			if no_bs:
				# if we are not reaturning backscatter, then move along!
				continue
			# so, supposedly this is now a data line!
			# break it up into its 5-character elements, and get to work :)
			i = 0

			#holder = array.array('f') - no more need for the holder...
			while i < len(line):
				val = line[i:i+5]
				key = i/5
				i+= 5
				if len(val) < 5:
					continue
				# I dont care when the key is greater than 350, so break!
				if key*GATE_HEIGHT > max_height:
					break
				val = int(val,16)
				# IF SCALED = TRUE, THEN WE LEAVE IT, ELSE WE NEED TO UNSCALE THIS VALUE, DIVIDE BY 10^9
				if not scaled:
					val = float(val) / SCALING_FACTOR
				# millions values really look like noise
				if val < lower_limit or val >= upper_limit: # cut it off if it is greater than 4.5
					val = lower_limit # give it a value of .8
				# to plot we want to use log10 of this value, but for now we will store raw

				Z[current_bin][-1].append(val)
				if not y_ed:
					Y.append(key * GATE_HEIGHT)
			#Zi.append(holder)
			start = False # this stos me from adding extra info to info lines...

	# convert the bins to lists in the clouds
	if clouds:
		for h in range(1,4):
			holder = []
			for b in range(lenr(Z)):
				holder.append([])
				for v in self.data.cl31.clouds[h][b]:
					holder[-1].append(v)
				# now calculate the mean from holder:
				if len(holder[-1]): #float('nan') in cloud_bin:
					val = float('nan') # start with the default - the median value
					su = 0
					su_cnt = 0
					for value in holder[-1]:
						if not np.isnan(value):	
							su += value
							su_cnt += 1
					val = su/su_cnt if su_cnt / len(holder[-1]) > .2 else val # ie, get the average, if more than 20% of the values are not nan
					holder[-1] = val * 0.3048 #height is given in feet...
				else:
					holder[-1] = float('nan')

			self.data.cl31.clouds[h] = holder
			

	if no_bs:
		# if there is no backscatter requested, then we are done... return the value X since that is the key of clouds...
		return X
	# for each bin, go through each height, and average it if !ddz, we will think of that one later
	out = np.zeros((lenr(X),lenr(Y))) # this is the return value, we only return one, so it best be good.
	if ddz_extra:
		out2 = np.zeros((lenr(X),lenr(Y)))
	
	if not compute_raw or ddz:
		print "computing log10 of Z"
		for b in range(lenr(Z)):
			Z[b] = np.log10(Z[b])

	# loop through the bins - for everyhing
	print "Averaging and whatnot"
	for b in range(lenr(Z)):
		da_bin = Z[b]
		self.log("processing bin",b)
		# now da_bin is the bin, which contains a series of profiles, averaging should be done in whatever form is necessary
		# result is a profile that should be appended to out, which will correspond to the time in X
		if len(da_bin) == 0:
			for i in range(lenr(Y)): 
				out[b][i] = float('nan') #-999 # set it equal to an entire -999 profile #FIX - set equal to nan
			continue # move on to the next bin
		# loop through Z, which should be the same size as da_bin[0], but why risk it. 
		for z in range(lenr(Y)):
			# logically, we go up the bin!
			# now define the vertical range we want, and grab all the values
			values = []
			for i in range(lenr(da_bin)):
				# logically we then go across the bin!
				if box_average and box_average > 0:
					for j in range(z - box_average if z > box_average else 0, z + box_average if z + box_average < lenr(Y) else lenr(Y)):
						values.append(da_bin[i][j])
					"""
					elif ddz and ddz > 0:
						# we are calculating the gradient over length ddz
						# append to the values, the value of the vertical gradient!
						top = z + ( ddz + ddz % 2 ) / 2
						bottom = z - ( ddz + ddz % 2 ) /  2 
						if top > len(Y) - 1: top = len(Y) - 1
						if bottom < 0: bottom = 0
						val  =  ( da_bin[i][top] - da_bin[i][bottom] ) / ddz * GATE_HEIGHT # d/dz === delta val / delta z
						values.append(val)
					"""
				else:
					values.append(da_bin[i][z])
			if len(values) == 0:
				out[b][z] = -999
			else:
				# compute the mean!! - use various techniques to do this...
				if not nm and not stdev and not minimum:
					out[b][z] = sum(values)/len(values)
				elif minimum:	
					# experiment!!
					out[b][z] = min(values)
				elif stdev:
					# first check if there are any nans in the list, if not, then just return the standard mean
					if np.isnan(lower_limit):
						anan = False
						for v in values:
							if np.isnan(v):
								anan = True
								break
						if not anan:
							out[b][z] = sum(values)/len(values)
							continue
					# ah, so now we know that a nan is present
					stv = nanstd(values)
					# now there should be a certain value, that should the standard deviation exceed it, the data is too variable
					if stv > 5e-7: #FIXME - find a proper value for this!!
						out[b][z] = np.nan
						continue
					# now we know that it does not deviate too much, so check the list for outliers, if a value is an outlier, do not mean it
					# sadly the mean must be computed to do this
					mn = nanmean(values)
					values2 = []
					for v in values:
						if not np.isnan(v) and math.fabs(v - mn) < 2.*stv:
							# it is not an outlier
								values2.append(v)
					if len(values2) < 1: out[b][z] = np.nan
					else:
						out[b][z] = sum(values2)/len(values2)
					# FIXME - in the future test for sample size, and if big enough, perhaps do some evaluations of distribution
				else:
					# use nanmean to compute the mean for the gate
					if nm_pct:
						# this input variable determines if we should still nan it if there is a pct > nm_pct
						# of nans in the value
						# sadly, we gotta loop through values
						c_need = nm_pct * len(values)
						c = 0
						for v in values:
							if np.isnan(v): c +=1
							if c >= c_need:
								out[b][z] = np.nan
								break
						
						if c < c_need:
							out[b][z] = nanmean(values)
					else:
						out[b][z] = nanmean(values)

		# now before we leave this column, if ddz is mandated, calculate it quickly and efficiently
		if not ddz and not ddz > 1:
			continue
		if not ddz_extra:
			out[b] = swap_inf(np.gradient(out[b]),1e11)
		else:
			out2[b] = swap_inf(np.gradient(out[b]),1e11)
			
	# //// IF MAKE_FILE HERE IS WHERE WE DO IT - since the Zi is exactly what we want to save, even in that order
	# makefile will use the raw data, scaled or unscaled as specified, so write it, save it, and return True on success
	if make_file:
		print "Creating Output File"
		# check if the location exists
		if not make_file[-1] == "/":
			make_file = make_file + "/" # ensure there is a / at the end - it must be a directory!
		if not os.path.exists(make_file): 
			print "Um, your make_file directory:",make_file,'doesn\'t exist, please make it '
			return False
		# create the file 
		text = 'NaN'
		t = 0
		# text's first row should be a list of heights, but starting with a blank
		self.log("inserting height keys")
		for x in Y:
			text += ','+str(x)
		text += "\n" # newline for the start of data rows
		# now if there is a span, we have to use Z_m
		if make_file_raw and not span:
			##want = flip2d(out) # can only print a raw file if a span is not calculated
			# convert logarithmic values back into non-log
			want = np.power(10,out)
		elif make_file_raw:
			##want = flip2d(out)
			want = out
			if not compute_raw or ddz:
				want = np.power(10,out)
		else:
			# not make file raw
			want = out
			if compute_raw:
				want = np.log10(out)
		self.log("Compiling data into file")
		for key in range(lenr(want)): #tm_l in want:
			# this is the beginning of a time, so put the time at the beginning of the line
			tm_l = want[key]
			text += str(X[key] + 60 * span) # give the time as the end of the period
			z = 0
			for ht_v in tm_l:
				# this is the raw number, for the line - convert to string and save
				text += ','+str(ht_v)
			text += "\n" # newline, since we are done with this height
		#del want,Z,Z_m,Z_d,X,Y
		self.log("Writing File")
		f = open(make_file+make_file_name,'w')
		f.write(text)
		f.close()
		if not still_plot:
			return True
	#//// End of Make_file //////

	# compute the logbase 10 of Z, and return as many as were requested
	if compute_raw and not ddz:
		print "computing log10 of Z"
		out = np.log10(out)
	print "returning values"



	if exp_filter:
		print "Running Experimental Value Filter"
		# the experimental filter, is a process by which we evaluate each individual profile
		# and 'remove' data that appear to be bad. This works best when data is otherwise unfiltered
		# (time averageing is ok, and generally helps)
		z = out #self.flip2d(out) out is already in a nice format!
		out = []
		for pro in z:
			out.append(array.array('f'))
			# pro is the profile
			d = np.gradient(pro)
			for key in range(len(pro)):
				# for every value, check some things
				dd = math.fabs(d[key])
				v = pro[key]
				if dd > 1. or v > -4.1:
					out[-1].append(float('nan'))
				else:
					out[-1].append(v)
	if not nans2val == False:
		"""
		This optoin allows the user to convert NaN values into the value of their choosing, nominally 0
		"""
		print "Converting NaNs to",nans2val
		z = out
		out = []
		for p in z:
			out.append(array.array('f'))
			for v in p:
				v = nans2val if np.isnan(v) else v
				out[-1].append(v)

	# Convenience information - return a variable which contains the plotting levels for the ceilometer plots
	# values on the plot should range from -8.7 to -4.3 - ah ah ah, 01 dec 2010 - 01-02utc, values >-4.3
	high_v = -4.0
	low_v = -8.7
	if ddz and not ddz_extra:
		maxs = mins = []
		for b in out:
			maxs.append(max(b))
			mins.append(min(b))
		high_v = max(maxs)
		low_v = min(mins)
	inc = np.absolute(high_v - low_v) / plot_levels
	self.data.cl31.set('plot_levels',[low_v + x*inc for x in range(plot_levels)])


	if ddz_extra:
		re = X,Y,flip2d(out),flip2d(out2)
	else:
		re = X,Y,flip2d(out)
	# clouds are returned to the data object, so no need to return further...
	return re




# define a flipping function, sice I seem to use it somewhat frequently - can be imported elsewhere as well!
def flip2d(wrong):
	right = np.zeros((len(wrong[1]),len(wrong))) # since Z is always full, but X can vary with the span parameter, it is best to use obCount
	i = 0
	for r in wrong:
		c = 0
		for v in r:
			right[c][i] = v
			c+=1
		i+=1
	return right

def lenr(x):
	return len(x)

def swap_inf(l,v):
	o = []
	for lv in l:
		if lv > v or lv < -1*v:
			o.append(np.nan)
		else:
			o.append(lv)
	return o
