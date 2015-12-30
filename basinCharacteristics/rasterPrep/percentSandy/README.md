Percent Sandy
=============

This script produces a categorical raster of geology that is categorized as 
"sandy" by the Soil Survey Geographic Database (SSURGO). A raster value of 
1 represents the presence the "sandy" classification and a 0 represents the 
absence.


## Data Sources
| Layer   | Source | 
|:-----:  | ------ |
| SSURGO  | [USDA-NRCS](http://datagateway.nrcs.usda.gov/GDGOrder.aspx?order=QuickState) Select: "2014 Gridded Soil Survey Geographic (gSSURGO) by State or Conterminous U.S." |

## Steps to Run:

The folder structure is set up within the scripts. In general, the existing 
structure in the repo should be followed. Raw data should be unzipped, but 
otherwise kept in the same format as it is downloaded.

1. Open the script `percentSandy.py`

2. Change the values in the "Specify inputs" section of the script
 - `baseDirectory` is the path to the `\percentSandy` folder (current parent 
 working directory)
 - `states` is the list of state abbreviations included in the desired range
 - `sourceFolder` is the directory containing the unzipped SSURGO datasets by 
 state
 - `outputName` is the name that will be associated with this particular run 
 of the tool (e.g. `NHDHRDV2` for all High Resolution Catchments)

3. Run the script in ArcPython. It does the following:
 - Sets up the folder structure in the specified directory
 - Creates an empty raster of the entire specified range
 - Merges the necessary data tables in order to connect spatial data to 
 necessary soil classification
 - Loops through the state polygons, creating state rasters of the sandy category
 - Mosaicks all of the state raster and the full range empty raster
 - Saves the completed rasters to the 
 `[baseDirectory]\gisFiles\[outputName]\outputFiles` directory

## Output Rasters

#### Percent Sandy
*Raster name:* sandy <br>
*Description:* This layer represents the soil parent material that is described as 
"sandy". This classification is defined as a soil whose parent material texture 
is sandy and is defined in SSURGO's "Component Parent Material" table ("copm") 
by features in the column "Textural Modifier" ("pmmodifier") = "Sandy". 


## Notes

- The spatial range is determined by the list of states specified.
