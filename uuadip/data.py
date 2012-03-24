import version
import array
class Data:
	def __init__(cls, dims, project, request, vers=version.get_version()):
		"""
			Initialization of the data object. Creates an object with included metadata
			Inputs:
			cls:   Class Object, Self.
			dims:   A list of the names of the dimensions, the length of indicates the number of dimensions
			project:   Location of project config file (hard location)
			start:   beginning epoch (unix) timestamp
			end:   End epoch timestamp
			dtype:   type of data (source/instrument) being held in this data object
		"""
		# first we will read in the basic information to class attributes
		cls.project = project
		# with some error checking
		cls.start = request.data.begin
		cls.end = request.data.end
		cls.__version = vers
		cls.__dversion = 1.0 # the version of the data object
		
		# now for dims
		if type(dims) == list:
			cls.__dims__ = dims
			cls.__dim_array__ = range(len(dims)) # since dim array will be the same size as dims
			# that was pretty simple
		else:
			print "Dims need to be a list you provide of the name of each dimension"
			return False
		# create a blank levels array
		cls.__levels__ = {}

	def pickle(cls):
		"""
			A powerful and standardized storange function which uses the datatype in filename, but will save this object.
			Will have to be unpickeled independently, and #FIXME may need to use a seperate unpickle function if it only pickles values
		"""
		pass
	def setdim(cls, name, values):
		"""
			Set the value of the dimension list. Values will not be checked 
		"""
		#FIXME - check values
		cls.__dim_array__[cls.__getDimKey__(name)] = values
	def dims(cls):
		"""
			print the dimensions of this dataset
		"""
		return 
	def dim(cls, name):
		"""
			Get the dimension array identified by name
		"""
		key = cls.__getDimKey__(name)
		return cls.__dim_array__[key]

	def data(cls, level=False, dims=False):
		"""
			return the data within the object, using the dimension method of the Level class
			if no level is specified, return a dict of grids, keyed by the level name.
			if no dims are specified, return in their current configuration, dim1 dim2 dim3 ... dimN
			dims can be bool, or an len(dims) = n list ordering the names of the dimensions how it 
			should be ordered or the keyword 'reverse' which will reverse the direction of the dimensions.
			ex: dims = ['height','time']; dims = 'reverse'
		"""
		# first check that if dims, all are accounted for
		
		pass

	def new(cls, name, fill=False):
		"""
			Create a new level of data - this will create a dict element identified by the name, so you can access
			all the 'public' methods of the Level class by using the method cls.level()
		"""
		cls.__levels__[name] = (Level(name, cls))
		if not type(fill) == bool:
			cls.__levels__[name].fill_table(fill)
		
	def level(cls, name=False):
		"""
			Return the level object identified by variable name 'name'
		"""
		if not name:
			return cls.__levels__[cls.__levels__.keys()[0]] # presumably there is only one
		if name in cls.__levels__.keys():
			return cls.__levels__[name]
		else:
			print "Sorry",name,"was not found in the list of variables"
			return False
	def get_levels(cls):
		"""
			return a list of all the current data levels - hah, so simple! 
		"""
		return cls.__levels__.keys()
		
	def series(cls, dim, key=False):
		"""
			Create n dimensional Data objects by splitting along dimension dim
			Example:
			grid of height by time data, dim 1 = time, dim 2 = height (2 dimensions)
			24 times and 50 heights
			Data.series('time') will create a list of 24 Data objects each 2 dimensions
			with the data in height, however time remains as one dimension since a grid 
			must have 2 dimensions. Time will be 1x1 dimension key array, as it is with all series data

			will use the get_data method of each level, save it, and then create a new data object by breaking up this array

			dim:   textual dimension
			key:   if you want only one series output, and you know the key along dimension dim, then you can specify (int)
		"""
		pass
	def grid(cls, *grids):
		"""
			when given a list of other grids (which can include the same one as is currently being run)
			return a single Data object which is a gridded form of all these data objects. The inverse of series.
		"""
		pass
	def profile(cls, key=False, levels=False):
		"""
			Create profiles from a 2 dimensional dataset only if time and height are the two dimensions
		"""

		pass

	def verscheck(cls, vers=version.get_version()):
		# compare the internal program version to the new program version
		# if it is from an older version, then it may be off
		if not vers == cls.__version:
			return False
		else:
			return True

	def __getDimKey__(cls, dim):
		"""
			internal method to get the dimension key from the dimension name
		"""
		lst = cls.__dims__
		for k in range(len(lst)):
			#print lst[k],dim
			if lst[k] == dim:
				return k
		# sadly, if we made it here, then it failed
		print "Could not find a dimension list for dimension:",dim
		return False

	def __getlevelkey__(cls, level):
		"""
			internal method to get the numerical level key from the level name
		"""
		lst = cls.__levels__
		for k in range(len(lst)):
			if lst[k] == level:
				return k

class Level:
	"""
		Within the data class, this is the data grid, which has several of its own methods
		such as fetching and whatnot
	"""
	def __init__(cls, name, parent):
		"""
			Create the level object, as a blank n-dimensional array
		"""
		cls.parent = parent
		cls.name = name # name corresponds to the key in the list in the Data object
		
		
	__table__ = []
	def push(cls, val, dims):
		"""
			Append a data value to the array simple,
			since values are stored in a large array, this will also append - must determine the
			sizes, and where to append in a multi-dimensional list or numpy array...
		"""
		# the dims will be the point where this value should be appended...
		pass #FIXME - how to deal with growing the size of the tables
	def replace(cls, val, point):
		"""
			Replace the value at a point. does not change anything about the sizes of anything
		"""
		pass
	def fill_table(cls, z):
		"""
			Give the entire table's worth of values
			z:   the multi-dimensional array containing all values, dimension checks will be made
		"""
		# FIXME - CHECK FOR DIMENSIONS
		cls.__table__ = z
		
	def get_data(cls, dims=False):
		"""
			Return the data grid of this level. 
		"""
		# FIXME for now it is dumb, and just returns the array
		if not dims:
			return cls.__table__
		else:
			print "Actually, this capability has yet to be perfected, so please use dims=False"
			return False
	
