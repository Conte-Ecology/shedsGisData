Impoundments: Downstream Impacted Zone
======================================

The impoundment influence zones layer is created using a network analysis 
methodology that maps a user-specified length downstream from an impoundment. 
The impoundments layer comes from the DSL Project version of The Nature 
Conservancy's dam inventory with locations snapped to the NHD high resolution 
flowlines. The impoundment influence zones are uploaded to the SHEDS database 
and used to identify sites that are potentially influenced by upstream 
impoundments. 



# Data Sources
|  Layer                        | Source                               |
| :-----:                       | ------                               |
| Dams Shapefile                | UMass Land Ecology Lab - DSL Project |
| NHD High Resolution Flowlines | Conte Ecology Group - NHDHRDV2       |



# Shapefile Creation


## Steps to Run:

The folder structure is set up within the scripts. In general, the existing 
structure in the repo should be followed.

1. Open the script `createImpactedZones.py`

2. Change the values in the "Specify Inputs" section of the script
 - `baseDirectory` is the path to the folder where results are written
 - `hydroRegions` is a list of the hydrologic regions to process
 - `zoneDistanceM` is the distance downstream, in meters, of each dam to cover
 - `snapDisancetM` is the maximum snapping distance, in meters, from the raw 
 impoundments layer to the flowlines
 - `sourceImpoundments` is the file path to the impoundments layer
 
3. Run the script in ArcPython


## Process Description:
The processing of this layer may be difficult to follow. This description  
is intended to assist with replication and re-use of the script. The different 
sections of the script are outlined separately.

### Network Pre-processing
This section maps the impoundments within the specified snap distance to the 
flowlines and creates a layer of the stream segments with dams present for 
processing. Only the dams where the column "Use" = 1 are processed. These dams 
have been confirmed to be on the high resolution flowlines. 

### Linear Referencing
This section creates the routes layer and determines the position of each 
impoundment along the stream segments.

The `FMEAS` column indicates the location along the segment, in meters, where 
the impoundment falls. The `FMEAS` column is used to create the line 
representing the impacted downstream zone from the impoundment.

A `zoneM` field is added for specifying the location along the segment, in 
meters, of the end point of the route event calculation. The calculation 
method varies for confluence and non-confluence zones described below.

When an impoundment falls on a confluence the marked location may slightly exceed 
the length of the line, resulting in a blank feature when generating the impacted 
zone. This situation is corrected by setting `FMEAS` to be 1 meter less than the 
length of the line, creating a small false section. These false sections are 
created so the processing will continue downstream from the confluence without 
stopping due to blank features. This effectively includes the case with the 
"Conlfuence Points" described below. These sections are removed later.

### Non-confluence Points
This section handles the impacted downstream zones that do not contain any 
confluences. This is the simpler of the processing methods.

In this section, `zoneM` is calulated as the impoundment's position along the 
line plus the specified zone distance (`zoneDistanceM`).

### Confluence Points
This section handles locations that have 1 or more confluences in the impacted 
downstream zone (`zoneDistanceM`).

The script iterates through confluences until the specified zone distance is 
met. A new field named `totalZoneM` is added to track the length of the zone as 
it is mapped iteratively through confluences from segment to segment. The `zoneM` 
field ends up being incremental and either equals the total length of the segment 
or the length that will push the total zone length (`totalZoneM`) to the 
specified zone distance. The `FMEAS` column is calculated as 0 for any segments 
directly downstream of a confluence. 

At the end of the section all of the non-confluence and confluence zones are 
merged into a single layer with the aforementioned 1 meter correction sections 
bing removed.

### Join Connected Areas
After merging the segments some connected reaches may still exist as separate 
features. This section converts the connected zones into single features by 
utilizing small buffers around each line segment. Overlapping buffers signify 
common groups by which the lines are joined into single features.

### Impacted Catchment Pour Points 
A separte list of catchments with pour points falling within an impounded zone 
is generated. These catchments are identified when the catchment boundary is 
crossed by an impoundment impacted zone and the catchment contains a dam. The 
possibility of false positives exist in the cases where the inlet of the 
stream segment into the catchmet is the point of crossing and a dam (with 
downstream zone) exist within the catchment without crossing the boundary at 
the pour point. 


## Output Layers

#### Impacted Zones
Layer name: impoundedZones[`zoneDistanceM`]m.shp <br>
Description: This polyline layer represents the sections along the flowlines 
that are within the specified distance downstream of an impoundment.

#### Pour Points
Table name: impactedPourPoints[`zoneDistanceM`]m.dbf <br>
Description: This table identifies the catchments with pour points falling 
within the specified distance downstream of an impoundment.



# Database Upload
The impoundment zone shapefile created in the previous section is uploaded to 
the SHEDS database. The upload script is specific to the zone shapefile with 
the reference to the spatial object being hard-coded, meaning a new script will 
need to be derived for each new zone length (a simple task). For example, the 
`import_impoundment_zones_100m.sh` script directly references the 
`impoundedZones100m.shp` layer. The steps below follow the example of the 100 
meter zone. 

1. Save the impoundment zone shapefile into a dedicated folder on the server 
with the name identifying the zone length (e.g. `impoundedZones100m.shp`). The 
upload script will specifically reference this name. The existing layer is 
currently saved to the `/home/kyle/data/gis/impoundment_zones` directory on 
felek. 

2. Set parameters for the bash script `import_impoundment_zones_100m.sh`. 
 - Parameter 1: The name of the database
 - Parameter 2: The path to the directory containing the impoundment zone 
 shapefile 
A duplicate of the script in this repo is saved in the `/home/kyle/scripts/qaqc` 
directory on felek.
 
3. Execute the bash script in the command line:
 - `./import_impoundment_zones_100m.sh sheds_new /home/kyle/data/gis/impoundment_zones`

4. The layer is uploaded to the specified database as the `gis.impoundment_zones_100m` 
table.



# QAQC Process

The uploaded layer is used to identify sites in the database from the 
`public.locations` table that are potentially influenced by impoundments. An 
optional CSV indicating the locations to check may be used with the script. The 
format of this CSV is an integer column with the header 'id'.

1. Set parameters for the bash script `id_impoundment_sites.sh`. 
 - Parameter 1: The name of the database
 - Parameter 2: The path to the output directory
 - Parameter 3: The path to the optional input CSV

2. Execute the bash script in the command line:

 - Evaluate all locations: `./id_impoundment_sites.sh sheds_new /home/kyle/qaqc`

 - Evaluate specified locations: `./id_impoundment_sites.sh sheds_new /home/kyle/qaqc /home/kyle/qaqc/eg_check_locations.csv`
 
3. A CSV identifying the sites within the downstream zone of an impoundment is 
saved to the output directory. The file has one column with the header "id". 
Currently, the identification method uses a 10 meter buffer around the site 
locations to determine if they intersect with an impoundment zone. This is 
because the points are not snapped to the flowlines. 



# Next Steps
- Upgrade the catchment pour point selection method.
