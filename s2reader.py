#!/usr/bin/env python

import os
import sys
import xml.etree.ElementTree as ET
from shapely.geometry import *
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

class SentinelDataSet():

    def __init__(self, path):
        self.path = os.path.normpath(path)
        basename = os.path.splitext(os.path.basename(self.path))[0]

        # Find manifest.safe.
        manifest_safe = os.path.join(self.path, "manifest.safe")
        try:
            assert os.path.isfile(manifest_safe)
        except:
            error = "manifest.safe not found: %s" %(manifest_safe)
            sys.exit(error)

        # Read manifest.safe.
        manifest = ET.parse(manifest_safe)
        dataObjectSection = manifest.find("dataObjectSection")
        for dataObject in dataObjectSection:
            # Find product metadata XML.
            if dataObject.attrib.get("ID") == "S2_Level-1C_Product_Metadata":
                relpath = dataObject.iter("fileLocation").next().attrib["href"]
                abspath = os.path.join(self.path, relpath)
                self.product_metadata = abspath
                try:
                    assert os.path.isfile(self.product_metadata)
                except:
                    error = "S2_Level-1C_Product_Metadata not found: %s" %(
                        self.product_metadata)
                    sys.exit(error)

        # Read product metadata XML.
        product_metadata_xml = ET.parse(self.product_metadata)
        for element in product_metadata_xml.iter("Product_Info"):

            # Read timestamps.
            self.product_start_time = element.find("PRODUCT_START_TIME").text
            self.product_stop_time = element.find("PRODUCT_STOP_TIME").text
            self.generation_time = element.find("GENERATION_TIME").text

            # Read processing level (e.g. Level-1C)
            self.processing_level = element.find("PROCESSING_LEVEL").text

        # Get Footprint
        product_footprint = product_metadata_xml.iter("Product_Footprint")
        # I don't know why two "Product_Footprint items are found."
        for element in product_footprint:
            global_footprint = None
            for global_footprint in element.iter("Global_Footprint"):
                coords = global_footprint.find("EXT_POS_LIST").text.split()
                number_of_points = len(coords)/2
                reshaped = np.array(coords).reshape(number_of_points, 2)
                points = []
                for i in reshaped.tolist():
                    points.append((float(i[1]), float(i[0])))
                self.footprint = Polygon(points)



# each Granule:

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



def herbert():
    print "herbert"