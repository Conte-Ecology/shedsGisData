Impoundments: Downstream Impacted Area
======================================

This script produces a polyline layer representing river segments of a specified 
length immediately downstream of impoundments. 


## Data Sources
| Layer                         | Source                               |
|:-----:                        | ------                               |
| dams shapefile                | UMass Land Ecology Lab - DSL Project |
| NHD High Resolution Flowlines | Conte Ecology Group - NHDHRDV2       |


## Steps to Run:

The folder structure is set up within the scripts. In general, the existing 
structure in the repo should be followed.

1. Open the script `createImpactedZones.py`

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
This section maps the impoundments within the specified snap distance to the 
flowlines and creates a layer of the stream segments with dams present for 
processing. Only the dams where the column "Use" = 1 are used as instructed 
in the source documentation.

### Linear Referencing
This section creates the routes layer and determines the position of each 
impoundment along the stream segments.

The `FMEAS` column indicates the location along the segment, in meters, where 
the impoundment falls. The `FMEAS` column is used to create the line 
representing the impacted downstream zone from the impoundment.

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
confluences. This is the simpler of the processing methods.

In this section, `zoneM` is calulated as the impoundment's position along the 
line plus the sepecfied zone distance (`zoneDistanceM`).

### Confluence Points
This section handles locations that have 1 or more confluences in the impacted 
downstream zone (`zoneDistanceM`).

The script iterates through confluences until the specified zone distance is 
met. A new field named `totalZoneM` is added to track the length of the zone as 
it is mapped through confluences from segment to segment. The `zoneM` field 
ends up being incremental and either equals the total length of the segment or 
the length that will get the total zone length (`totalZoneM`) to the specified 
zone distance. The `FMEAS` column is calculated as 0 for any segments directly 
downstream of a confluence. 

At the end of the section all of the non-confluence and confluence zones are 
merged into a single layer with the aforementioned 1 meter correction sections 
bing removed.

### Join Connected Areas
After merging the segments some connected reaches may still exist as separate 
features. This section converts the connected zones into single features by 
utilizing small buffers around each line segment. Overlapping buffers signify 
common groups by which the lines are joined.

### Impacted Catchment Pour Points 
Catchments with pour points within an impounded zone are noted in a separate 
list. These catchments are identified if the catchment boundary is crossed by 
an impoundment impacted zone and the catchment contains a dam. The possibility 
of false positives exist in the cases where the upstream end of the stream is 
the point of crossing and a dam (with downstream zone) exist within the 
catchment without crossing the boundary. 


## Output Layers

#### Impacted Zones
Layer name: impoundedZones[`zoneDistanceM`]m.shp <br>
Description: This layer represents the sections along the flowlines that are 
within the specified distance downstream of an impoundment.

#### Pour Points
Raster name: impactedPourPoints[`zoneDistanceM`]m.dbf <br>
Description: This table identifies the catchments with pour points falling 
within the specified distance downstream of an impoundment.


## Next Steps
- Upgrade the catchment pour point selection method.
