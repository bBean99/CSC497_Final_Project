# CSC497_Final_Project
README


Remote Sensing Imagery QGIS Preprocessing Scripts


The collection of scripts contained within this folder are for usage in preprocessing multiple datasets of remote sensing imagery for the Sentinel-2 Satellite, particularly for coastal studies regarding the detection of macro-algaes, such as kelp. The scripts are designed to be utilized in a QGIS project environment, in conjunction with manual manipulation of data.


Prerequisites


* QGIS desktop


Code has been tested and is functional in QGIS desktop 3.16.11, other versions likely capable of running these scripts, but untested.


Usage


1. Open a new QGIS project, and save the project to your desired working directory.


2. Place whatever remote sensing images you want to work with in this directory, along with the folder containing this readme and the python scripts.


3. Add ONLY your images as raster layers to the QGIS project.


4. Navigate to the ‘Plugins’ button on the QGIS toolbar, and open the Python Console .


   1. Click the ‘Show Editor’ button in the Python console and add the three scripts contained in this file.


5. Run the MergeBandsAndImages.py script.


6. Conduct manual geometric and atmospheric correction of the data if necessary.


7. Add your masking layer as a vector to the QGIS project, ensure it is named ‘Mask.shp’


   2. Run the Masking.py script


8. If Band Indices or Enchancements are required, run the BandIndicesAndEnhancements.py script (Note, this is an example file that only contains NDVI)


Contact


Author - Sean Turney - email: turney.sean.d@gmail.com
