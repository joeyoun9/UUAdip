"""
# UTDewey package for processing MesoWest requests for surface data stations. 
# current configuration is for PTU and GPS files, to be time synched, as well, John Horel has processed
# some more high resolution / more raw formats, and those will be experimented with, possibly with sub operations

Created by Joe Young March 2011 
Dept. of Atmospheric Sciences
University of Utah
Salt Lake City, Utah, USA

Created under the NSF funding for the PCAPS project 2010 - 2013
"""
import sys,time,datetime,calendar,array,math
from math import atan2


# as with all packages for the UTDewey data system, this should simply be a function that returns 
# the data in the specialized format. Function MUST begin with the data request object (self)
# and the function is to be called 'run'

def run(self, **kwargs):
	# request is for mesowest data, so we want to set the variables to get some mesowest info
		# import the keyword arguments into the data object
		self.data.stations = self.data.domain = False
		for kw in kwargs:
			self.data.set(kw,kwargs[kw]) 
		if not self.data.stations and not self.data.domain:
			print "When calling the mesowest method, you need to specify either a domain, or a list of station(s)"
			print "Use the format stations=['STN1','STN2','STN3'] OR a domain entry"+"""
Domain entries can be of 4 forms:
	1) domain=True : get all stations in the XML config defined project boudning box
	2) domain=[lat1,lon1,lat2,lon2] : gives all the stations in the box from UL to LR
	3) domain=[radius,lat,lon] : gives all the stations within the radius (km) of a lat/lon point
	4) domain="text" : this text will be passed directly to MesoWest, and we will process what comes back

Note: any list of stations takes priority over domains, so you will only get the station data
"""
			return False
		# specified stations dominate over domains
		if self.data.stations:
			print "Beginning to process stations from MesoWest"
			if self.data.domain:
				print "You gave both a station list and a domain, I am taking only the station list. Stations > Domain FFR."
			# now the first task is to download from every one of these stations
			self.data.process = self.data.stations
			
		else:
			# to process the domain we need to check which of the 4 forms it is, and then go from there
			print "Processing your domain: "+str(self.data.domain)
			if self.data.domain == True:
				area = self.data.bounding_box
				print "Grabbing data for the entire ",self.pid,"area (in a box form)"
			elif len(self.data.domain) == 4 and type(self.data.domain) == list:
				print "yay subdomain"
				# then it is a list of tuples, and a specified box
			elif len(self.data.domain) == 3 and type(self.data.domain) == list:
				# then it is a radius
				print "yay radius!"
			elif type(self.data.domain) == str:
				# then i have to assume it is a text thing
				print "Processing your text domain"
			else:
				print "Your domain was unacceptable, please edit it"
				return False	
			# now we create a mesowest request, and grab the data... via http most likely
			self.data.process = self.data.domain
