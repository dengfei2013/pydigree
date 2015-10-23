import argparse
import numpy as np
import pydigree as pyd
from pydigree.stats import MixedModel
from pydigree.stats.stattests import LikelihoodRatioTest

parser = argparse.ArgumentParser()
parser.add_argument('--ped', required=True,
                    help='LINKAGE formatted 5/6 column pedigree file')
parser.add_argument('--phen', required=True,
                    help='CSV formatted phenotype file')
parser.add_argument('--geno', required=True,
                    help='PLINK formatted genotype PED file')
parser.add_argument('--map', required=True, help='PLINK formatted MAP file')
parser.add_argument('--outcome', required=True, help='Response variable')
parser.add_argument('--fixefs', required=False, nargs='*', default=[],
                    help='Names of fixed effects to include in model')
parser.add_argument('--maxmethod', default='Fisher Scoring')
parser.add_argument('--only', required=False, default=None, nargs='*',
                    help='Labels of genotypes to be tested')
parser.add_argument('--verbose', default=False, action='store_true')
args = parser.parse_args()

if args.only is not None:
    only = frozenset(args.only)

print 'Reading pedigree'
peds = pyd.io.read_ped(args.ped)
print 'Reading phenotypes'
pyd.io.read_phenotypes(peds, args.phen)
print 'Reading genotypes'
genodata = pyd.io.plink.read_plink(pedfile=args.geno,
                                   mapfile=args.map)
peds.update(genodata)

print 'Fitting polygenic model'
null_model = MixedModel(peds, outcome=args.outcome, fixed_effects=args.fixefs)
null_model.add_genetic_effect()
null_model.fit_model()
null_model.maximize(method=args.maxmethod, verbose=args.verbose)
null_model.summary()
llik_null = null_model.loglikelihood()


def tableformat(*cells):
    return ''.join(['{:<12}'.format(x) for x in cells])


def measured_genotype_association(extrapredictor):
    model = MixedModel(peds,
                       outcome=args.outcome,
                       fixed_effects=args.fixefs + [extrapredictor])
    model.add_genetic_effect()
    model.fit_model()
    model.maximize(method=args.maxmethod, verbose=args.verbose)
    return model

print tableformat('CHROM', 'POS', 'MARKER', 'MAJ', 'MIN',
                  'MAF', 'BETA', 'LOD', 'PVALUE')
for chromidx, chromobj in enumerate(peds.chromosomes):
    for locidx, markerlabel in enumerate(chromobj.labels):
        locus = chromidx, locidx

        if args.only is not None and markerlabel not in only:
            continue

        freqs = peds.allele_frequencies(locus, nonfounders=True)
        alleles = [x[0]
                   for x in sorted(freqs.items(),
                                   key=lambda x: x[1],
                                   reverse=True)]

        if len(alleles) == 1:
            print 'Monomorphic genotype: {}'.format(markerlabel)
            continue

        maj_allele = alleles[0]

        for min_allele in alleles[1:]:
            predictorname = '{0}{1}'.format(markerlabel, min_allele)
            maf = freqs[min_allele]

            peds.genotype_as_phenotype(locus,
                                       minor_allele=min_allele,
                                       label=predictorname)
            alt_model = measured_genotype_association(predictorname)
            beta = np.matrix.item(alt_model.beta[-1])  # Slope of marker effect

            lrt = LikelihoodRatioTest(null_model, alt_model)

            print tableformat(chromobj.label,
                              chromobj.physical_map[locidx],
                              markerlabel,
                              maj_allele,
                              min_allele,
                              '{:<10.3g}'.format(maf),
                              '{:<10.3g}'.format(beta),
                              '{:<10.3f}'.format(lrt.lod),
                              '{:<10.4g}'.format(lrt.pvalue))
            peds.delete_phenotype(predictorname)