#!/usr/bin/env python

from s2reader import *
import sys
import os
import argparse


def main(args):

    parser = argparse.ArgumentParser()
    parser.add_argument("SAFE", type=str)

    parsed = parser.parse_args(args)
    input_SAFE = parsed.SAFE

    dataset = SentinelDataSet(input_SAFE)

    # Paths
    print "dataset.path:", dataset.path
    print "dataset.product_metadata:", dataset.product_metadata

    # Timestamps
    print "dataset.product_start_time:", dataset.product_start_time
    print "dataset.product_stop_time:", dataset.product_stop_time
    print "dataset.generation_time:", dataset.generation_time

    # Processing level
    print "dataset.processing_level:", dataset.processing_level

    # Footprint
    print "dataset.footprint:", dataset.footprint

    # Granules

    for granule in dataset.granules:
        print granule.granule_identifier

    #evens = [some_special_func(even) for even in range(20) if (even % 2) == 0]
    #evens = map(some_special_func, filter(lambda e: e%2 == 0, range(20)))


if __name__ == "__main__":
    main(sys.argv[1:])
