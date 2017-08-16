#!/usr/bin/env python
"""Test s2reader main module."""

import os
import s2reader

SCRIPTDIR = os.path.dirname(os.path.realpath(__file__))
TESTDATA_DIR = os.path.join(SCRIPTDIR, "data")
SAFE = "S2A_OPER_PRD_MSIL1C_PDMC_20160905T104813_R002_V20160905T005712_20160905T010424.SAFE"
COMPACT_SAFE = "S2A_MSIL1C_20170226T102021_N0204_R065_T32TNM_20170226T102458.SAFE"


def test_safe():
    """Test SAFE format basic properties."""
    test_data = {
        'product_start_time': "2016-09-05T00:57:12.026Z",
        'product_stop_time': "2016-09-05T01:04:24.002Z",
        'generation_time': "2016-09-05T10:48:13.000935Z",
        'footprint': "POLYGON ((136.2159945831901 -35.8621",
        'num_of_granules': 6
    }
    _test_attributes(test_data, os.path.join(TESTDATA_DIR, SAFE))


def test_compact_safe():
    """Test compact SAFE format basic properties."""
    test_data = {
        'product_start_time': "2017-02-26T10:20:21.026Z",
        'product_stop_time': "2017-02-26T10:20:21.026Z",
        'generation_time': "2017-02-26T10:24:58.000000Z",
        'footprint': "POLYGON ((9.975430158966422 42.4470105948154, 9.97451",
        'num_of_granules': 1
    }
    _test_attributes(test_data, os.path.join(TESTDATA_DIR, COMPACT_SAFE))


def _test_attributes(test_data, safe_path):
    """Compare dictionary attributes with given SAFE file."""
    with s2reader.open(safe_path) as safe:
        assert safe is not None
        assert safe.product_start_time == test_data["product_start_time"]
        assert safe.product_stop_time == test_data["product_stop_time"]
        assert safe.generation_time == test_data["generation_time"]
        assert len(safe.granules) == test_data["num_of_granules"]
        assert safe.footprint.is_valid
