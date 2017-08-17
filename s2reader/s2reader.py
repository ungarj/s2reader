#!/usr/bin/env python
"""
s2reader reads and processes Sentinel-2 L1C SAFE archives.

This module implements an easy abstraction to the SAFE data format used by the
Sentinel 2 misson of the European Space Agency (ESA)
"""

import os
from lxml.etree import parse, fromstring
from shapely.geometry import Polygon, MultiPolygon, box
from shapely.ops import transform
from functools import partial
import pyproj
import numpy as np
import re
from cached_property import cached_property
import zipfile


def open(safe_file):
    """Return a SentinelDataSet object."""
    try:
        assert os.path.isdir(safe_file) or os.path.isfile(safe_file)
    except AssertionError:
        raise IOError("file not found: %s" % safe_file)

    return SentinelDataSet(safe_file)


class SentinelDataSet(object):
    """
    Return SentinelDataSet object.

    This object contains relevant metadata from the SAFE file and its containing
    granules as SentinelGranule() object.
    """

    def __init__(self, path):
        """Assert correct path and initialize."""
        filename, extension = os.path.splitext(os.path.normpath(path))
        try:
            assert extension in [".SAFE", ".ZIP", ".zip"]
        except AssertionError:
            raise IOError("only .SAFE folders or zipped .SAFE folders allowed")
        self.is_zip = True if extension in [".ZIP", ".zip"] else False
        self.path = os.path.normpath(path)

        if self.is_zip:
            self._zipfile = zipfile.ZipFile(self.path, 'r')
            self._zip_root = os.path.basename(filename)
            if self._zip_root not in self._zipfile.namelist():
                if not filename.endswith(".SAFE"):
                    self._zip_root = os.path.basename(filename) + ".SAFE/"
                else:
                    self._zip_root = os.path.basename(filename) + "/"
                try:
                    assert self._zip_root in self._zipfile.namelist()
                except:
                    raise IOError("unknown zipfile structure")
            self.manifest_safe_path = os.path.join(
                self._zip_root, "manifest.safe")
        else:
            self._zipfile = None
            self._zip_root = None
            # Find manifest.safe.
            self.manifest_safe_path = os.path.join(self.path, "manifest.safe")

        try:
            assert os.path.isfile(self.manifest_safe_path) or \
                self.manifest_safe_path in self._zipfile.namelist()
        except AssertionError:
            raise IOError(
                "manifest.safe not found: %s" % self.manifest_safe_path
                )

    @cached_property
    def _product_metadata(self):
        if self.is_zip:
            return fromstring(self._zipfile.read(self.product_metadata_path))
        else:
            return parse(self.product_metadata_path)

    @cached_property
    def _manifest_safe(self):
        if self.is_zip:
            return fromstring(self._zipfile.read(self.manifest_safe_path))
        else:
            return parse(self.manifest_safe_path)

    @cached_property
    def product_metadata_path(self):
        """Return path to product metadata XML file."""
        data_object_section = self._manifest_safe.find("dataObjectSection")
        for data_object in data_object_section:
            # Find product metadata XML.
            if data_object.attrib.get("ID") == "S2_Level-1C_Product_Metadata":
                relpath = os.path.relpath(
                    data_object.iter("fileLocation").next().attrib["href"])
                try:
                    if self.is_zip:
                        abspath = os.path.join(self._zip_root, relpath)
                        assert abspath in self._zipfile.namelist()
                    else:
                        abspath = os.path.join(self.path, relpath)
                        assert os.path.isfile(abspath)
                except AssertionError:
                    raise IOError(
                        "S2_Level-1C_product_metadata_path not found: %s \
                        " % abspath
                        )
                return abspath

    @cached_property
    def product_start_time(self):
        """Find and returns "Product Start Time"."""
        for element in self._product_metadata.iter("Product_Info"):
            return element.find("PRODUCT_START_TIME").text

    @cached_property
    def product_stop_time(self):
        """Find and returns the "Product Stop Time"."""
        for element in self._product_metadata.iter("Product_Info"):
            return element.find("PRODUCT_STOP_TIME").text

    @cached_property
    def generation_time(self):
        """Find and returns the "Generation Time"."""
        for element in self._product_metadata.iter("Product_Info"):
            return element.findtext("GENERATION_TIME")

    @cached_property
    def processing_level(self):
        """Find and returns the "Processing Level"."""
        for element in self._product_metadata.iter("Product_Info"):
            return element.findtext("PROCESSING_LEVEL")

    @cached_property
    def product_type(self):
        """Find and returns the "Product Type"."""
        for element in self._product_metadata.iter("Product_Info"):
            return element.findtext("PRODUCT_TYPE")

    @cached_property
    def spacecraft_name(self):
        """Find and returns the "Spacecraft name"."""
        for element in self._product_metadata.iter("Datatake"):
            return element.findtext("SPACECRAFT_NAME")

    @cached_property
    def sensing_orbit_number(self):
        """Find and returns the "Sensing orbit number"."""
        for element in self._product_metadata.iter("Datatake"):
            return element.findtext("SENSING_ORBIT_NUMBER")

    @cached_property
    def sensing_orbit_direction(self):
        """Find and returns the "Sensing orbit direction"."""
        for element in self._product_metadata.iter("Datatake"):
            return element.findtext("SENSING_ORBIT_DIRECTION")

    @cached_property
    def product_format(self):
        """Find and returns the Safe format."""
        for element in self._product_metadata.iter("Query_Options"):
            return element.findtext("PRODUCT_FORMAT")

    @cached_property
    def footprint(self):
        """Return product footprint."""
        product_footprint = self._product_metadata.iter("Product_Footprint")
        # I don't know why two "Product_Footprint" items are found.
        for element in product_footprint:
            global_footprint = None
            for global_footprint in element.iter("Global_Footprint"):
                coords = global_footprint.findtext("EXT_POS_LIST").split()
                return _polygon_from_coords(coords)

    @cached_property
    def granules(self):
        """Return list of SentinelGranule objects."""
        for element in self._product_metadata.iter("Product_Info"):
            product_organisation = element.find("Product_Organisation")
        if self.product_format == 'SAFE':
            return [
                SentinelGranule(_id.find("Granules"), self)
                for _id in product_organisation.findall("Granule_List")
                ]
        elif self.product_format == 'SAFE_COMPACT':
            return [
                SentinelGranuleCompact(_id.find("Granule"), self)
                for _id in product_organisation.findall("Granule_List")
                ]
        else:
            raise Exception("PRODUCT_FORMAT not recognized in metadata file, found: '" + str(self.safe_format) + "' accepted are 'SAFE' and 'SAFE_COMPACT'")
    def granule_paths(self, band_id):
        """Return the path of all granules of a given band."""
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
        """Return self."""
        return self

    def __exit__(self, t, v, tb):
        """Do cleanup."""
        try:
            self._zipfile.close()
        except AttributeError:
            pass

