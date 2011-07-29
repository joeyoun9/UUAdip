#!/usr/bin/env python

def alg(self,md,x,y):
	# Algorithm 3.0
	newm = self.flip2d(md)
	# for every value of X, find this point!
	hts = []
	hts_m = []
	print "pretending to get a pollutant concentration level!"
	for i in range(len(x)):
		# find the height, with the current array in newm
		profile = newm[i]
		gts_gt_3 = 0
		gts_lt_3 = 0
		_1500_m_min = min(profile[0:150])
		# redefine a minimum as the lowest value in the range between the sfc, and where the gradient is 0, having had a 
		# point in which the gradient was a maximum of -0.3
		_low_min = 0
		_low_min_z = 0
		passed_3 = False
		for z in range(len(profile)):
			val = profile[z]
			if val < -0.0019: passed_3 = True
			if val < _low_min:
				_low_min = val
				_low_min_z = y[z]
			# if it is passed the min value, and it is effectively positive in trend, then we are done
			if passed_3 and  val >= -0.0001: break
		hts_m.append(_low_min_z)
		# FIXME then we need to figure out how deep the negative gradient is, so we can reasonably assume passage
		for z in range(len(profile)):
			val = profile[z]
			ht = y[z]
			if val >= 0.0 and gts_gt_3 >= 3 and ht > _low_min_z:
				#'tis golden! this is what we want!
				hts.append(ht)
				break
			if val <= _low_min + 0.01:
				gts_gt_3 += 1
		# check that there was a value created, if not, insert a nan
		if not len(hts) - 1 == i:
			hts.append(float('nan'))
			# hts_m cannot have this problem
	if len(hts) < len(x):
		print "um, yeah, i dont know what happened"
		
	return hts,hts_m

