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

    






