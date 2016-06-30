Tidally Influenced Areas
========================

The tidally influenced zones are created from the [U.S. Fish & Wildlife National 
Wetlands Inventory](http://www.fws.gov/wetlands/Data/Data-Download.html) polygon 
layers. All of the polygons that have any form of tidal influence as defined by 
the [NWI Wetlands and Deepwater Map Code Diagram](http://www.fws.gov/wetlands/Documents/NWI_Wetlands_and_Deepwater_Map_Code_Diagram.pdf) are indexed. The polygons are joined 
together and output in a single shapefile representing all bodies of water 
within the SHEDS range that are impacted by tide. This layer is used to identify 
sites that are potentially influenced by tides.


# Shapefile Creation

1. Open the ArcPy script `createTidalShapefile.py`

2. Change the values in the "Specify inputs" section of the script
 - `baseDirectory` is the path to the folder to output spatial data
 - `states` is the list of state abbreviations that identify the layers to use from the FWS data
 - `wetlandsFolder` is the source folder containing the downloaded wetlands datasets by state
 - `grid` is a grid layer used to divide the final product into manageable sized polygons. This 
 currently refers to a pre-existing climate grid of 25km x 25km grid cells.

3. Execute the script in Arc Python

4. Categorization errors exist within the raw wetland layers. After the script 
is run a handful of these errors need to be corrected. Small polygons located 
far enough inland to be positively identified as not tidally influenced are 
manually deleted and the corrected layer is saved.


# Database Upload
The tidal zone shapefile created in the previous section is uploaded to the 
SHEDS database. 

1. Save the tidal zone shapefile as `tidal_zones.shp` into a dedicated folder 
on the server.

2. Set parameters for the bash script `import_tidal_zones.sh`. 
 - Parameter 1: The name of the database
 - Parameter 2: The path to the directory containing the tidal zone shapefile 
 
3. Execute the bash script in the command line:
 - `./import_tidal_zones.sh sheds_new /home/kyle/data/gis/tidal_zones`

4. The layer is uploaded to the specified database as the `gis.tidal_zones` 
table.


# QAQC 
The uploaded layer is used to identify sites in the database from the 
`public.locations` table that are potentially tidally influenced.

1. Set parameters for the bash script `id_tidal_sites.sh`. 
 - Parameter 1: The name of the database
 - Parameter 2: The path to the directory to output a CSV

2. Execute the bash script in the command line:
  `./id_tidal_sites.sh sheds_new /home/kyle/qaqc`

3. A CSV identifying the sites which intersect the tidal layer is saved to the 
output directory. The file has one column with the header "id".

