#!/usr/bin/env python

import pybedtools
import multiprocessing
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("--test_bed",
                    help="bedfile being tested for enrichment of a "
                    "genomic feature",
                    required=True)
parser.add_argument("--background_bed",
                    help="Optional path to the bedfile used for background "
                    "for enrichment analysis")
parser.add_argument("--permutations",
                    help="number of permutations to run", type=int)
parser.add_argument("--output",
                    help="path and name of output file to be written with "
                    "results",
                    required=True)
parser.add_argument("--genome",
                    help="genome assembly name",
                    required=True)
parser.add_argument("--ibed", "-i", required=True,
                    help="BED file to check")
parser.add_argument("--processes", "-j", type=int,
                    default=multiprocessing.cpu_count(),
                    help="Number of CPUs to use.  Defaults to all available")
args = parser.parse_args()

# Create a genome file once, to be used with all iterations.
genome_fn = pybedtools.chromsizes_to_file(args.genome)

# If background was provided, then pass it to shuffle's "-incl" arg; otherwise
# don't pass any additional args
shuffle_kwargs = {}
if args.background_bed:
    shuffle_kwargs['incl'] = args.background_bed

bed = pybedtools.BedTool(args.ibed)


# `results` will be a dictionary with all sorts of calculated info; see the
# output file for what's included:
results = bed.randomstats(

    # `bed` will be shuffled many times, each time checking intersection with
    # `test_bed`
    other=args.test_bed,

    # pvalue resolution limited by permutations
    iterations=args.permutations,

    # use new pybedtools parallel functionality
    new=True,

    # genome file that was prepared above
    genome_fn=genome_fn,

    # This will include, in the `distribution` key of the results dictionary,
    # a NumPy array containing the intersection counts for each iteration.
    # Useful for calculating your own enrichment statistics later.
    include_distribution=True,

    # Pass these on to BedTool.shuffle
    shuffle_kwargs=shuffle_kwargs,

    # Pass these on to BedTool.intersect
    intersect_kwargs=dict(u=True),

    # CPUs to use.
    processes=args.processes,

)

# Convert the NumPy array of distributions to a list so it can be output to
# JSON
results['distribution'] = results['distribution'].tolist()

# Write to JSON
with open(args.output, 'w') as fout:
    json.dump(results, fout)
