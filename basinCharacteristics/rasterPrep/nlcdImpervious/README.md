Impervious Surface
==================

This script produces a raster representing the percentage of the area, based on 
the National Land Cover Dataset, that is covered by impervious surface. Raster 
values range from 1 to 100.


## Data Sources
| Layer           | Source                                              |
|:-----:          | ------                                              |
| Land Use Raster | [National Land Cover Dataset](http://www.mrlc.gov/) |
| Catchments      | Conte Ecology Group  - NHDHRDV2                     |

## Steps to Run:

The folder structure is set up within the scripts. In general, the existing 
structure in the repo should be followed. Raw data should be unzipped, but 
otherwise kept in the same format as it is downloaded.

1. Open the script `nlcdImpervious.py`

2. Change the values in the "Specify inputs" section of the script
 - `baseDirectory` is the path to the folder where results are written
 - `catchmentsFilePath` is the file path to the catchments polygons shapefile. 
 (See "Notes" section)
 - `rasterFilePath` is the file path to the raw NLCD Impervious raster (`.img` 
 format)
 - `outputName` is the name that will be associated with this particular run of 
 the tool (e.g. `NHDHRDV2` for all High Resolution Catchments)

3. Run the script in ArcPython. It does the following:
 - Sets up the folder structure in the specified directory
 - Generates the processing boundary from the specified shapefile
 - Trims the raw raster to the spatial boundary and removes the missing data
 - Saves the completed rasters to the 
 `[baseDirectory]\gisFiles\[outputName]\outputFiles` directory

## Output Rasters 

#### Impervious
*Raster name:* impervious <br>
*Description:* This layer represents the percentage of the area that is covered 
by impervious surface.


## Notes

- Typically, the `catchmentsFilePath` variable specifies a shapefile of 
hydrologic catchments defining the range over which the "Zonal Statistics" tool 
will be applied. It is possible to enter another polygon shapefile, such as 
state or town boundaries, as this variable. The primary purpose of this file is 
to trim the original raster, which represents the continental US, to a manageable 
size.
