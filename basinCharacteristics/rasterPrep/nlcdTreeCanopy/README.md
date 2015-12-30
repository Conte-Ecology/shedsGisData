Tree Canopy
===========

This script produces a raster representing the percentage of the ground covered 
by a vertical projection of tree canopies, based on the National Land Cover 
Dataset. Raster values range from 1 to 100.


## Data Sources
| Layer              | Source                                                                                                              |
|:-----:             | ------                                                                                                              |
| Tree Canopy Raster | [National Land Cover Dataset](http://www.mrlc.gov/)                                                                 |
| Catchments         | Conte Ecology Group   - NHDHRDV2                                                                                    |
| State Boundaries   | [National Atlas of the United States](http://dds.cr.usgs.gov/pub/data/nationalatlas/statesp010g.shp_nt00938.tar.gz) |


## Steps to Run:

The folder structure is set up within the scripts. In general, the existing 
structure in the repo should be followed. Raw data should be unzipped, but 
otherwise kept in the same format as it is downloaded.

1. Open the script `nlcdTreeCanopy.py`

2. Change the values in the "Specify inputs" section of the script
 - `baseDirectory` is the path to the `\nlcdTreeCanopy` folder
 - `catchmentsFilePath` is the file path to the catchments polygons shapefile 
 (See "Notes" section)
 - `rasterFilePath` is the file path to the raw NLCD Land Use raster (`.img` 
 format)
 - `outputName` is the name that will be associated with this particular run of 
 the tool (e.g. `NHDHRDV2` for all High Resolution Catchments)
 - `statesFilePath` is the filepath to the state boundary shapefile
 
3. Run the script in ArcPython. It does the following:
 - Sets up the folder structure in the specified directory
 - Generates the processing boundary from the specified shapefile. 
 Specifically, the states overlapping the range file (`catchmentsFilePath`)
 are used to create the boundary (see "Notes")
 - Trims the raw raster to the spatial boundary and removes the missing data
 - Saves the completed rasters to the 
 `[baseDirectory]\gisFiles\[outputName]\outputFiles` directory


## Output Rasters 

#### Tree Canopy
*Raster name:* tree_canopy <br>
*Description:* This layer represents the percentage of the raster cell area that 
is covered by a vertical projection of tree canopy.


## Notes

- Typically, the `catchmentsFilePath` variable specifies a shapefile of hydrologic 
catchments defining the range over which the "Zonal Statistics" tool will be 
applied. It is possible to enter another polygon shapefile, such as state or town 
boundaries, as this variable. The primary purpose of this layer is to trim the 
original raster, which represents the continental US, to a manageable size.

- The Tree Canopy raster uses values of zero in areas outside of the U.S. Using 
zero values in place of NA will provide incorrect stats (i.e. read as having no 
canopy coverage). As a result, the States shapefile is used to trim the raster 
to where it has usable data for running the "Zonal Statistics" tool. This layer 
is not currently applicable to zones outside of the U.S.
