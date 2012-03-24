"""
	apparently it is a pain to convert from UTM and lat lon, so here is a tool	
	from my understanding, the y value is distance in m from the equator, directly N-S ideally,
	the x value is the distance from the defined meridian, directly east, therefore the further you are from the meridian
	the worse it gets

	PLUS you have to know what meridian you are talking about. The ll2utm comes from wikipedia, if what I code works...
	that meridian is known as the zone, and there are 60 zones on earth - a method can be used to determine the zone

	utah should be zone 12
"""

from math import *

def ll2utm(lat, lon, zone=False):
	"""
		convert a lat lon in decimal to cartesina UTM in meters
	"""
	if not zone:
		zone = find_zone(lon)

	# CALCULATION USES RADIANS AND KILOMTERS
	# the N0 value is hemisphere specific, so figure that out, ace
	if lat >= 0:
		N0 = 0
	else:
		N0 = 10000 #(km)
	lat = radians(lat)
	lon = radians(lon)
	E0  = 500 #km
	k0 = 0.9996
	a = 6378.137 #km earth radius
	e = 0.0818192 # earth eccentricity - NOT TO BE CONFUSED WITH 2.982... e, 
	_A = A(lat,lon,zone,e)
	_T = T(lat,e)
	_C = C(lat,e)
	_s = s(lat,e)
	_v = v(lat,e)
	
	x = E0 + k0*a*_v*(_A+(1 - _T + _C)*(pow(_A,3)/6) + (5 - 18*_T + _T*_T)*(pow(_A,5)/120))
	y = N0 + k0*a*(_s+_v*tan(lat)*(_A*_A/2 + (5 - _T + 9*_C + 4*_C*_C)*pow(_A,4)/24 + (61 - 58*_T + _T*_T)*pow(_A,6)/720))
	return x*1000,y*1000
	

# defining several functions needed
def v(lat,ec):
	return 1/sqrt(1-pow(ec,2)*pow(sin(lat),2))

def A(lat,lon,zone,ec):
	lon0 = radians(zone * 6 - 180 - 3)
	print degrees(lon),degrees(lon0)
	return (lon - lon0)* cos(lat)

def s(lat,ec):
	a = (1 - pow(ec,2)/4 - 3 * pow(ec,4)/64 - 5 * pow(ec,6)/256) * lat
	b = (3*pow(ec,2)/8 + 3 * pow(ec,4)/32 + 45*pow(ec,6)/1024)*sin(2*lat)
	c = (15*pow(ec,4)/256 + 45*pow(ec,6)/1024) * sin(4*lat)
	d = 35*pow(ec,6)*sin(6*lat) / 3072
	return a - b + c - d

def T(lat,ec):
	return pow(tan(lat),2)

def C(lat,ec):
	return pow(ec,2)*pow(cos(lat),2) / (1- pow(ec,2))



def find_zone(lon):
	"""
		a SEMI functional UTM zone finding tool (does not account for things like where Norway pulls a fast one)
	"""
	# number of zones is 60, atarting at 01 with -180 to 60 at <= 180 WARNING - MORE COMPLEX IN NORTHERN EUROPE!!
	v = lon+180 # now we are calculating from 0 - 360
	for z in range(1,61):
		if v <= z*(360/60):
			zone = z
			break
	print "Identified as zone",zone
	return zone

