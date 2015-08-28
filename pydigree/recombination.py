#!/usr/bin/env python

from bisect import bisect_left
from pydigree.genotypes import Alleles, LabelledAlleles

import numpy as np


def recombine(chr1, chr2, map):
    '''
    Takes two chromatids and returns a simulated one by an exponential process
    '''
    
    # An optimization for gene dropping procedures on IBD states.
    # If there is only one marker, choose one at random, and return that.
    # There's no need for searching through the map to find crossover points
    if len(map) == 1:
        return chr1 if np.random.randint(0, 2) else chr2

    newchrom = _recombine_haldane(chr1, chr2, map)
    return newchrom

def _recombine_haldane(chr1, chr2, map):
    # The map is sorted list, and the last item will always be largest.
    maxmap = map[-1]
    nmark = len(map)

    if type(chr1) is not Alleles: 
        raise ValueError(
            'Invalid chromosome type for recombination: {}'.format(type(chr1))) 

    if type(chr1) is not type(chr2):
        raise ValueError("Can't mix chromosome types in recombination")

    if chr1.dtype != chr2.dtype:
        raise ValueError('Chromosomes have different data types')
    
    # Return a new genotype container with the same specs as chr1
    newchrom = chr1.empty_like() 

    # Randomly pick a chromosome to start from
    # np.random.randint works on a half open interval, so the upper bound
    # specified is 2. We'll get zeros and ones out of it.
    flipped = np.random.randint(0, 2)

    last_crossover_index = 0
    crossover_position = 0
    while True:
        # Get from the next chromosome
        flipped = not flipped
        c = chr1 if flipped else chr2

        # Find the next crossover point
        # np.random.exponential is parameterized with the RECIPROCAL of the
        # rate parameter. With random.expovariate I would have used (0.01),
        # here I supply 100 as an argument.
        crossover_position += np.random.exponential(100)

        if crossover_position > maxmap:
            # We've reached the end of our journey here.
            newchrom.copy_span(c, last_crossover_index, None)
            break

        # Find the next crossover point in the chromosome by binary search
        nextidx = bisect_left(
            map, crossover_position, last_crossover_index, nmark)
        newchrom.copy_span(c, last_crossover_index, nextidx)

        # Get ready to do it all over again
        last_crossover_index = nextidx

    return newchrom
