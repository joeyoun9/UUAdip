"""
	read in lidar data from the gridded hoch lidar flatfiles
	one per day

	STARE DATA ONLY!!!
"""
import calendar,time
import numpy as np

def run(self, bin_size=5):
	"""
		Read the files and return a gridded data object
		bin_size is the distance in minutes of the bins
	"""
	X = [] # time dimension
	Y = [] # height dimension (ASSUMED TO BE 1-DIMENSIONAL!!!)
	Z = [] # data
	for fd in self.find_files('void','lidardata',allow_repeats=False):
		# now we are in the file
		# get the file time
		fname = fd.split('/')[-1]
		# file format expected: lidardata_joe_20110218.dat
		otime = calendar.timegm(time.strptime(fname[-12:-4]+"00UTC","%Y%m%d%H%Z"))
		# files last for 1 24 hour period, so, yeah, add 86400
		if otime + 86400 < self.data.begin or otime - 86400 > self.data.end:
			continue
		print 'reading',fname
		# well, the file shall be opened!
		f = open(fd)
		i = -2 # index; starts at -2 because the first line is heights, but we stil accumulate
		for line in f:
			i += 1
			if i == -1:
				# then this is the heights line, 
				if not 'NaN' in line and len(Y) == 0:
					# then this is a good line, save it as Y
					Y = line.split() # I would do something more robust if i trusted it
				continue
			tm = otime + bin_size*60 * i # each line is 5 minutes
			if tm < self.data.begin:
				continue
			if tm > self.data.end:
				# then we are done with this chirade.
				break
			# well, then this is a data line
			X.append(tm)
			Z.append([float(x) for x in line.split()])
		f.close()

	data = self.DO(['time','height'],'kennecott.xml',self)
	data.setdim('time',X)
	data.setdim('height',Y)
	data.new('beta',fill=self.flip2d(Z))


	return data


		
		
