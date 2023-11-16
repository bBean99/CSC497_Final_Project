from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import *
from qgis import processing

"""
MergeBandsAndImages:

For use with Sentinel-2 10m Resolution Imagery.
Creates virtual rasters for each spatially unique image, comprised of all bands.
Then, combines virtual rasters into mosiacked image, which is saved to the working directory of the project as 'Merged.tif'.

"""

## Create Virtual Rasters:
## For each spatially unique image, combine bands into virtual raster, load results directly into current QGIS project instance
def createVirtualRasters():
    # Determine num of and names of spatially unique images
    layerNames = []
    for l in QgsProject.instance().mapLayers().values():    
        layerNames.append(l.name())
    uniqueImages = []
    s = layerNames[0]
    uniqueImages.append(s[:len(s)-8]) #Remove band suffix to group like names
    for n in layerNames:
        if n[:len(n)-8] not in uniqueImages:
            uniqueImages.append(n[:len(n)-8])
    for n in uniqueImages:
        layerPaths = []
        for l in QgsProject.instance().mapLayers().values():
            s = l.name()
            if s[:len(s)-8] == n:
                layerPaths.append(l.source())
        processing.runAndLoadResults("gdal:buildvirtualraster",{
                                    'INPUT':layerPaths,
                                    'RESOLUTION':0,
                                    'SEPARATE':True,
                                    'PROJ_DIFFERENCE':False,
                                    'ADD_ALPHA':False,
                                    'ASSIGN_CRS':None,
                                    'RESAMPLING':0,
                                    'OUTPUT':'TEMPORARY_OUTPUT'})

# Mosiac temporary virtual rasters, load results directly into current QGIS project instance, save output to wokring directory.                      
def mosiacVirtualRasters():
    virtualLayerPaths = []
    outputPath = QgsProject.instance().homePath() + '/Merged.tif' #Create a non-temporary filepath so this raster can be utilized in further scripts
    for l in QgsProject.instance().mapLayers().values():
        if l.name() == 'Virtual':
            virtualLayerPaths.append(l.source())
    processing.runAndLoadResults("gdal:merge", {
                                'INPUT':virtualLayerPaths,
                                'PCT': False,
                                'SEPARATE':False,
                                'NODATA_INPUT':None,
                                'NODATA_OUTPUT':None,
                                'DATA_TYPE':5,
                                'OUTPUT':outputPath})    
            
createVirtualRasters()
mosiacVirtualRasters()