BAND_IDS = [
    "01", "02", "03", "04", "05", "06", "07", "08", "8A", "09", "10",
    "11", "12"]


class SentinelGranule(object):
    """This object contains relevant metadata from a granule."""

    def __init__(self, granule, dataset):
        """Prepare data paths depending on if ZIP or not."""
        self.dataset = dataset
        if self.dataset.is_zip:
            granules_path = os.path.join(self.dataset._zip_root, "GRANULE")
        else:
            granules_path = os.path.join(dataset.path, "GRANULE")
        self.granule_identifier = granule.attrib["granuleIdentifier"]
        self.granule_path = os.path.join(
            granules_path, self.granule_identifier)
        self.datastrip_identifier = granule.attrib["datastripIdentifier"]

    @cached_property
    def _metadata(self):
        if self.dataset.is_zip:
            return fromstring(self.dataset._zipfile.read(self.metadata_path))
        else:
            return parse(self.metadata_path)

    @cached_property
    def _nsmap(self):
        if self.dataset.is_zip:
            root = self._metadata
        else:
            root = self._metadata.getroot()
        return {
            k: v
            for k, v in root.nsmap.iteritems()
            if k
            }

    @cached_property
    def srid(self):
        """Return EPSG code."""
        tile_geocoding = self._metadata.iter("Tile_Geocoding").next()
        return tile_geocoding.findtext("HORIZONTAL_CS_CODE")

    @cached_property
    def metadata_path(self):
        """Determine the metadata path."""
        xml_name = _granule_identifier_to_xml_name(self.granule_identifier)
        metadata_path = os.path.join(self.granule_path, xml_name)
        try:
            assert os.path.isfile(metadata_path) or \
                metadata_path in self.dataset._zipfile.namelist()
        except AssertionError:
            raise IOError(
                "Granule metadata XML does not exist:", metadata_path)
        return metadata_path

    @cached_property
    def pvi_path(self):
        """Determine the PreView Image (PVI) path inside the SAFE pkg."""
        pvi_name = self._metadata.iter("PVI_FILENAME").next().text
        pvi_path = os.path.join(self.granule_path, "QI_DATA", pvi_name) + ".jp2"
        try:
            assert os.path.isfile(pvi_path) or \
                pvi_path in self.dataset._zipfile.namelist()
        except AssertionError:
            raise IOError(
                "PVI path does not exist:", pvi_path)
        return pvi_path

    @cached_property
    def cloud_percent(self):
        """Return percentage of cloud coverage."""
        image_content_qi = self._metadata.findtext(
            (
                """n1:Quality_Indicators_Info/Image_Content_QI/"""
                """CLOUDY_PIXEL_PERCENTAGE"""
            ),
            namespaces=self._nsmap)
        return float(image_content_qi)

    @cached_property
    def footprint(self):
        """Find and return footprint as Shapely Polygon."""
        # Check whether product or granule footprint needs to be calculated.
        tile_geocoding = self._metadata.iter("Tile_Geocoding").next()
        resolution = 10
        searchstring = ".//*[@resolution='%s']" % resolution
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

    @cached_property
    def cloudmask(self):
        """Return cloudmask as a GeoJSON like list."""
        polys = list(self._get_mask(mask_type="MSK_CLOUDS"))
        return MultiPolygon([
            poly["geometry"]
            for poly in polys
            if poly["attributes"]["maskType"] == "OPAQUE"
        ])

    @cached_property
    def nodata_mask(self):
        """Return nodata mask as Shapely Polygon."""
        return MultiPolygon(list(self._get_mask(mask_type="MSK_NODATA")))

    def band_path(self, band_id, for_gdal=False):
        """Return paths of given band's jp2 files for all granules."""
        band_id = str(band_id).zfill(2)
        try:
            assert isinstance(band_id, str)
            assert band_id in BAND_IDS
        except AssertionError:
            raise AttributeError(
                "band ID not valid: %s" % band_id
                )
        if self.dataset.is_zip:
            # zip_prefix = "zip://!"
            zip_prefix = "/vsizip/"
            granule_basepath = zip_prefix + os.path.join(
                self.dataset.path, self.granule_path)
        else:
            granule_basepath = self.granule_path
        return os.path.join(
            os.path.join(granule_basepath, "IMG_DATA"),
            "".join([
                    "_".join((self.granule_identifier).split("_")[:-1]),
                    "_B",
                    band_id,
                    ".jp2"
                    ])
            )

    def _get_mask(self, mask_type=None):
        assert mask_type
        exterior_str = str(
            "eop:extentOf/gml:Polygon/gml:exterior/gml:LinearRing/gml:posList"
        )
        interior_str = str(
            "eop:extentOf/gml:Polygon/gml:interior/gml:LinearRing/gml:posList"
        )
        for item in self._metadata.iter("Pixel_Level_QI").next():
            if item.attrib.get("type") == mask_type:
                gml = os.path.join(
                    self.granule_path, "QI_DATA", os.path.basename(item.text)
                )
        if self.dataset.is_zip:
            root = fromstring(self.dataset._zipfile.read(gml))
        else:
            root = parse(gml).getroot()
        nsmap = {k: v for k, v in root.nsmap.iteritems() if k}
        try:
            for mask_member in root.iterfind(
                    "eop:maskMembers", namespaces=nsmap):
                for feature in mask_member:
                    _type = feature.findtext(
                        "eop:maskType", namespaces=nsmap)
                    ext_pts = feature.find(exterior_str, nsmap).text.split()
                    exterior = _polygon_from_coords(
                        ext_pts,
                        fix_geom=True,
                        swap=False
                    )
                    try:
                        interiors = [
                            _polygon_from_coords(
                                int_pts.text.split(),
                                fix_geom=True,
                                swap=False
                            )
                            for int_pts in feature.findall(interior_str, nsmap)
                            ]
                    except AttributeError:
                        interiors = []
                    project = partial(
                        pyproj.transform,
                        pyproj.Proj(init=self.srid),
                        pyproj.Proj(init='EPSG:4326')
                        )

                    yield dict(
                        geometry=transform(
                            project, Polygon(exterior, interiors)
                            ),
                        attributes=dict(
                            maskType=_type
                            )
                        )
        except StopIteration:
            yield dict(
                geometry=Polygon(),
                attributes=dict(
                    maskType=None
                    )
                )
            raise StopIteration()

