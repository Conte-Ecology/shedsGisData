Basin Characteristics
=====================

# Description

This repo calculates statistics of spatial data within hydrologic catchment 
delineations in support of the models and web applications created by the Conte 
Ecology Group. A combination of ArcPy and R scripts are used to process spatial 
data and assign spatially averaged statistics to catchment polygons. Within each 
delineation, a unique catchment identifier is assigned values for basin 
characteristics such as land cover or geology variables. A full list of variables 
can be found in the [Covariate Data Status spreadsheet](https://github.com/Conte-Ecology/shedsData/blob/master/basinCharacteristics/Covariate%20Data%20Status%20-%20High%20Res%20Delineation.xlsx).


# Software Requirements

ArcGIS 10.2 with Spatial Analyst Toolbox  
R version 3.1.2  
Current R libraries:  
  - `reshape2`
  - `foreign`
  - `tcltk`
  - `dplyr`
  - `lazyeval`
  

# Repository Structure

The `\rasterPrep` subfolder contains the scripts used to create the value rasters 
for calulcuating basin characteristics. Each sub-folder contains stand-alone 
scripts and spatial data sources used to create layers for a user-defined spatial 
range. The layers created in each sub-repo are defined by the scripting process 
and not necessarily the data source or the layer definition. For example, multiple 
sub-repos exist that access the same source layers from SSURGO because the 
scripting process differs significantly enough to warrant separation. 

The `\zonalStatistics` subfolder contains the scripts used to calculate the 
statistics for the user-defined version of the catchments shapefile. This 
sub-repo accepts the output layers from all of the others, as outlined in the 
"Sample Workflow" section. This section also describes the process of running 
the scripts in series. 

An up-to-date, descriptive list of the current sub-repos is maintained in the 
`Covariate Data Status - High Res Delineation.xls` file in this repository. 
This spreadsheet provides the metadata for the final layers and the spatial 
ranges for which they are being used. A duplicate `.csv` version of this file 
is currently maintained for the purpose of specifying and accessing the 
conversion factors for final output of basin characteristics.


# Sample Workflow

The steps below outline an example workflow to create basin characteristics for 
spatial data layers using the U.S. Fish & Wildlife National Wetlands Inventory 
surface water data as an example for the first couple of steps. Basin 
characteristics are calculated for the high resolution catchments in reigon 01.

## Standard Workflow
Below is an example of the basic workflow for assigning attributes to the 
catchment polygons. This is the simplest procedure and does not include the 
extra, source-specific scripts.


1. Navigate to the `\basinCharacteristics\fwsWetlands` repo. Follow the 
instructions in the repo's `README` file for downloading & unzipping data, 
setting user inputs, and executing the code (`\scrpits\fwsWetlands.py`) in 
ArcPython. This information is unique to each sub-repo and is contained in the 
`README` files. Processed spatial data layers (ESRI GRID format) are output to 
`basinCharacteristics\fwsWetlands\gisFiles\NHDHRDV2\outputFiles`.

2. Copy the output spatial layers from step 1 to a stand-alone directory 
containing all other value rasters.

3. Repeat steps 1 and 2 for any other spatial layers outside of the 
`\fwsWetlands` repo to be calculated for catchments shapefile.

4. Place all of the externally created catchments shapefiles (`Catchments01.shp`) 
to a stand-alone directory containing all catchment polygon files to be used.

5. Navigate to the `\basinCharacteristics\zonalStatistics` sub-repo. The `README` 
file in this repo contains specific information on setting the appropriate input 
variables and running the spatial averaging scripts. 

6. Open the "INPUTS" text file in the `\scripts` sub-repo and specify the 
version-specific inputs. Different versions of this file can be maintained. Each 
script allows the user to specify which inputs file is used.

7. Run the `NHDHRDV2_1_zonalStatisticsProcessing.py` script in ArcPython. 
This script calculates the statistics for each spatial layer within the zones 
of the catchments shapefile.

8. Run the `NHDHRDV2_2_delineateUpstreamCatchments.R` script in R, generating a 
list of upstream catchments for each individual catchment in the shapefile. This 
script only needs to be run once initially and is specific to the the catchments 
shapefile.

9. Run the `NHDHRDV2_3_calculateUpstreamStatistics.R` script in R, calculating the upstream average of the spatial data variables for each catchment.

10. Run the `NHDHRDV2_4_statsFileGenerator.R` script in R, formatting and converting 
basin characteristics for output.


## Riparian Buffer Workflow
The workflow for the riparian buffer layers differs slightly from that of the 
catchments. Steps 1 - 6 remain the same as the "Standard Workflow" section. The 
riparian buffer workflow relies on the upstream network lists calculated in Step 
8 from the previous section. 

7. Run the `NHDHRDV2_1R_zonalStatisticsProcessing_RIPARIAN.py` script in 
ArcPython. This script calculates the statistics for each spatial layer within 
the zones of the riparian buffer shapefile.

9. Run the `NHDHRDV2_3R_calculateUpstreamStatistics_RIPARIAN.R` script in R, 
calculating the upstream average of the spatial data variables for each riparian 
buffer.

10. Run the `NHDHRDV2_4_statsFileGenerator.R` script in R, formatting and 
converting basin characteristics for output.


## Contact Info

Kyle O'Neil  
koneil@usgs.gov  

