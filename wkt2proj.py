#!/usr/bin/env python

import os
import sys
import string
import osgeo.osr

if (len(sys.argv) <> 2):
        print 'Usage: wkt2proj.py [WKT Projection Text]'
else:
        srs = osgeo.osr.SpatialReference()
        srs.ImportFromWkt(sys.argv[1])
        print srs.ExportToProj4()