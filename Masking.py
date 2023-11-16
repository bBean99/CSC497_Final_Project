from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import *
from qgis import processing

"""
Masking:

Takes the 'Merged.tif' raster and clips it by the vector boundaries from 'Mask.shp' 
Saves clipped raster to working directory as 'clippedRaster.tif'

"""

# Defining path to project and working raster
outputPath = QgsProject.instance().homePath()
rasterPath = outputPath + '/Merged.tif'

# Use QGIS clipping tool, load results directly into current QGIS project instance, save output to wokring directory. 
def masking():    
    processing.runAndLoadResults("gdal:cliprasterbymasklayer", {
                                'INPUT': rasterPath,
                                'MASK': outputPath + '/Mask.shp',
                                'ALPHA_BAND':False,
                                'CROP_TO_CUTLINE':True,
                                'KEEP_RESOLUTION':False,
                                'SET_RESOLUTION':False,
                                'X_RESOLUTION':None,
                                'Y_RESOLUTION':None,
                                'MULTITHREADING':False,'DATA_TYPE':0,
                                'OUTPUT':outputPath + '/clippedRaster.tif'})
        
masking()