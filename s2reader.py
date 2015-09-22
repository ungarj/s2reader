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
import re

def granule_identifier_to_xml_name(granule_identifier):
    '''
    Very ugly way to convert the granule identifier.
    e.g.
    From
    Granule Identifier:
    S2A_OPER_MSI_L1C_TL_SGS__20150817T131818_A000792_T28QBG_N01.03
    To
    Granule Metadata XML name:
    S2A_OPER_MTD_L1C_TL_SGS__20150817T131818_A000792_T28QCJ.xml
    '''
    # Replace "MSI" with "MTD".
    changed_item_type = re.sub("_MSI_", "_MTD_", granule_identifier)
    # Split string up by underscores.
    split_by_underscores = changed_item_type.split("_")
    del split_by_underscores[-1]
    cleaned = str()
    # Stitch string list together, adding the previously removed underscores.
    for i in split_by_underscores:
        cleaned += (i + "_")
    # Remove last underscore and append XML file extension.
    out_xml = cleaned[:-1] + ".xml"

    return out_xml


def get_granule_xml_path(granule_path, granule_identifier):
    '''
    Determines the metadata path by joining the granule path with the XML path.
    '''
    xml_name = granule_identifier_to_xml_name(granule_identifier)
    metadata_path = os.path.join(granule_path, xml_name)
    try:
        assert os.path.exists(metadata_path)
    except Exception:
        print "Granule metadata XML does not exist:", metadata_path
        raise

    return metadata_path


class Granule(object):
    '''
    This object contains relevant metadata from a granule.
    '''
    def __init__(self, granule, dataset):
        granules_path = os.path.join(dataset.path, "GRANULE")
        self.granule_identifier = granule.attrib["granuleIdentifier"]
        self.granule_path = os.path.join(granules_path, self.granule_identifier)
        self.datastrip_identifier = granule.attrib["datastripIdentifier"]
        self.metadata_path = get_granule_xml_path(
            self.granule_path,
            self.granule_identifier
            )


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
        self.product_metadata_path = get_product_metadata_path(
            manifest_safe,
            self.path
            )
        # Read product metadata XML.
        product_metadata = ET.parse(self.product_metadata_path)
        # Get timestamps.
        (
        self.product_start_time,
        self.product_stop_time,
        self.generation_time
        ) = get_timestamps(product_metadata)
        # Read processing level (e.g. Level-1C)
        self.processing_level = get_processing_level(product_metadata)
        # Get product Footprint
        self.footprint = get_footprint(product_metadata)
        # Read granule info.
        self.granules = get_granules(product_metadata, self)


def get_processing_level(product_metadata):
    '''
    Finds and returns the "Processing Level".
    '''
    for element in product_metadata.iter("Product_Info"):
        processing_level = element.find("PROCESSING_LEVEL").text
    return processing_level


def get_timestamps(product_metadata):
    '''
    Finds and returns the "Product Start Time", "Product Stop Time" and
    "Generation Time".
    '''
    for element in product_metadata.iter("Product_Info"):
        # Read timestamps.
        product_start_time = element.find("PRODUCT_START_TIME").text
        product_stop_time = element.find("PRODUCT_STOP_TIME").text
        generation_time = element.find("GENERATION_TIME").text
    return product_start_time, product_stop_time, generation_time


def get_granules(product_metadata, self):
    '''
    Finds granules information and returns a list of Granule objects.
    '''
    for element in product_metadata.iter("Product_Info"):
        product_organisation = element.find("Product_Organisation")
    granules = [
        Granule(_id.find("Granules"), self)
        for _id in product_organisation.findall("Granule_List")
        ]
    return granules


def get_footprint(product_metadata):
    '''
    Finds the footprint coordinates and returns them as a shapely
    polygon.
    '''
    product_footprint = product_metadata.iter("Product_Footprint")
    # I don't know why two "Product_Footprint" items are found.
    for element in product_footprint:
        global_footprint = None
        for global_footprint in element.iter("Global_Footprint"):
            coords = global_footprint.find("EXT_POS_LIST").text.split()
            footprint = footprint_from_coords(coords)
    assert footprint.is_valid
    return footprint


def footprint_from_coords(coords):
    '''
    Convert list of alterating latitude / longitude coordinates and returns it
    as a shapely Polygon.
    '''
    number_of_points = len(coords)/2
    coords_as_array = np.array(coords)
    reshaped = coords_as_array.reshape(number_of_points, 2)
    points = [
        (float(i[1]), float(i[0]))
        for i in reshaped.tolist()
        ]
    footprint = Polygon(points)
    try:
        assert footprint.is_valid
    except Exception:
        print "Footprint is not valid."
        raise
    return footprint


def get_product_metadata_path(manifest_safe, basepath):
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
            product_metadata_path = abspath
            try:
                assert os.path.isfile(product_metadata_path)
            except AssertionError:
                print "S2_Level-1C_product_metadata_path not found: %s" %(
                    product_metadata_path)
                raise
            return product_metadata_path
    # TBD improve error handling or, even better, improve getting the file URL.


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
