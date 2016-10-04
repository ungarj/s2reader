#!/usr/bin/env python

import s2reader
import sys
import os

def main(args):
    scriptdir = os.path.dirname(os.path.realpath(__file__))
    example = "data/S2A_OPER_PRD_MSIL1C_PDMC_20160905T104813_R002_V20160905T005712_20160905T010424.SAFE"
    example_safe = os.path.join(scriptdir, example)

    with s2reader.open(example_safe) as testfile:
        print testfile
        print testfile.product_start_time
        print testfile.product_stop_time
        print testfile.generation_time
        print testfile.footprint
        # for granule in testfile.granules:
        #     # print granule.footprint
        #     print granule.srid
        #     print granule.band_path(1)
        # for band_id in BAND_IDS:
        #     for path in testfile.granule_paths(band_id):
        #         print path

if __name__ == "__main__":
    main(sys.argv[1:])
