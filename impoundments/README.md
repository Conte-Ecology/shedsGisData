Impoundments: Downstream Impacted Area
======================================

This script produces a spatial polyline layer representing stream sections 
immediately downstream of an impoundment. The length of the section is specified 
in the script.


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




# QAQC Process
The tidal influence layer is used in Postgres to identify sites with potential 
tidal influence. The QAQC bash script uses the lat/lon coordinates of the 
locations to perform a spatial intersection with the tidal layer. A CSV file 
identifying the location id of the tidally influenced sites is generated. The 
option exists to specify the locations to evaluate.

## Run script

1. Prepare script arguments

| Parameter |              Description              |                Example                 | 
|:---------:|              -----------              |                -------                 |
|     1     | The current working database          | sheds_new                              |
|     2     | The output directory                  | /home/kyle/qaqc                        |
|     3     | The CSV file specifying location id's | /home/kyle/qaqc/eg_check_locations.csv |

The format of the CSV that specifies the location id's to check is a single 
column with the header 'id'. The column data type should be integer. If this 
changes in the system, the QAQC script will need to be updated. 


2. Execute the scrpt in the bash (include full path)

Evaluate all locations:
`/home/kyle/scripts/qaqc/id_impoundment_sites.sh sheds_new /home/kyle/qaqc`

Evaluate specified locations:
`/home/kyle/scripts/qaqc/id_impoundment_sites.sh sheds_new /home/kyle/qaqc /home/kyle/qaqc/eg_check_locations.csv`



# Next Steps
- Upgrade the catchment pour point selection method.
