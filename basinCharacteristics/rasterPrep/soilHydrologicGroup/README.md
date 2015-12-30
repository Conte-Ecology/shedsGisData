Hydrologic Soil Group
=====================

This script produces categorical rasters of hydrologic soil group classifications 
based on the Soil Survey Geographic Database (SSURGO). A raster value of 1 
represents the presence the specified hydrologic group and a 0 represents the 
absence. Hydrologic soil groups are based on the minimum rate at which water 
infiltrates a soil layer, where A allows for the most infiltraiton and D the 
least. Some soils may be classified in group D because of a high water table 
creating poor drainage.


## Data Sources
| Layer  | Source | 
|:----:  | ------ | 
| SSURGO | [USDA-NRCS](http://datagateway.nrcs.usda.gov/GDGOrder.aspx?order=QuickState) Select: "2014 Gridded Soil Survey Geographic (gSSURGO) by State or Conterminous U.S." |

## Steps to Run:

The folder structure is set up within the scripts. In general, the existing 
structure in the repo should be followed. Raw data should be kept in the same 
format as it is downloaded.

1. Open the script `soilsHydrologicGroup.py`

2. Change the values in the "Specify inputs" section of the script
 - `baseDirectory` is the path to the `soilsHydrologicGroup` folder (current 
 parent working directory)
 - `states` is the list of state abbreviations included in the desired range
 - `sourceFolder` is the directory containing the unzipped SSURGO datasets by 
 state 
 - `outputName` is the name that will be associated with this particular run of 
 the tool (e.g. `NHDHRDV2` for all High Resolution Catchments)
 - `hydroGroups` is a list of lists describing the classifications to process. 
 The first element in each sublist is the SQL where clause defining which 
 hydrologic groups to select. The second element in the sublist is the name to 
 assign to that selection.
 
4. Run the script in ArcPython. It does the following:
 - Sets up the folder structure in the specified directory
 - Creates an empty raster of the entire specified range
 - Merges the necessary data tables in order to connect spatial data to 
 specified soil classification
 - Loops through the state polygons, creating state rasters of the surficial 
 coarseness category
 - Mosaicks all of the state raster and the full range empty raster
 - Saves the completed rasters to the 
 `[baseDirectory]\gisFiles\[outputName]\outputFiles` directory


## Output Rasters

#### Soil Hydrologic Group A
*Raster name:* hydrogroup_a <br>
*Description:* The layer represents the soil hydrolic group A. This category is 
defined by features where Hydrologic Group ("hydgrp") = "A" in SSURGO's 
Component ("component") table.

#### Soil Hydrologic Group A & B
*Raster name:* hydrogroup_ab <br>
*Description:* The layer represents the soil hydrolic groups A & B. This category 
is defined by features where Hydrologic Group ("hydgrp") = "A" or "B" in SSURGO's 
Component ("component") table.

#### Soil Hydrologic Group C & D
*Raster name:* hydrogroup_cd <br>
*Description:* The layer represents the soil hydrolic groups C & D. This category 
is defined by features where Hydrologic Group ("hydgrp") = "C" or "D" in SSURGO's 
Component ("component") table.

#### Soil Hydrologic Group D (Only)
*Raster name:* hydrogroup_d1 <br>
*Description:* The layer represents the soil hydrolic group D and only D. This 
category is defined by features where Hydrologic Group ("hydgrp") = "D" in 
SSURGO's Component ("component") table.

#### Soil Hydrologic Group D (All)
*Raster name:* hydrogroup_d4 <br>
*Description:* The layer represents the soil hydrolic group D where any 
combination including group D is included. This category is defined by features 
where Hydrologic Group ("hydgrp") = "A/D", "B/D", "C/D", or "D" in SSURGO's 
Component ("component") table.


## Notes

- The spatial range is determined by the list of states specified.
- Different rasters may be created by editing the `hydroGroups` object in the 
script
