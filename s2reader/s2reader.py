#!/usr/bin/env python
'''
This module implements an easy abstraction to the SAFE data format used by the
Sentinel 2 misson of the European Space Agency (ESA)
'''

import os
from lxml.etree import parse
from shapely.geometry import Polygon, box
from shapely.ops import transform
from functools import partial
import pyproj
import numpy as np
import re

def open(safe_file):
    """
    Returns a SentinelDataSet object.
    """
    try:
        assert os.path.isdir(safe_file)
    except AssertionError:
        raise IOError("file not found")

    return SentinelDataSet(safe_file)


class SentinelDataSet(object):
    '''
    This object contains relevant metadata from the SAFE file and its containing
    granules as SentinelGranule() object.
    '''
    def __init__(self, path):
        self.path = os.path.normpath(path)

        # Find manifest.safe.
        self.manifest_safe = os.path.join(self.path, "manifest.safe")
        try:
            assert os.path.isfile(self.manifest_safe)
        except AssertionError:
            raise IOError("manifest.safe not found: %s" %(self.manifest_safe))

        # Read product metadata XML.
        self._product_metadata = parse(self.product_metadata_path)

    @property
    def product_metadata_path(self):
        '''Returns path to product metadata XML file.'''
        manifest = parse(self.manifest_safe)
        data_object_section = manifest.find("dataObjectSection")
        for data_object in data_object_section:
            # Find product metadata XML.
            if data_object.attrib.get("ID") == "S2_Level-1C_Product_Metadata":
                relpath = data_object.iter("fileLocation").next().attrib["href"]
                abspath = os.path.join(self.path, relpath)
                product_metadata_path = abspath
                try:
                    assert os.path.isfile(product_metadata_path)
                except AssertionError:
                    raise IOError("S2_Level-1C_product_metadata_path not found")
                return product_metadata_path

    @property
    def product_start_time(self):
        '''Finds and returns "Product Start Time"'''
        for element in self._product_metadata.iter("Product_Info"):
            return element.find("PRODUCT_START_TIME").text

    @property
    def product_stop_time(self):
        '''Finds and returns the "Product Stop Time".'''
        for element in self._product_metadata.iter("Product_Info"):
            return element.find("PRODUCT_STOP_TIME").text

    @property
    def generation_time(self):
        '''Finds and returns the "Generation Time".'''
        for element in self._product_metadata.iter("Product_Info"):
            return element.find("GENERATION_TIME").text

    @property
    def processing_level(self):
        '''Finds and returns the "Processing Level".'''
        for element in self._product_metadata.iter("Product_Info"):
            return element.find("PROCESSING_LEVEL").text

    @property
    def footprint(self):
        '''Returns product footprint.'''
        product_footprint = self._product_metadata.iter("Product_Footprint")
        # I don't know why two "Product_Footprint" items are found.
        for element in product_footprint:
            global_footprint = None
            for global_footprint in element.iter("Global_Footprint"):
                coords = global_footprint.find("EXT_POS_LIST").text.split()
                return _footprint_from_coords(coords)

    @property
    def granules(self):
        '''
        Finds granules information and returns a list of SentinelGranule
        objects.
        '''
        for element in self._product_metadata.iter("Product_Info"):
            product_organisation = element.find("Product_Organisation")
        granules = [
            SentinelGranule(_id.find("Granules"), self)
            for _id in product_organisation.findall("Granule_List")
            ]
        return granules

    def granule_paths(self, band_id):
        """Returns the path of all granules of a given band."""
        band_id = str(band_id).zfill(2)
        try:
            assert isinstance(band_id, str)
            assert band_id in BAND_IDS
        except AssertionError:
            raise AttributeError(
                "band ID not valid: %s" % band_id
                )
        return [
            granule.band_path(band_id)
            for granule in self.granules
            ]

    def __enter__(self):
        return self

    def __exit__(self, t, v, tb):
        pass


BAND_IDS = ["01", "02", "03", "04", "05", "06", "07", "08", "8A", "09", "10",
    "11", "12"]


class SentinelGranule(object):
    '''
    This object contains relevant metadata from a granule.
    '''
    def __init__(self, granule, dataset):
        granules_path = os.path.join(dataset.path, "GRANULE")
        self.granule_identifier = granule.attrib["granuleIdentifier"]
        self.granule_path = os.path.join(granules_path, self.granule_identifier)
        self.datastrip_identifier = granule.attrib["datastripIdentifier"]
        self._metadata = parse(self.metadata_path)

    @property
    def srid(self):
        tile_geocoding = self._metadata.iter("Tile_Geocoding").next()
        return tile_geocoding.findall("HORIZONTAL_CS_CODE")[0].text

    @property
    def metadata_path(self):
        '''
        Determines the metadata path by joining the granule path with the XML
        path.
        '''
        xml_name = _granule_identifier_to_xml_name(self.granule_identifier)
        metadata_path = os.path.join(self.granule_path, xml_name)
        try:
            assert os.path.exists(metadata_path)
        except AssertionError:
            raise IOError("Granule metadata XML does not exist:", metadata_path)
        return metadata_path

    @property
    def footprint(self):
        '''
        Finds the footprint coordinates and returns them as a shapely
        polygon.
        '''
        # Check whether product or granule footprint needs to be calculated.
        tile_geocoding = self._metadata.iter("Tile_Geocoding").next()
        resolution = 10
        searchstring = ".//*[@resolution='%s']" %(resolution)
        size, geoposition = tile_geocoding.findall(searchstring)
        nrows, ncols = (int(i.text) for i in size)
        ulx, uly, xdim, ydim = (int(i.text) for i in geoposition)
        lrx = ulx + nrows * resolution
        lry = uly - ncols * resolution
        utm_footprint = box(ulx, lry, lrx, uly)
        project = partial(
            pyproj.transform,
            pyproj.Proj(init=self.srid),
            pyproj.Proj(init='EPSG:4326')
            )
        footprint = transform(project, utm_footprint)
        return footprint

    def band_path(self, band_id):
        band_id = str(band_id).zfill(2)
        try:
            assert isinstance(band_id, str)
            assert band_id in BAND_IDS
        except AssertionError:
            raise AttributeError(
                "band ID not valid: %s" % band_id
                )
        return os.path.join(
            os.path.join(self.granule_path, "IMG_DATA"),
            "".join([
                    "_".join((self.granule_identifier).split("_")[:-1]),
                    "_B",
                    band_id,
                    ".jp2"
                ])
            )

def _granule_identifier_to_xml_name(granule_identifier):
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

def _footprint_from_coords(coords):
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
