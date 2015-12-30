Soil Drainage Class
===================

This script produces a spatial dataset of the soil drainage class of the soil 
based on the Soil Survey Geographic Database (SSURGO). The qualitiative 
classification are reclassified to numeric values (ranging from 1 to 7) for 
spatial averaging. 


## Data Sources
| Layer   | Source | 
|:-----:  | ------ | 
| SSURGO  | [USDA-NRCS](http://datagateway.nrcs.usda.gov/GDGOrder.aspx?order=QuickState) Select: "2014 Gridded Soil Survey Geographic (gSSURGO) by State or Conterminous U.S."|


## Steps to Run:

The folder structure is set up within the scripts. In general, the existing 
structure in the repo should be followed. Raw data should be kept in the same 
format as it is downloaded.

1. Open the script `soilDrainageClass.py`

2. Change the values in the "Specify inputs" section of the script
 - `baseDirectory` is the path to the `\soilDrainageClass` folder 
 (current parent working directory)
 - `states` is the list of state abbreviations included in the desired range
 - `sourceFolder` is the directory containing the unzipped SSURGO datasets by 
 state 
 - `outputName` is the name that will be associated with this particular run of 
 the tool (e.g. `NHDHRDV2` for all High Resolution Catchments)

3. Run the script in ArcPython. It does the following:
 - Sets up the folder structure in the specified directory
 - Merges the necessary data tables in order to connect spatial data to 
 necessary soil classification
 - Loops through the state polygons, creating state rasters of the drainage 
 class
 - Converts the drainage class categories to numeric values according to the 
 table in the next section
 - Mosaicks all of the state rasters to output a single raster
 - Saves the completed rasters to the 
 `[baseDirectory]\gisFiles\[outputName]\outputFiles` directory
 
 
## Reclassification Values
|        Drainage Class       | Assigned Value |
|:---------------------------:|:--------------:|
| Excessively drained         |      1         |
| Somewhat excessively drained|      2         |
| Well drained                |      3         |
| Moderately well drained     |      4         |
| Somewhat poorly drained     |      5         |
| Poorly drained              |      6         |
| Very poorly drained         |      7         |


## Output Rasters

#### Soil Drainage Class
*Raster name:* drainageclass <br>
*Description:* This layer is a numeric representation of the soil drainage class. 
This category is defined in the Drainage Class ("drainagecl") column of 
SSURGO's Component table ("component").


## Notes

- The spatial range is determined by the list of states specified.