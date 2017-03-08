#!/usr/bin/env python

import s2reader
import sys
import os
import unittest

class SAFETest(unittest.TestCase):

    _scriptdir = None
    _SAFE_PKG = None
    COMPACT_SAFE_PKG = None

    @classmethod
    def setUpClass(cls):
        cls._scriptdir = os.path.dirname(os.path.realpath(__file__))
        cls._SAFE_PKG = "data/S2A_OPER_PRD_MSIL1C_PDMC_20160905T104813_R002_V20160905T005712_20160905T010424.SAFE"
        cls._COMPACT_SAFE_PKG = "data/S2A_MSIL1C_20170226T102021_N0204_R065_T32TNM_20170226T102458.SAFE"

    def test_SAFE(self):
        dict = {}
        dict['product_start_time'] = "2016-09-05T00:57:12.026Z"
        dict['product_stop_time'] = "2016-09-05T01:04:24.002Z"
        dict['generation_time'] = "2016-09-05T10:48:13.000935Z"
        dict['footprint'] = "POLYGON ((136.2159945831901 -35.8621"
        dict['num_of_granules'] = 6
        self._inspect_package(os.path.join(self._scriptdir, self._SAFE_PKG),dict)

    def test_SAFE_COMPACT(self):
        dict = {}
        dict['product_start_time'] = "2017-02-26T10:20:21.026Z"
        dict['product_stop_time'] = "2017-02-26T10:20:21.026Z"
        dict['generation_time'] = "2017-02-26T10:24:58.000000Z"
        dict['footprint'] = "POLYGON ((9.975430158966422 42.4470105948154, 9.97451"
        dict['num_of_granules'] = 1
        self._inspect_package(os.path.join(self._scriptdir, self._COMPACT_SAFE_PKG),dict)

    def _inspect_package(self, path, dict):
        with s2reader.open(path) as pkg:
            self.assertIsNotNone(pkg)
            self.assertEqual(pkg.product_start_time, dict['product_start_time'])
            self.assertEqual(pkg.product_stop_time, dict['product_stop_time'])
            self.assertEqual(pkg.generation_time, dict['generation_time'])
            self.assertTrue(str(pkg.footprint).startswith(dict['footprint']))
            self.assertEqual(len(pkg.granules),dict['num_of_granules'])

def main():
    unittest.main()

if __name__ == "__main__":
    main()
