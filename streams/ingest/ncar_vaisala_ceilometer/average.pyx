import Cython
import numpy as np
cimport cython
cimport numpy as np



DTYPE = np.int
ctypedef np.int_t DTYPE_t

DTYPE32 = np.float32
ctypedef np.float32_t DTYPE32_t

DTYPE64 = np.float64
ctypedef np.float64_t DTYPE64_t



@cython.boundscheck(False)
@cython.cdivision(True)

def average_ceil(np.ndarray[DTYPE64_t,ndim=2] z, np.ndarray[DTYPE64_t,ndim=1] X, int average, int span, int ddz, int x_size, int y_size, char ave_type):
	""" Perform averaging of whatever type specified..."""

	# returning the x_m list, of mean values currently - will eventually also return x_d
	x_m = np.zeros(y_size, x_size)
	cdef float h_beg, h_end, v_beg, v_end, d_beg, d_end,ave
	cdef int t, i, dist,low_key,high_key
	# compute the span, X indicates the points needed
	
	for i in range(len(z)):
		zed = z[i]
		for t in range(x_size):
			# for span X will be the key of Z we should average around
			key = X[t]

			# check for averaging type-assumed horizontal for now
			
			# look back and forward span/2 keys to find the value
			low_key = key - int(span / 2)
			high_key = key - int(span / 2)
			if low_key < 0:
				low_key = 0
			if high_key > x_size:
				high_key = x_size
			ave = sum(zed[low_key:high_key]) / span		

			x_m[i].append(ave)
	return x_m


