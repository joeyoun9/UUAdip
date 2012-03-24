"""
	functions which will be made available globally by import, as well as in the uudewey DataRequest object under funcs
"""

def flip2d(self, wrong):
	if len(wrong) is not 2:
		raise "Oops, flip2d can only handle 2 dimensional arrays!"
		exit()
	import numpy as np
	#UPDATED 1 - 6- 2011: wrong[0] instead of wrong[1]. Thus, all (both) columns must be the same length as col 0!
	right = np.zeros((len(wrong[0]),len(wrong))) 
	# since Z is always full, but X can vary with the span parameter, it is best to use obCount
	i = 0
	for r in wrong:
		c = 0
		for v in r:
			right[c][i] = v
			c+=1
		i+=1
	return right

# SOME UTILITIES AS WELL

def dump(obj):
  for attr in dir(obj):
    print "obj.%s = %s" % (attr, getattr(obj, attr))
	




def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)


def stamp2time(date,format):
	"""
		convert a datestring to unix epoch time
	"""
	from calendar import gmtime
	from time import strptime
	return timegm(strptime(date,format))

	
