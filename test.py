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
    print "dataset.product_metadata_path:", dataset.product_metadata_path

    # Timestamps
    print "dataset.product_start_time:", dataset.product_start_time
    print "dataset.product_stop_time:", dataset.product_stop_time
    print "dataset.generation_time:", dataset.generation_time

    # Processing level
    print "dataset.processing_level:", dataset.processing_level

    # Footprint
    print "dataset.footprint:", dataset.footprint

    # Granules
    print len(dataset.granules), "granule(s))"
    x = 1
    for granule in dataset.granules:
        print "granule", x
        print "granule.datastrip_identifier", granule.datastrip_identifier
        print "granule.granule_identifier", granule.granule_identifier
        print granule.footprint
        assert dataset.footprint.intersects(granule.footprint)
        x += 1


if __name__ == "__main__":
    main(sys.argv[1:])
