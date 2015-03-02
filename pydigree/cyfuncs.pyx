test='test'

from itertools import izip
import numpy as np
cimport numpy as np

cpdef ibs(g1,g2, missingval=None):
 ''' Returns how many alleles are identical-by-state between two genotypes, or missingval if either genotype is missing ''' 
 a,b = g1
 c,d = g2
 
 if not (a and b and c and d):
    return missingval
 if (a == c and b == d) or (a == d and b == c):
    return 2
 elif a == c or a == d or b == c or b == d:
    return 1
 return 0


def runs(sequence, predicate, minlength=2):
    """
    Identifies runs of values for which predicate(value) evaluates True and yields 2-tuples of the start and end (inclusive) indices
    """
    cdef int inrun = False
    cdef int start, stop
    for i,v in enumerate(sequence):
        if not inrun and predicate(v):
            inrun = True
            start = i
        elif inrun and not predicate(v):
            inrun = False
            stop = i - 1
            if stop - start >= minlength:
                yield start, stop

    if predicate(v) and inrun:
        stop = i
        if stop - start >= minlength:
            yield start, stop
    
def runs_gte(sequence, double minval, int minlength=2):
    cdef int inrun = False
    cdef int start, stop, i, l

    i = 0

    for i in range(len(sequence)):
        v = sequence[i]
        if not inrun and v >= minval:
            inrun = True
            start = i
        elif inrun and v < minval:
            inrun = False
            stop = i - 1
            if stop - start >= minlength:
                yield start, stop
    if inrun and (stop - start) >= minlength:
        yield start, i

def set_intervals_to_value(intervals, size, value):
    DTYPE = np.int
    cdef int start = 0
    cdef int stop = 0
    cdef np.ndarray array = np.zeros(size, dtype=DTYPE)
    for start, stop in intervals:
        array[start:(stop+1)] = value
    return array