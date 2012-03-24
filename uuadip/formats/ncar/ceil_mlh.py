"""
	Process the ceilometer MLH (Vaisala) output files produced from the software.
	filed under NCAR, because these files are not necessarily a product of the Vaisala Software
	Joe Young U of Utah, September 2011
"""

import sys,time,datetime,calendar

def run(self):
	"""
		read in mlh output files
	"""
	print "Reading ceilometer MLH Files"
	
	out = self.DO(['time'],'...',self)
	# now identify the files we want to use, use only files ending in 00.txt for now, there are 00 - 10, or 11
	self.log('Finding Files...')
	first = []
	second = []
	third = []
	fourth = []
	fifth = []
	tms = []
	for f in self.find_files('','00.txt',allow_repeats=False):
		# determine if this file is in our range!
		ftime = calendar.timegm(time.strptime(f.split("/")[-1][0:-6]+"UTC","%Y%m%d%H%Z"))
		if ftime + 3600 > self.data.end or ftime - 3600 < self.data.begin:
			continue
		# now we have sorted out the riffraf
		# now we see a reason to open the file, hoever we will not announce file openings
		#self.log('Opening',f.split("/")[-1])
		fh = open(f)
		lines = fh.readlines()
		fh.close()
		for line in lines:
			parts = line.split()
			date = parts[0]+parts[1]+"UTC"
			tm = calendar.timegm(time.strptime(date,"%d/%m/%Y%H:%M%Z"))
			if tm < self.data.begin:
				continue
			if tm > self.data.end:
				break
			tms.append(tm)
			first.append(int(parts[2]))
			second.append(int(parts[3]))
			third.append(int(parts[4]))
			fourth.append(int(parts[5]))	
		
	out.setdim('time',tms)
	out.new('first',fill=first)
	out.new('second',fill=second)
	out.new('third',fill=third)
	out.new('fourth',fill=fourth)

	return out	
