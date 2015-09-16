#!/usr/bin/env python
'''
This module implements an easy abstraction to the SAFE data format used by the
Sentinel 2 misson of the European Space Agency (ESA)
'''

import os
import sys
import xml.etree.ElementTree as ET
from shapely.geometry import Polygon
import numpy as np

# create class SentinelDataSet

# attributes:

# .granules
## List of granules found. / iterator
## use granuleIdentifier as subfolder, IMAGE_ID + jp2 as file name
# .bbox
## Bounding box in WGS84.
## type: geometry
# .footprint
## Footprint in WGS84
# .product_start_time
## TBD
## type: timestamp
# .producut_stop_time
## TBD
## type: timestamp
# .processing_level
## TBD e.g. Level-1C
## type: string
# .generation_time
## TBD
## type: timestamp
# .band_name
## Name of band
## type: string

class Granule(object):
    '''
    This object contains relevant metadata from a granule.
    '''

    def __init__(self, granule_identifier):
        self.granule_identifier = granule_identifier


class SentinelDataSet(object):
    '''
    This object contains relevant metadata from the SAFE file and its containing
    granules as Granule() object.
    '''

    def __init__(self, path):
        self.path = os.path.normpath(path)

        # Find manifest.safe.
        manifest_safe = os.path.join(self.path, "manifest.safe")
        try:
            assert os.path.isfile(manifest_safe)
        except AssertionError:
            error = "manifest.safe not found: %s" %(manifest_safe)
            sys.exit(error)

        # Read manifest.safe.
        self.product_metadata = get_product_metadata(manifest_safe, self.path)

        # Read product metadata XML.
        product_metadata_xml = ET.parse(self.product_metadata)
        for element in product_metadata_xml.iter("Product_Info"):

            # Read timestamps.
            self.product_start_time = element.find("PRODUCT_START_TIME").text
            self.product_stop_time = element.find("PRODUCT_STOP_TIME").text
            self.generation_time = element.find("GENERATION_TIME").text

            # Read processing level (e.g. Level-1C)
            self.processing_level = element.find("PROCESSING_LEVEL").text

        # Get product Footprint
        product_footprint = product_metadata_xml.iter("Product_Footprint")
        # I don't know why two "Product_Footprint items are found."
        for element in product_footprint:
            global_footprint = None
            for global_footprint in element.iter("Global_Footprint"):
                coords = global_footprint.find("EXT_POS_LIST").text.split()
                self.footprint = footprint_from_coords(coords)

        # Read granule info.
        granule_list = []
        for element in product_metadata_xml.iter("Product_Info"):
            product_organisation = element.find("Product_Organisation")

        self.granules = [
            Granule(id.find("Granules").attrib["datastripIdentifier"])
            for id in product_organisation.findall("Granule_List")
            ]

def footprint_from_coords(coords):
    '''
    Convert list of alterating latitude / longitude coordinates and returns it
    as a shapely Polygon.
    '''
    number_of_points = len(coords)/2
    coords_as_array = np.array(coords)
    reshaped = coords_as_array.reshape(number_of_points, 2)
    points = []
    for i in reshaped.tolist():
        points.append((float(i[1]), float(i[0])))
    footprint = Polygon(points)
    try:
        assert footprint.is_valid
    except Exception:
        print "Footprint is not valid."
        raise
    return footprint


def get_product_metadata(manifest_safe, basepath):
    '''
    Returns path to product metadata XML file.
    '''
    manifest = ET.parse(manifest_safe)
    data_object_section = manifest.find("dataObjectSection")
    for data_object in data_object_section:
        # Find product metadata XML.
        if data_object.attrib.get("ID") == "S2_Level-1C_Product_Metadata":
            relpath = data_object.iter("fileLocation").next().attrib["href"]
            abspath = os.path.join(basepath, relpath)
            product_metadata = abspath
            try:
                assert os.path.isfile(product_metadata)
            except AssertionError:
                error = "S2_Level-1C_Product_Metadata not found: %s" %(
                    product_metadata)
                raise
            return product_metadata
    return None



# each Granule:

# .MGRS_identifier
## MGRS string
# .bbox
## Bounding box in WGS84.
## type: geometry
# .footprint
## Footprint in WGS84
# .product_start_time
## TBD
## type: timestamp
# .producut_stop_time
## TBD
## type: timestamp
# .processing_level
## TBD e.g. Level-1C
## type: string
# .generation_time
## TBD
## type: timestamp
# .band_names

# each path:

# .<band_name>.path


# --> Image_Display_Order
