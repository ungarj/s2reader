#!/usr/bin/env python
"""Test s2reader main module."""

import os
import s2reader

SCRIPTDIR = os.path.dirname(os.path.realpath(__file__))
TESTDATA_DIR = os.path.join(SCRIPTDIR, "data")
SAFE = "safe/S2A_OPER_PRD_MSIL1C_PDMC_20160905T104813_R002_V20160905T005712_20160905T010424.SAFE"
COMPACT_SAFE = "compact_safe/S2A_MSIL1C_20170226T102021_N0204_R065_T32TNM_20170226T102458.SAFE"
ZIPPED_SAFE = "zipped_safe/S2A_MSIL1C_20170809T100031_N0205_R122_T32TQT_20170809T100028.zip"


def test_safe():
    """Test SAFE format basic properties."""
    test_data = {
        'product_start_time': "2016-09-05T00:57:12.026Z",
        'product_stop_time': "2016-09-05T01:04:24.002Z",
        'generation_time': "2016-09-05T10:48:13.000935Z",
        'num_of_granules': 6,
        'processing_level': 'Level-1C',
        'product_type': 'S2MSI1C',
        'spacecraft_name': 'Sentinel-2A',
        'sensing_orbit_number': '2',
        'sensing_orbit_direction': 'DESCENDING'
    }
    _test_attributes(test_data, os.path.join(TESTDATA_DIR, SAFE))


def test_compact_safe():
    """Test compact SAFE format basic properties."""
    test_data = {
        'product_start_time': "2017-02-26T10:20:21.026Z",
        'product_stop_time': "2017-02-26T10:20:21.026Z",
        'generation_time': "2017-02-26T10:24:58.000000Z",
        'num_of_granules': 1,
        'processing_level': 'Level-1C',
        'product_type': 'S2MSI1C',
        'spacecraft_name': 'Sentinel-2A',
        'sensing_orbit_number': '65',
        'sensing_orbit_direction': 'DESCENDING'
    }
    _test_attributes(test_data, os.path.join(TESTDATA_DIR, COMPACT_SAFE))


def test_zipped_safe():
    """Test zipped SAFE format basic properties."""
    test_data = {
        'product_start_time': "2017-08-09T10:00:31.026Z",
        'product_stop_time': "2017-08-09T10:00:31.026Z",
        'generation_time': "2017-08-09T10:00:28.000000Z",
        'num_of_granules': 1,
        'processing_level': 'Level-1C',
        'product_type': 'S2MSI1C',
        'spacecraft_name': 'Sentinel-2A',
        'sensing_orbit_number': '122',
        'sensing_orbit_direction': 'DESCENDING'
    }
    _test_attributes(test_data, os.path.join(TESTDATA_DIR, ZIPPED_SAFE))


def _test_attributes(test_data, safe_path):
    """Compare dictionary attributes with given SAFE file."""
    with s2reader.open(safe_path) as safe:
        assert safe is not None
        assert safe.product_start_time == test_data["product_start_time"]
        assert safe.product_stop_time == test_data["product_stop_time"]
        assert safe.generation_time == test_data["generation_time"]
        assert len(safe.granules) == test_data["num_of_granules"]
        assert safe.footprint.is_valid
        assert safe.processing_level == test_data["processing_level"]
        assert safe.product_type == test_data["product_type"]
        assert safe.spacecraft_name == test_data["spacecraft_name"]
        assert safe.sensing_orbit_number == test_data["sensing_orbit_number"]
        assert safe.sensing_orbit_direction == test_data["sensing_orbit_direction"]
        for granule_path in safe.granule_paths("02"):
            assert isinstance(granule_path, str)
        for granule in safe.granules:
            assert granule.srid.startswith("EPSG")
            assert isinstance(granule.metadata_path, str)
            # TODO PVI not always available
            # assert isinstance(granule.pvi_path, str)
            assert isinstance(granule.cloud_percent, float)
            assert granule.footprint.is_valid
            assert granule.cloudmask.is_valid
            if not granule.cloudmask.is_empty:
                assert granule.cloudmask.intersects(granule.footprint)
            assert granule.nodata_mask.is_valid
            if not granule.nodata_mask.is_empty:
                assert granule.nodata_mask.intersects(granule.footprint)
            assert isinstance(granule.band_path("02"), str)
            assert isinstance(granule.band_path("02", for_gdal=True), str)
