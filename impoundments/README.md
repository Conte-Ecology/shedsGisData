Impoundments: Downstream Impacted Area
======================================

This script produces the spatial datasets of "Open Water" and "Wetland" land 
coverage, based on the USFWS National Wetlands Inventory. In each raster, a 
value of 1 represents the presence the specified land cover classification and 
a 0 represents the absence.


## Data Sources
| Layer            | Source                                           | Link |
|:-----:           | ------                                           | ---- |
| Wetlands Layer   | U.S. Fish & Wildlife National Wetlands Inventory | 
http://www.fws.gov/wetlands/Data/Data-Download.html                          |
| State Boundaries | National Atlas of the United States              | 
http://dds.cr.usgs.gov/pub/data/nationalatlas/statesp010g.shp_nt00938.tar.gz |

## Steps to Run:

The folder structure is set up within the scripts. In general, the existing 
structure in the repo should be followed. Raw data should be kept in the same 
format as it is downloaded (unzip the state boundaries layer)

1. Open the script `fwsWetlands.py`

2. Change the values in the "Specify Inputs" section of the script
 - `baseDirectory` is the path to the `\fwsWetlands` folder on GitHub
 - `hydroRegions` is a list of the hydrologic regions to process
 - `zoneDistanceM` is the distance downstream, in meters, of each dam to cover
 - `snapDisancetM` is the maximum snapping distance, in meters, from the raw 
 impoundments layer to the flowlines
 - `sourceImpoundments` is the file path to the impoundments layer
 
3. Run the script in ArcPython. It creates the following:



## Process Description:
The processing of this layer can be difficult to follow. A description is 
included here to assist with replication and re-use of the script. The different 
sections of the script are outlined separately.



### Network Pre-processing

This section Maps the impoundments within the specified snap distance to the flowlines and 
creates a layer of the stream segments with dams present for processing.



### Linear Referencing

This section creates the routes layer and determines the position of each impoundment along 
the stream segments.

The `FMEAS` column indicates the location along the segment, in meters, where 
the impoundment falls. The `FMEAS` column is used to create the line representing 
the impacted downstream zone from the impoundment.

A `zoneM` field is added for specifying the end point of the route event 
calculation. The calulation varies for confluence and non-confluence zones 
described below.

When an impoundment falls on a confluence, the marked location may slightly exceed 
the length of the line. This situation is corrected by setting `FMEAS` to be 1 
meter less than the end of the line. These false sections are created so the 
processing will continue downstream from the confluence without stopping due to 
blank features. This effectively includes the case with the "Conlfuence Points" 
described below. These sections are removed later.


### Non-confluence Points

This section handles the impacted downstream zones that do not contain any 
confluences.

In this section, `zoneM` is just calulated as the impoundment's position along 
the line plus the sepecfied zone distance (`zoneDistanceM`).


### Confluence Points

This section handles locations that have 1 or more confluences in the impacted 
downstream zone.

The script iterates through confluences until the specified zone distance is 
met. A new field named `totalZoneM` is added to track the length of the zone as 
it is mapped through confluences from segment to segment. The `zoneM` field 
ends up being incremental and either equals the total length of the segment or 
the length that will get the total zone length (`totalZoneM`) to the specified 
zone distance. The `FMEAS` column is calculated as 0 for any segments 
downstream of a confluence. 




 
 
 
 
 
 
 
 
 
 
   - Sets up the folder structure in the specified directory
   - Ensures constistency of projections
   - Creates an empty raster of the entire specified range based on the State 
   Boundaries shapefile
   - Loops through the state polygons, creating state rasters of the categories 
   described below
   - Mosaicks all of the state raster and the full range empty raster
   - Saves completed rasters to the `fwsWetlands\gisFiles\[outputName]\outputFiles` 
   directory

















## Output Rasters

#### Open Water 
Raster name: fwsOpenWater <br>
Description: This layer represents the FWS wetlands defined as "open water" (where 
"WETLAND_TYPE" = "Freshwater Pond", "Lake", or "Estuarine and Marine Deepwater").

#### Wetlands
Raster name: fwsWetlands <br>
Description: This layer represents the FWS wetlands defined as "open water" (where 
"WETLAND_TYPE" = "Estuarine and Marine Wetland", "Freshwater Emergent Wetland", or 
"Freshwater Forested/Shrub Wetland").

## Notes

- The states listed in the "Specify inputs" section of the script will determine 
the spatial range of the output

- The layers for Maryland (MD) and the District of Columbia (DC) overlap in the 
FWS data, but not in the state boundary layer. DC is not included in "states" 
(only MD is used). In the state boundaries layer, "District of Columbia" must 
be specified if including Maryland.

## Next Steps
- Classification definitions can be changed with relatively minimal effort. 
