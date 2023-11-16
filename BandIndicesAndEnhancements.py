from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import *
from qgis import processing

"""
BandIndicesAndEnhancments:

Applies band index or enhancement to 'clippedRaster.tif'
Saves new rasters in working directory.
Example provided is the NDVI Vegetation Index

"""

# Defining path to project and working raster
outputPath = QgsProject.instance().homePath()
rasterPath = outputPath + '/clippedRaster.tif'

# NDVI Function: For use as a Vegetation Index: NDVI = (NIR-Red)/(NIR+Red)
def ndvi():
    processing.runAndLoadResults('gdal:rastercalculator', {
                                'INPUT_A':rasterPath,'BAND_A':4,
                                'INPUT_B':rasterPath,'BAND_B':3,
                                'FORMULA':'(A-B)/(A+B)',
                                'NO_DATA':None,
                                'RTYPE':5,
                                'OUTPUT':outputPath + '/NDVI.tif'})

ndvi()
