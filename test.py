#!/usr/bin/env python

from s2reader import *

dataset = SentinelDataSet("../../geodata/S2A/S2A_OPER_PRD_MSIL1C_PDMC_20150818T101516_R022_V20150813T102406_20150813T102406.SAFE/")

# Paths
print "dataset.path:", dataset.path
print "dataset.product_metadata:", dataset.product_metadata

# Timestamps
print "dataset.product_start_time:", dataset.product_start_time
print "dataset.product_stop_time:", dataset.product_stop_time
print "dataset.generation_time:", dataset.generation_time

# Processing level
print "dataset.processing_level:", dataset.processing_level

# Footprint
print "dataset.footprint:", dataset.footprint
#print "dataset.bounds:", dataset.bounds
#print "dataset.bbox:", dataset.bbox