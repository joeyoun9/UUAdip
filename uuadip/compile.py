"""
	compile.py - 
	A utility for compressing various raw data files into single larger more native file formats
	
	Can only be run over an entire project, using the <cache> tag in a v3 xml config script
"""

from tools import getText
import sys

def compile (object, stream=False):
	"""
		compile all the native data formats from this project into native format
		data files in the specified cache directory. Object is the project DataFetch object.

		uses the compile method if present within each identified stream.
		OR it can run only on a specified stream.
	"""
	print "Compiling your project to the cache directory"
	if object.proj.c_version < 3:
		print "You need to be using version 3+ of the XML config to use the cache tag."
		return False
	count = 0
	cache = object.proj.cache
	streams = object.proj.findsource('',find='all') 
	# now we have an XML object of all the streams... whoopie.
	# now loop through them, import, check for compile options, and run if necessary
	for s in streams:
                        name = getText(s.getElementsByTagName('name')[0].childNodes)
			if stream and not stream == name:
				# then continue
				continue
			# now import the module, and check for a compile method
			pkg = object.proj.findsource(name, find='package')
			#package = getText(s.getElementsByTagName('type')[0].childNodes)
                        #exec "import uudewey.readers."+package+" as c"
			__import__(pkg) # ooh! all newfangled!
			c = sys.modules[pkg]
			object.nowPkg = name # needed for the find_files method to work!
	
			if 'compile' in dir(c):
				# then run compile! it's that simple!
				print "Compiling:",name
				count += 1
				object.nowPkg = name
				pkg_id = name.lower().replace(' ','')
				c.compile(object,pkg_id)
			else:
				print name,"is not a compilable datatype currently. (",pkg,")"
	# well, if we got to this point, then the project has no streams capable of compiling
	print "Project Compiled: streams successfully compiled: ",count
