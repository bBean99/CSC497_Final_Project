from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import *
from qgis import processing
import numpy as np
import rasterio
import os

#def noDataFilter():
#    for raster in rlayers:
#        rasterPath = []
#        #print(raster.source())
#        rasterPath.append(raster.source())
#        #print(rasterPath)
#        processing.run("gdal:translate", {
#            'INPUT':rasterPath[0],
#            'TARGET_CRS':None,
#            'NODATA':0,
#            'COPY_SUBDATASETS':False,
#            'OPTIONS':'',
#            'EXTRA':'',
#            'DATA_TYPE':0,
#            'OUTPUT':rasterPath[0]+'nodataFilter'})

"""
findMinimumDataValue: Helper Function
    Takes the data of an input raster and returns the 'minimum' (that disregards outliers) value. Code was heavily inspired from this 
    post: https://gis.stackexchange.com/questions/353909/formula-dark-object-subtraction-1-qgis-semi-automatic-classification-plugin
"""
def findMinimumDataValue(inputRaster):
    uniqueValues, counts = np.unique(inputRaster, return_counts=True)
    totalSum = np.sum(inputRaster) * 0.0001
    partialSum = 0
    index = 0

    for value in uniqueValues:
        partialSum += value * counts[index]
        if partialSum >= totalSum:
            minimumDataValue = value
            break
        index += 1

    return minimumDataValue

"""
darkObjectSubtraction:
    Uses principles described in https://semiautomaticclassificationmanual.readthedocs.io/en/latest/remote_sensing.html#dos1-correction
    to preform DOS. Takes a raster and working directory path as input, and adjusts the values of the raster.
    Original raster is removed from the project, and the new atmospherically corrected one is added.
"""
def darkObjectSubtraction(raster, outputDir):
    rasterPath = raster.source()
    with rasterio.open(rasterPath) as src:
        rasterData = src.read(1)

        # Calculate the minimum data value
        minimumDataValue = findMinimumDataValue(rasterData)

        # Adjust pixel values using the specified formula
        adjustedRaster = rasterData - (minimumDataValue - 100)

        # Get metadata from the original raster
        meta = src.meta

    # Update metadata for the new raster
    meta.update(dtype=rasterio.int16, count=1)

    # Construct output raster path
    outputRasterPath = os.path.join(outputDir, f"DOS_{os.path.basename(rasterPath)}")

    # Save the atmospherically corrected raster to the new file
    with rasterio.open(outputRasterPath, 'w', **meta) as dst:
        dst.write(adjustedRaster, 1)
        
    # Add atmospherically corrected raster to project, remove original layer
    iface.addRasterLayer(outputRasterPath, f"DOS_{os.path.basename(rasterPath)}"[:-4], "gdal")
    QgsProject.instance().removeMapLayer(raster.id())

"""
createVirtualRasters:
    For each spatially unique image, combine bands into virtual raster. 
    Load results into current QGIS project instance as temporary files.
"""
def createVirtualRasters(layers):
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
                                        
"""
mosiacVirtualRasters:
    Mosiac temporary virtual rasters.
    Load results directly into current QGIS project instance, save output to wokring directory.                      
"""
def mosiacVirtualRasters():
    virtualLayerPaths = []
    # Create a non-temporary filepath so this raster can be utilized in further preprocessing
    outputPath = QgsProject.instance().homePath() + '/Merged.tif' 
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
                                
"""
BandIndicesAndEnhancments:

Applies band index or enhancement to 'clippedRaster.tif'
Saves new rasters in working directory.
Example provided is the NDVI Vegetation Index

"""
# NDVI Function: For use as a Vegetation Index: NDVI = (NIR-Red)/(NIR+Red)
def ndvi(outputPath):
    rasterPath = outputPath + '/Merged.tif'
    processing.runAndLoadResults('gdal:rastercalculator', {
                                'INPUT_A':rasterPath,'BAND_A':4,
                                'INPUT_B':rasterPath,'BAND_B':3,
                                'FORMULA':'(A-B)/(A+B)',
                                'NO_DATA':None,
                                'RTYPE':5,
                                'OUTPUT':outputPath + '/NDVI.tif'})




# Usage:

# Get project directory
rlayers = list(QgsProject.instance().mapLayers().values())
outputDirectory = os.path.dirname(inputRasterPath)

# No Data Filter *Currently not working/not necessary
#noDataFilter()

# Atmospheric Correction
for i in range(0, len(rlayers)):
    inputRaster = rlayers[i]
    darkObjectSubtraction(inputRaster, outputDirectory)
    
# Merge Bands and Images:

# Re-update list of current layers
rlayers = list(QgsProject.instance().mapLayers().values())

createVirtualRasters(rlayers)
mosiacVirtualRasters()

# NDVI Band Index:

# Defining path to project and working raster
homePath = QgsProject.instance().homePath()

ndvi(homePath)
    