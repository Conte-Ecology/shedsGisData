NADP Atmospheric Deposition
===========================

This script produces continuous rasters representing the atmospheric deposition of 
various compounds (NO3 & SO4). The raster values are the total annual wet atmospheric
deposition in kg/ha.


## Data Sources
|    Layer           | Source                                                                                             | 
|   :-----:          | ------                                                                                             | 
| Deposition Rasters | [National Atmospheric Deposition Program](http://nadp.sws.uiuc.edu/ntn/annualmapsByYear.aspx#2011) |
| Catchments         | Conte Ecology Group  - NHDHRDV2                                                                    |

## Steps to Run

The folder structure is set up within the scripts. In general, the existing structure 
in the repo should be followed. Raw data should be unzipped, but otherwise kept in the
same format as it is downloaded.

1. Open the script `atmosphericDeposition.py`

2. Change the values in the "Specify inputs" section of the script
 - `baseDirectory` is the path to the folder where results are written
 - `catchmentsFilePath` is the file path to the catchments polygons shapefile. 
 (See "Notes" section")
 - `sourceFolder` is the path to the folder containing the deposition rasters in .tif 
 format
 - `outputName` is the name that will be associated with this particular run of the 
 tool (e.g. "NHDHRDV2")

3. Run the script in ArcPython. It does the following:
 - Sets up the folder structure in the specified directory
 - Generates the processing boundary from the specified shapefile and clips the source 
 raster to this range
 - Trims the raw raster to the spatial boundary
 - Outputs the raster to the 
 `[baseDirectory]\gisFiles\[outputName]\outputFiles` directory


## Output Rasters

#### Nitrate Ion (NO3) Deposition
*Raster name:* dep_no3_2011 <br>
*Description:* This layer represents the total annual wet deposition of nitrate (NO3) in 2011.

#### Sulfate Ion (SO4) Deposition
*Raster name:* dep_so4_2011 <br>
*Description:* This layer represents the total annual wet deposition of sulfate (SO4) in 2011.



## Notes

- Typically, the `catchmentsFilePath` variable specifies a shapefile of hydrologic catchments 
defining the range over which the "Zonal Statistics" tool will be applied. It is possible to 
enter another polygon shapefile, such as state or town boundaries, as this variable. The 
primary purpose of this file is to clip the original raster from the the continental US 
extent, to a manageable size.

## Next Steps
- Additional deposition layers are available and can be added with relative ease