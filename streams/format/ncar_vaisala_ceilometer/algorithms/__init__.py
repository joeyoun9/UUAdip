#!/usr/bin/env python

# this is the init script for the algorithms package. This code will be used to help manage algorithms.

def surf_pol(*args,**kwargs):
	from streams.format.ncar_vaisala_ceilometer.algorithms.sfc_pol_6 import alg as sp
	return sp(*args,**kwargs)
	
