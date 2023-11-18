from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import *
from qgis import processing

layers = list(QgsProject.instance().mapLayers().values())
#print(layers)

## Create Virtual Rasters:
## For each spatially unique image, combine bands into virtual raster, load results into current QGIS project instance as temporary files
def createVirtualRasters():
    uniqueExtents = []
    uniqueExtents.append(layers[0].extent())

    # Determine raster extent of each unique image
    for r in range(1, len(layers)):
        if layers[r].extent() != layers[r-1].extent():
            uniqueExtents.append(layers[r].extent())
    
    # If all the image extents are unique (single band), reduce processing time and create a virtual raster for each. 
    if len(uniqueExtents) == len(layers):
        # Initialize list to store raster sources
        layerPaths = []
        
        # Get raster sources
        for raster in layers:
            layerPaths.append(raster.source())
            
        # Build virtual rasters
        processing.runAndLoadResults("gdal:buildvirtualraster",{
                                            'INPUT':layerPaths,
                                            'RESOLUTION':0,
                                            'SEPARATE':True,
                                            'PROJ_DIFFERENCE':False,
                                            'ADD_ALPHA':False,
                                            'ASSIGN_CRS':None,
                                            'RESAMPLING':0,
                                            'OUTPUT':'TEMPORARY_OUTPUT'})    
        
    else:
        #For each unique image extent with multiple bands, create a virtual raster
        for ext in uniqueExtents:
            layerPaths = []
            for ras in layers:
                extent = ras.extent()
                if ras.extent() == ext:
                    layerPaths.append(ras.source())
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