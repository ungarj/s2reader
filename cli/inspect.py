#!/usr/bin/env python
""" Command line utility to inspect SAFE files. """

import sys
import argparse
import s2reader
import pprint

def main(args=None):

    if args is None:
        args = sys.argv[1:]
        parser = argparse.ArgumentParser()
        parser.add_argument("safe_files", type=str, nargs='*')
        parser.add_argument("--granules", action="store_true")
        parsed = parser.parse_args(args)
    elif isinstance(args, argparse.Namespace):
        parsed = args
    else:
        raise RuntimeError("invalid arguments for mapchete execute")

    pp = pprint.PrettyPrinter()
    for safe_file in parsed.safe_files:
        with s2reader.open(safe_file) as safe_dataset:
            if parsed.granules:
                pp.pprint(
                    dict(
                        granules=[
                            dict(
                                granule_identifier=granule.granule_identifier,
                                footprint=str(granule.footprint),
                                srid=granule.srid,
                                cloudmask=str(granule.cloudmask)
                                )
                            for granule in safe_dataset.granules
                            ]
                        )
                    )
            else:
                pp.pprint(
                    dict(
                        safe_file=safe_file,
                        product_start_time=safe_dataset.product_start_time,
                        product_stop_time=safe_dataset.product_stop_time,
                        generation_time=safe_dataset.generation_time,
                        footprint=str(safe_dataset.footprint),
                        granules=len(safe_dataset.granules),
                        granules_srids=list(set([
                            granule.srid
                            for granule in safe_dataset.granules
                            ]))
                        )
                    )
            print "\n"
