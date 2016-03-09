Tidally Influenced Areas
========================

The tidally influenced zones are created from the [U.S. Fish & Wildlife National 
Wetlands Inventory](http://www.fws.gov/wetlands/Data/Data-Download.html) polygon 
layers. The ArcPy script indexes all of the polygons that have any form of tidal 
influence as defined by the [NWI Wetlands and Deepwater Map Code Diagram](http://www.fws.gov/wetlands/Documents/NWI_Wetlands_and_Deepwater_Map_Code_Diagram.pdf).

The polygons are joined together and output in a single shapefile representing 
all bodies of water within the SHEDS range that are impacted by tide. This layer 
is used to identify sites that are potentially influenced by tides.


# Shapefile Creation

1. Open the script `createTidalShapefile.py`

2. Change the values in the "Specify inputs" section of the script
 - `baseDirectory` is the path to the folder to output spatial data
 - `states` is the list of state abbreviations that identify the layers to use from the FWS data
 - `wetlandsFolder` is the source folder containing the downloaded wetlands datasets by state

3. Execute the script in Arc Python

4. Unfortunately, some categorization errors are present in the raw wetland layers. 
After the script is run a handful of errors need to be corrected. These errors 
exist in the form of small polygons located far enough inland to be positively 
identified as not tidally influenced.


# Database Upload
The tidal zone shapefile created in the previous sction is uploaded to the 
SHEDS database. 

1. Save the tidal zone shapefile as `tidal_zones.shp` into a dedicated folder 
on the server.

2. Set parameters for the bash script `import_tidal_zones.sh`. 
 - Parameter 1: The name of the database
 - Parameter 2: The path to the directory containing the tidal zone shapefile 
 
3. Execute the bash script:
  `./import_tidal_zones.sh sheds_new /home/kyle/data/gis/tidal_zones`

4. The layer is uploaded as `gis.tidal_zones` to the specified database.


# QAQC 
The layer uploaded to the database is used to identify sites that are 
potentially tidally influenced.

1. Set parameters for the bash script `id_tidal_sites.sh`. 
 - Parameter 1: The name of the database
 - Parameter 2: The path to the directory to output a CSV

2. Execute the bash script:
  `./id_tidal_sites.sh sheds_new /home/kyle/qaqc`

3. A CSV is saved to the output directory that identifies the sites which 
intersect the tidal layer. The file has one column with the header "id".

