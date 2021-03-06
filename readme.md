Created by Joe Young March 2011

Originally motivated by the PCAPS field project in Salt Lake City, Utah, run by the University of Utah Department of Atmospheric Sciences.

A utility for managing the observational raw and processed data from a field campaign. Used best with a filesystem based archive of raw file data. 

Modular approach towards data type ingestion allows for extensive applicability to various kinds of observation. From surface stations, to rawinsondes, to wind profilers and aircraft data, this system is able to process easily and efficiently any kind of data that can be stored. 

Due to high variability in data types, it is likely the user will need to write their own processing packages. For this reason, the core modules of the package attempt to simplify much of the work in writing this code. Available to the package writer are time and date processors, file searching techniques, data saving resources, reading and managing XML config script, and a few planned resources such as:
	- file date interpretation
	- raw file peeking
	- Standardized method for producing flat file text output
	- Reading and writing to databases
	- Writing netCDF's (likely with NCAR's pyNIO)
	- support for pickled storage of already processed data
	- methods to automatically determine a datatype for ingestion
	- methods to more easily read text output files (non-pickled storage)
	- probably more things

This is written in python 2.6, and has been tested on Linux (Redhat 4.1.2) and Mac OSX 10.5. This package makes extensive use of numpy, and other packages traditionally packaged with the enthought python distribution. Should these be absent, some of the code will still work. Cython is not presently implemented.

Future versions may require (and may come packaged with) PyNIO and PyNGL, and perhaps some other packages such as metpy. It is possible these will be included, either directly, or through an automated sys.path evaluation.

A planned improvement is an automated sys.path append system, currently one must use the included csh script from the setup directory to use this code without actually installing the service via the [FUTURE] setup.py

This code is still under development, and new modules for different types of observation, file, or instrument are frequently being written. 