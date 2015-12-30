PRISM Climate Data
==================

This script produces rasters of climate variables based on the PRISM Climate 
Dataset. Temperature rasters are in degrees C and precipitation rasters are 
in mm.


## Data Sources
| Layer                                                       | Source |
|:-----:                                                      | ------ |
| PRISM 30-Year Normal (1981 - 2010) of monthly precipition   | [PRISM Climate Group](http://www.prism.oregonstate.edu/normals/) |
| PRISM 30-Year Normal (1981 - 2010) of min & max temperature | [PRISM Climate Group](http://www.prism.oregonstate.edu/normals/) |
| Catchments                                                  | Conte Ecology Group - NHDHRDV2 |


## Steps to Run:

The folder structure is set up within the scripts. In general, the existing 
structure in the repo should be followed. Raw data should be unzipped, but 
otherwise kept in the same format as it is downloaded.

1. Open the script `prism.py`

2. Change the values in the "Specify inputs" section of the script
 - `baseDirectory` is the path to the `prism` folder
 - `catchmentsFilePath` is the file path to the catchments polygons shapefile 
 (See "Notes" section)
 - `sourceFolder` is the source folder of the PRISM datasets by state
 - `outputName` is the name that will be associated with this particular run of 
 the tool (e.g. `NHDHRDV2` for all High Resolution Catchments)

3. Run the script in ArcPython. It does the following:
 - Sets up the folder structure in the specified directory
 - Generates the processing boundary from the specified shapefile and clips 
 the source raster to this range
 - Trims the raw raster to the spatial boundary 
 - Saves the completed rasters to the 
 `[baseDirectory]\gisFiles\[outputName]\outputFiles` directory
   
## Output Rasters

#### Average Minimum Annual Temperature
*Raster name:* ann_tmin_c <br>
*Description:* This layer represents the 30-year normal (1981-2010) of average 
minimum annual temperature.

#### Average Maximum Annual Temperature
*Raster name:* ann_tmax_c <br>
*Description:* This layer represents the 30-year normal (1981-2010) of average 
maximum annual temperature.

#### Average Monthly Precipition (12 rasters)
Raster names: e.g. jan_prcp_mm, feb_prcp_mm, mar_prcp_mm, apr_prcp_mm, 
may_prcp_mm, jun_prcp_mm, jul_prcp_mm, aug_prcp_mm, sep_prcp_mm, oct_prcp_mm, 
nov_prcp_mm, dec_prcp_mm <br>
Description: These layers represents the 30-year normal (1981-2010) of average 
monthly precipitaion.


## Notes

- Typically, the `catchmentsFilePath` variable specifies a shapefile of hydrologic 
catchments defining the range over which the "Zonal Statistics" tool will be 
applied. It is possible to enter another polygon shapefile, such as state or town 
boundaries, as this variable. The primary purpose of this layer is to trim the 
original raster, which represents the continental US, to a manageable size.


## Next Steps

- Additional climate variables, available from the PRISM website, can be processed 
in the same manner by adding them to the `sourceFolder`.