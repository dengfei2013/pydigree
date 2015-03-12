#!/usr/bin/env python

import random

from pydigree import ChromosomeTemplate
from pydigree.recombination import recombine

nmark = 5000
poolsize = 10000
ngen = 25

c = ChromosomeTemplate()
for x in range(nmark): c.add_genotype(random.random(),.1)
mapp = [.1]*nmark

d = 0

print "Initializing pool"
pool = [c.linkageequilibrium_chromosome() for x in range(poolsize)]

for x in xrange(ngen):
    print "Iteration %d" % d
    recombs = [recombine(random.choice(pool),random.choice(pool),mapp) for x in xrange(poolsize)]
    pool = random.sample(recombs+pool,poolsize)
    d += 1