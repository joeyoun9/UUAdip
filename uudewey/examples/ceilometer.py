"""
	Example script using the v0.0 uudewey data management software for analyzing a raw vaisala CL31 ceilometer dataset.
	This data is based on the PCAPS field project, and the data is not included with the example. Likewise, this example
	involves a project configuation file, which is described in detail at www.jsyoung.us/#code/uudewey

	This is simply a reading exercise, plotting tools are not demonstrated
"""

from uudewey import DataRequest, streams.ingest.ncar.cl31
# import both the DataRequest class, as well as the NCAR ceilometer (cl31) module

# create the request
request = DataRequest('../pcaps.xml','iop05')

# using the request object, now run the ingestor for this data - saving to the file specified
streams.ingest.ncar.cl31.run(request,make_file_raw='./rawfile.txt')
