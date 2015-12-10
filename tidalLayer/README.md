Tidally Influenced Areas
========================

The tidally influenced zones are created from the [U.S. Fish & Wildlife National 
Wetlands Inventory](http://www.fws.gov/wetlands/Data/Data-Download.html) polygon 
layers. The ArcPy script indexes all of the polygons that have any form of tidal 
influence as defined by the >>>>attributes file (LINK)<<<<<. 

The polygons are joined together and output in a single shapefile representing 
all bodies of water within the SHEDS range that are impacted by tide.


## Steps to Run:

1. Open the script `createTidalShapefile.py`

2. Change the values in the "Specify inputs" section of the script
 - `baseDirectory` is the path to the folder to output spatial data
 - `states` is the list of state abbreviations that identify the layers to use from the FWS data
 - `wetlandsFolder` is the source folder containing the downloaded wetlands datasets by state

3. Execute the script in Arc Python.



