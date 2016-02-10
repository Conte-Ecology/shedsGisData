Tidally Influenced Areas
========================

The tidally influenced zones are created from the [U.S. Fish & Wildlife National 
Wetlands Inventory](http://www.fws.gov/wetlands/Data/Data-Download.html) polygon 
layers. The ArcPy script indexes all of the polygons that have any form of tidal 
influence as defined by the [NWI Wetlands and Deepwater Map Code Diagram](http://www.fws.gov/wetlands/Documents/NWI_Wetlands_and_Deepwater_Map_Code_Diagram.pdf).

The polygons are joined together and output in a single shapefile representing 
all bodies of water within the SHEDS range that are impacted by tide.


## Steps to Run:

1. Open the script `createTidalShapefile.py`

2. Change the values in the "Specify inputs" section of the script
 - `baseDirectory` is the path to the folder to output spatial data
 - `states` is the list of state abbreviations that identify the layers to use from the FWS data
 - `wetlandsFolder` is the source folder containing the downloaded wetlands datasets by state

3. Execute the script in Arc Python


## Manual Editing

Unfortunately, some categorization errors are present in the raw wetland layers. 
After the script is run a handful of errors need to be corrected. These errors 
exist in the form of small polygons located far enough inland to be positively 
identified as not tidally influenced.