class SentinelGranuleCompact(SentinelGranule):
    """This object contains relevant metadata from a granule."""

    def __init__(self, granule, dataset):
        """Prepare data paths depending on if ZIP or not."""
        self.dataset = dataset
        if self.dataset.is_zip:
            granules_path = self.dataset._zip_root
        else:
            granules_path = dataset.path
        self.granule_identifier = granule.attrib["granuleIdentifier"]
        #extract the granule folder name by an IMAGE_FILE name
        image_file_name = granule.find("IMAGE_FILE").text
        image_file_name_arr = image_file_name.split("/")
        self.granule_path = os.path.join(
            granules_path, image_file_name_arr[0], image_file_name_arr[1])
        self.datastrip_identifier = granule.attrib["datastripIdentifier"]

    @cached_property
    def metadata_path(self):
        """Determine the metadata path."""
        metadata_path = os.path.join(self.granule_path, 'MTD_TL.xml')
        try:
            assert os.path.isfile(metadata_path) or \
                metadata_path in self.dataset._zipfile.namelist()
        except AssertionError:
            raise IOError(
                "Granule metadata XML does not exist:", metadata_path)
        return metadata_path

    @cached_property
    def pvi_path(self):
        """Determine the PreView Image (PVI) path inside the SAFE pkg."""
        pvi_name = self._metadata.iter("PVI_FILENAME").next().text
        pvi_name = pvi_name.split("/")
        pvi_path = os.path.join(self.granule_path, pvi_name[len(pvi_name)-2], pvi_name[len(pvi_name)-1])
        try:
            assert os.path.isfile(pvi_path) or \
                pvi_path in self.dataset._zipfile.namelist()
        except AssertionError:
            raise IOError(
                "PVI path does not exist:", pvi_path)
        return pvi_path

def _granule_identifier_to_xml_name(granule_identifier):
    """
    Very ugly way to convert the granule identifier.

    e.g.
    From
    Granule Identifier:
    S2A_OPER_MSI_L1C_TL_SGS__20150817T131818_A000792_T28QBG_N01.03
    To
    Granule Metadata XML name:
    S2A_OPER_MTD_L1C_TL_SGS__20150817T131818_A000792_T28QBG.xml
    """
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


def _polygon_from_coords(coords, fix_geom=False, swap=True):
    """
    Return Shapely Polygon from coordinates.

    - coords: list of alterating latitude / longitude coordinates
    - fix_geom: automatically fix geometry
    """
    number_of_points = len(coords)/2
    coords_as_array = np.array(coords)
    reshaped = coords_as_array.reshape(number_of_points, 2)
    points = [
        (float(i[1]), float(i[0])) if swap else ((float(i[0]), float(i[1])))
        for i in reshaped.tolist()
        ]
    polygon = Polygon(points)
    try:
        assert polygon.is_valid
        return polygon
    except AssertionError:
        if fix_geom:
            return polygon.buffer(0)
        else:
            raise RuntimeError("Geometry is not valid.")
