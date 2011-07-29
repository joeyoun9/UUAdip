#!/usr/bin/env python
"""
metcalcs.sounding is a repository of sounding related functions that are available as part of the UTDewey system. They can be imported simply by
import metcalcs.sounding
"""
import numpy as np
import math
def rh2td(t,rh,kc):
	# use the more accurate approximation
	# TEMP IN K
	if kc == "k":
		td = 17.271*t/(237.7 + t) + np.log(rh/100)
	else:
		td = t - (100.-rh)/5.
	return td

def sounding_dewpoint(t,rh):
	# calculates and returns kelvin dew point temperature
	# for given temperature [k] and rh [%]
	#philosophy: rh = e/es. now, e depends on the temperature, as does es
	# basically, at hella cold temperatures, L = something else
	#FIXME replace math objects with np objects
	R = 286.9
	P0 = 6.112
	T0 = 273.15
	L = 2260000 if t > 274 else 2260000 # + 334000
	if t < 271:
		e = (rh / 100) * (6.112 * math.exp( ( L / R ) * ( (1/T0) - (1/t) )))
		td = ( T0**-1 - (R / L) * math.log(e / P0) )**-1
	else:
		e = (rh / 100) * (6.112 * math.exp( ( L / R ) * ( (1/T0) - (1/t) )))
		#td = (  T0**-1 - (R / L) * math.log(e / P0) )**-1
		td = (243.5 * math.log(e / 6.112)) / (17.67 - math.log(e / 6.112)) + 273.15
			
	# td can be found by rearranging the clausius-clapeyron equation
	return td


def e_calc(t,rh):
	pass
	# this will use an iterative method of solving for e (vapor pressure)
	# at the given temperature basically the same as the dewpoint, but using
	# iterative forms of the clasius-clapeyron equation... eventually!


def c2f(t):
	return 1.8*t+32

def f2c(t):
	return (t-32)/1.8


def moist_adiabat (tmp,pres,kc):
	# this is a wallace and hobbs approximation:
	if kc=="k":
		t = tmp
	else:
		t = tmp+273.15
	lv = 2500000.
	cp = 1004.
	td = dry_adiabat(t,pres,'k')
	te = td * np.exp(lv*ws(t,pres)/cp*t)
	print t,pres,es(t),ws(t,pres),lv*ws(t,pres)/cp*t	
	return te

def ws (t,pres):
	# saturation mixing ratio, a function of saturation vapor pressure
	pres = pres * 100 # expect entry of hPa - convert to pa because that is the unit es returns
	return 0.622 * ( es(t)/(pres - es(t)) )

def es (t):
	# saturation vapor pressure
	es0 = 6.11 #Pa
	t0 = 273.15
	l = 2500000. # J/whatever kg m^2 blah
	rv = 461.5
	return es0 * np.exp( (l/rv) * ((1/t0) - (1/t)) )


def dry_adiabat (temp,pres,kc):
	# temp in K!!
	if kc=="k":
		t = temp
	else:
		t = temp+273.15
	tda = t*(np.power(pres/1000.,2./7.))
	return tda



def skew (temp,pres, rate=.005):
	#return temp + (1000-pres)*.05
	dz = 5740.*np.log(1000/pres)
	return temp + rate*dz 

def skewz (temp, z, rate=.005):
	return temp + rate*z

def virt (t,RH,p):
	# sadly this has to be calculated from td, because i have no real good way of calculating td from RH
	tv = t / ( 1 - ( ( RH * es(t) ) / ( 100 * p )  ) * (1 - 0.622) )
	return tv
