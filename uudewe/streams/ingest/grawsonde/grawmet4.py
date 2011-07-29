"""
# UTDewey package for processing Graw Rawinsondes, both from processed files, and raw GD and GDP files
# current configuration is for both raw computation, as well as reformatting of processed files
# as well, processed files are not always of the same format, so this compensates for the various formats

Created by Joe Young March 2011 
Dept. of Atmospheric Sciences
University of Utah
Salt Lake City, Utah, USA

Created under the NSF funding for the PCAPS project 2010 - 2013
"""
import sys,time,datetime,calendar,array,math
from math import degrees, atan2
from time import strftime, gmtime
from metcalcs.sounding import sounding_dewpoint


# as with all packages for the UTDewey data system, this should simply be a function that returns 
# the data in the specialized format. Function MUST begin with the data request object (self)
# and the function is to be called 'run'

def run (self, site=False, proc=False, wind_averaging=20, cutoff=True):
	num = -1
	print "Grabbing Graw soundings"
	# initialize the output array, which for now will be a simple list of lists
	self.data.set("graw_soundings",[])
	if site:
		site = site.lower().replace(' ','')
	self.data.set("site",site)
	if not self.data.site:
		print "Just FYI, you didnt specify a site, so you are going to get everything within the date range"
	
	if proc:
		# just grab the list of proc files once, so we dont do it too many times
		proc_files = self.find_files('graw_rawinsondes','txt',aux=True) # i didnt want to do the .txt restriction, but no binaries
		processed_files = {}
		for f in proc_files:
			#FIXME - if there is a way to save this information, or go through the files only once, that would be better
			# read the first line in the file, if it has the sonde id, this is our file!
			fl = open(f)
			ln = fl.readline().strip().split()
			processed_files[ln[-1]] = f
			#if sonde in fl.readline(): # check the first line for this sonde number
			#	found = True
			#	break
			#else:
			fl.close()
	for file_loc in self.find_files('graw_rawinsondes','.GD',allow_repeats=False):
		fname = file_loc.split("/")[-1]
		if not fname[-2:] == "GD":
			continue
		# now we need to check the date range, and make sure we have an ob at the specified time
		date = fname[0:12]
		ftime = calendar.timegm(time.strptime(date+"UTC","%Y%m%d%H%M%Z"))
		if ftime > self.data.end or ftime < self.data.begin:
			continue
		# line 2[0] of the GD file lists the station name, so we need to scan this for any possible
		# agreement
		gd_lines = open(file_loc).readlines()
		### --- SMALL QC, IF THIS FILE / IF LEN(GD_LINES) IS LESS THAN ~1000, ITS A BAD SOUNDING FILE
		if len(gd_lines) < 1000:
			print "Uh oh, GD file of < 1000 lines, it is bad, skipping"
			continue
		fsite = gd_lines[1].split("    ")[0].lower().replace(' ','') # lowercase and no spaces for the search
		if self.data.site and self.data.site not in fsite:
			continue
		# --- WE HAVE DECIDED TO OPEN AND PROCESS THIS SOUNDING - PRINT THE FILE NAME --- 
		print fname # just so you can check on the progress :)
		num = len(self.data.graw_soundings)
		self.data.graw_soundings.append({}) # append a new sounding dictionary!
		## -- here is the great fissure between the processed and the raw soundings!!! --#
		######## ------------------------------ PROCESSED SOUNDINGS WILL BE READ HERE --------------###
		if proc:
			sonde = fname[12:-3]
			t_l = []
			td_l = []
			rh_l = []
			p_l = []
			tv_l = []
			t_l = []
			ln_l = []
			lt_l = []
			z_l = []
			tm_l = []
			dir_l = []
			spd_l = []
			gp_l = [] #geopotential alt
			rs_l = [] # vertical speed [m/min]
			# we must scan the text files for this sounding id in line 1
			if not sonde in processed_files:
				print "I could not find a txt file for that sounding, sorry"
				continue # move on to the next sounding...
			f = processed_files[sonde]
			# woohoo, we have found our file!
			fl = open(f)
			print "file: ",f
			key = -2 # moved since this was coded with the first line having been removed, which is no longer the case
			threshold = 0
			elv = 0
			tv = 0
			rs = 0
			for line in fl.readlines():
				key += 1
				l = line.split()
				if key == 4:
					alt_i = float(line.split()[-1])
				# since these festive processed files can vary with their formatting, we must check
				# it seems that it is always time, pres, temp, rh, wsp, wdir, lon, lat, and then it goes kerfufle
				if key == 9: 
					header = [] # saving the header line to check
					di = 14 ## PLEASE LET THIS BE THE ONLY DELIMING DISTANCE!!
					i = 0
					while i < len(line):
						header.append(line[i:i+di])
						i+= di
				if key < 11 or len(l) < 11: continue 
				# now we are on a data line, check for the cutoff, but thats all
				if "---" in line: continue # bad data point
				tm = float(l[0].split(":")[0]) * 60 + float(l[0].split(":")[1]) if ":" in l[0] else float(l[0])
				p = float(l[1]) # I am now changing it to hPa
				tc = float(l[2])
				rh = float(l[3])
				if "m/s" in header[4]: wsp = float(l[4])
				elif "kn" in header[4]: wsp = float(l[4]) * 0.51444
				else: wsp = 0
				wdir = float(l[5])
				lon = float(l[6])
				lat = float(l[7])
				z = float(l[8]) + alt_i # since I like ground relative!
				gp = float(l[9]) # geopotential altitude
				# cutoff check, 
				if threshold > 5: break # if there are more than 5 times that the height is downward, we are done
				if elv > z:
					# this means that there is downward movement!
					threshold += 1
				elv = z
				# now it can get variable, there are things called MRI and RI that I want to avoid
				r = len(header)
				while r > 1:
					r-=1
					k = header[r]
					if "Dew" in k:
						tdc = float(l[r])
					elif "Vi Te" in k:
						tv = float(l[r])
					elif "Rs" in k:
						rs = float(l[r])
				# hopefully we have all those variables now :)
				t_l.append(tc)
				td_l.append(tdc)
				rh_l.append(rh)
				p_l.append(p)
				if tv: tv_l.append(tv)
				lt_l.append(lat)
				ln_l.append(lon)
				z_l.append(z)
				tm_l.append(tm)
				dir_l.append(wdir)
				spd_l.append(wsp)
				gp_l.append(gp) #geopotential alt
				if rs: rs_l.append(rs) # vertical speed [m/min]
				
			fl.close()
			# now append them to data.graw_soundings[num]
			self.data.graw_soundings[num]['time'] = tm_l
			self.data.graw_soundings[num]['keys'] = range(len(tm_l))
			self.data.graw_soundings[num]['tc'] = t_l
			self.data.graw_soundings[num]['tdc'] = td_l
			self.data.graw_soundings[num]['rh'] = rh_l
			self.data.graw_soundings[num]['tv'] = tv_l
			self.data.graw_soundings[num]['rs'] = rs_l
			self.data.graw_soundings[num]['gp'] = gp_l
			self.data.graw_soundings[num]['p'] = p_l
			self.data.graw_soundings[num]['wdir'] = dir_l
			self.data.graw_soundings[num]['wspd'] = spd_l
			self.data.graw_soundings[num]['lat'] = lt_l
			self.data.graw_soundings[num]['lon'] = ln_l
			self.data.graw_soundings[num]['z'] = z_l
				
			# now we command this to be done, and not process further, move on to the next sounding
			continue
		# now is where we begin processing the sounding...
		gdp_lines = open(file_loc+"P").readlines()
		init = [gd_lines[2].split("     ")[0]+gd_lines[3].split("    ")[0],
			float(gd_lines[6].split()[1]),
			float(gd_lines[6].split()[0]),
			float(gd_lines[6].split()[2]),
			float(gd_lines[8].strip().split()[0])* 100.,fsite]
		init_ob = [0, float(gd_lines[8].split()[1]),float( gd_lines[8].split()[2] ),[init[1],init[2],init[3]]] # tm, tc, rhi
		init.append(init_ob) # stick this on the end for the pressure calculations
		init[0] = calendar.timegm(time.strptime(init[0]+"UTC","%d.%m.%Y%H:%M:%S%Z"))
		self.data.graw_soundings[num]['init'] = init
		
		# now looping through, we want to detect launch, sadly, I have no idea what the time is relative
		# to the launch or to the initialization. We will computee the seconds elapesed for now
		# use the GDP file elevation information to learn where the launch began, via GPS
		gps = array.array('f')
		gps_2 = []
		dat = []
		el_av = [0,0]
		launched = False
		key = -1
		for ln in gdp_lines:
			key += 1
			l = ln.split()
			if len(l) < 10 or not ln[-3].isdigit(): continue
			tm = float(l[0])*60. + float(l[1])
			# ERROR CHECKING  - if the ob is clearly bad, then skip it!
				# skip if it is lower than the initalized elevation, though that can be just as bad...
			if float(l[-1]) < init[3] or not self.in_lat(float(l[-2])) or not self.in_lon(float(l[-3][-11:])): continue 
			# now we need to identify where the launch time is!
			if not launched:
				# check if ftime + tm == init[0] as the file time may be the 'start' time!
				if ftime + tm >= init[0] - 40: # 10 seconds before init
					launched = True
					launch_delay = tm
				else: continue
				# BACKUP / AUXILIARY PROCESSING METHOD - IF THE PREVIOUS DOESN'T APPEAR TO DO A GOOD JOB
				# I like using elevation, if the elevation changes by more than 10m (disregarding any values lower than init[3])
				# lets try looking 4 or 5 into the future, if they are all increasing, then we are launching!
				p1 = float(gdp_lines[key + 1].split()[-1]) # this one has already been checked
				p2 = float(gdp_lines[key + 2].split()[-1]) if float(gdp_lines[key+2].split()[-1]) > init[3] else p1 + 01
				p3 = float(gdp_lines[key + 3].split()[-1]) if float(gdp_lines[key+3].split()[-1]) > init[3] else p2 + 01
				p4 = float(gdp_lines[key + 4].split()[-1]) if float(gdp_lines[key+4].split()[-1]) > init[3] else p3 + 0.1
				p5 = float(gdp_lines[key + 5].split()[-1]) if float(gdp_lines[key+5].split()[-1]) > init[3] else p4 + 0.1
				if p1 < p2 and p2 < p3 and p3 < p4 and p4 < p5:
			#	el = float(l[-1])
			#	el_av[0] += el
			#	el_av[1] += 1
			#	ave = el_av[0]/el_av[1]
			#	#theory: if the value is more than 10 > than the average, then we have launched?!
			#	if el - ave > 10:
					launched = True
					launch_delay = tm
				else: continue	
			#el_p = el
			gps.append(tm)
			#FIXME if the raw data does not follow this pattern of vvel-lng then we need to recal
			lat = float(l[-2])
			lon = float(l[-3][-11:]) # this column seems to be pegged to the vertical acceleration
			elev = float(l[-1])
			gps_2.append([lat,lon,elev])
		#gdp_lines.close()
		del gdp_lines
		# now we do something that seems inefficient, but actually its not bad
		key = -1 # so i can add at the beginning, instead of at teh end
		almost_there = [] # this list will be the ALMOST final version (what's memory???)
		line = -1
		recent_ave = []
		for ln in gd_lines:
			line += 1 
			l = ln.split()
			if not len(l) == 6 or not ln[-3].isdigit(): continue
			# now it should be a data point
			# we also need to check that this time is not less than the launch time = gps[0]
			tm = float(l[0])*60. + float(l[1])
			if len(gps) > 0 and tm < gps[0] - 2.: continue
			## ----- ERROR CHECKING!! IF THE OB IS BAD, SKIP IT AND MOVE ON! (#thanks to headers, line will always be > 1)
			# - RH cannot be 0, no temps below -80c
			if float(l[2]) < -90.0: continue # filter out -99.00s
			if float(l[3]) < 0.01: continue # terrible idea ->l[3] = 0.01 # instead of killing a datapoint, give it something to be!
			# ok, we also need to ensure there are no massive shifts in obs, ave the last 10, and check
			#FIXME - it is possible that this will not work. if there is a large shift in the data, this will fail
			if len(recent_ave) > 0 and math.fabs(float(l[2]) - sum(recent_ave)/len(recent_ave)) >= 3:
				continue
			else:
				if len(recent_ave) > 2:
					old = recent_ave.pop(0) # eject the oldest value
				recent_ave.append(float(l[2]))
			# ------------------- END ERROR CHECKING of data values ----------------------- #
			# now we are past the launch time, so we will begin popping [0] from the gps times until we find the closest one
			t_p = 0
			for t in gps:
				if t < tm:
					#thus t_p is < t and < tm, so it is to be discarded
					key += 1
					t_p = gps.pop(0)
				else:
					# this means that t_p < tm < t, so figure out which to use, and then we are done!
					if t - tm > tm - t_p:
						# then t_p is closest!
						almost_there.append([tm,float(l[2]),float(l[3]),gps_2[key]])
					else:
						almost_there.append([tm,float(l[2]),float(l[3]),gps_2[key+1]])
					break
		if len(almost_there) < 50 or not almost_there[0]:
			# something is horribly wrong with this sounding
			print "Found a bad file. Launch was not detected, or some other issue with this file (this is normal)"
			continue
		# finally we need to loop through the sounding, and compute some festive things like winds, dewpoints and pressures
		p_prev = init[-3]
		ob_prev = init[-1] # instead of initialized values, use the first 'good' observation, probably a horrible decision
		op5 = op4 = op3 = ob_p2 = almost_there[0]
		
		k = -1
		# we make seperate lists for each variable!
		t_l = []
		td_l = []
		rh_l = []
		p_l = []
		e_l = []
		q_l = []
		tv_l = []
		lt_l = []
		ln_l = []
		z_l = []
		tm_l = []
		dir_l = []
		spd_l = []
		L = 2260000
		R = 286.9
		P0 = 6.112
		T0 = 273.15
		g = 9.81
		wind_ave_length = wind_averaging
		for w in almost_there:
			k += 1
			tm = w[0]
			t = w[1] + 273.15
			t_p = ob_prev[1] + T0
			rh_p = ob_prev[2]
			tc = w[1]
			rh = w[2]
			lt = w[3][0]
			ln = w[3][1]
			# lat and lon need to be averaged over the previous 10 obs if possible
			end = k - wind_ave_length if k - wind_ave_length >=0 else 0
			tr = 0
			key = k
			lh = 0 # lon holder
			th = 0 # lat holder
			tm_0 = 0
			while key >= end:
				tr += 1
				key -= 1
				tm_0 += almost_there[key][0] #if almost_there[key][0] < tm_0 else tm_0
				lh += almost_there[key][3][1]
				th += almost_there[key][3][0]
			lat = math.radians(th / tr) #(w[3][0] + ob_prev[3][0] + ob_p2[3][0]) / 3 
			lon = math.radians(lh / tr) #(w[3][1] + ob_prev[3][1] + ob_p2[3][1]) / 3
			tm_0 = tm_0 / tr
			# now we need the average over the next 10 obs!
			end = k + wind_ave_length if k + wind_ave_length < len(almost_there) else len(almost_there) - 1
			tr = 0
			key = k - 1
			lh = 0
			th = 0
			elv = 0
			tm_1 = 0
			threshold = 0 # threshold increases every time we find an elevation lower than the prev
			### AAAALSO i will use this to check elevations, that they keep increasing, if not, cut it!
			while key < end:
				tr += 1
				key += 1
				tm_1 += almost_there[key][0] #if almost_there[key][0] > tm_1 else tm_1
				lh +=  almost_there[key][3][1]
				th +=  almost_there[key][3][0]
				threshold = threshold + 1 if almost_there[key][3][2] < elv else threshold
				elv = almost_there[key][3][2]
			if wind_ave_length > 5 and threshold > wind_ave_length / 2 and cutoff:
				# IF ALL BUT 5 OF THESE OBS WERE LOWER THAN THE PREVIOUS, WE ARE HEADING DOWN, SO END
				print "cutoff reached"
				break
			lat_1 = math.radians(th / tr)
			lon_1 = math.radians(lh / tr)
			tm_1 = tm_1 / tr
			elev = w[3][2]
			# first lets pump out specific humidity, since this plays a role, starting with vapor pressure
			#rh = 100 e / es, so e = es * rh / 100
			e_p = (rh_p / 100) * (6.112 * math.exp( ( L / R ) * ( (1/T0) - (1/t_p) )))
			# calculate pressure, layer by layer, use p_prev as a guide for q
			q = ( 0.622 * e_p ) / p_prev
			tv_low = (1+0.61*q)*(ob_prev[1]+273.15)
			tv_high = (1+0.61*q)*(t) # assume q remains the same
			tva = (tv_low + tv_high) / 2 
			# now for the reversed hypsometric equation
			p = p_prev / math.exp((g/(R * tva)) * (elev - ob_prev[3][2]))
			
			### now calculate dew point temperature - using a close approximation out of laziness
			td = sounding_dewpoint(t,rh)
			tdc = td - 273.15 
			# now for WINDS!!
			dt = tm_1 - tm_0
			dlat = lat_1 - lat
			dlon = lon_1 - lon
			# time to use the great circle calculations... should give dir and spd [spherical law of cosines]
			eR = 6378137 #(+/-2 m :) Earth's Radius 
			dist = math.acos(math.sin(lat)*math.sin(lat_1) +
					math.cos(lat)*math.cos(lat_1) *
					math.cos(lon_1 - lon) ) * eR
			spd = dist / dt if dt > 0 else 0
			dir = degrees( atan2( math.sin(dlon)*math.cos(lat_1),
				math.cos(lat) * math.sin(lat_1) -
				math.sin(lat)*math.cos(lat_1)*math.cos(dlon) ) ) + 180
			if spd > 340: continue # speed of sound limit there...
			if p > 80000 and spd > 150: continue # greatly exceeding cat-5 hurricane below 800mb

			# well, it is high time to save this data!!!
			tm_l.append(tm - launch_delay)
			t_l.append(tc)
			td_l.append(tdc)
			rh_l.append(rh)
			tv_l.append(tv_high)
			q_l.append(q)
			p_l.append(p / 100.) # i dont feel like dealing in Pa
			dir_l.append(dir)
			spd_l.append(spd)
			lt_l.append(lt)
			ln_l.append(ln)
			z_l.append(elev)
			# reset values so we can do it again!! fun fun!!
			p_prev = p
			ob_prev = w
		self.data.graw_soundings[num]['time'] = tm_l
		self.data.graw_soundings[num]['keys'] = range(len(tm_l))
		self.data.graw_soundings[num]['tc'] = t_l
		self.data.graw_soundings[num]['tdc'] = td_l
		self.data.graw_soundings[num]['rh'] = rh_l
		self.data.graw_soundings[num]['tv'] = tv_l
		self.data.graw_soundings[num]['q'] = q_l
		self.data.graw_soundings[num]['p'] = p_l
		self.data.graw_soundings[num]['wdir'] = dir_l
		self.data.graw_soundings[num]['wspd'] = spd_l
		self.data.graw_soundings[num]['lat'] = lt_l
		self.data.graw_soundings[num]['lon'] = ln_l
		self.data.graw_soundings[num]['z'] = z_l
	print num + 1,"sounding(s) found"
