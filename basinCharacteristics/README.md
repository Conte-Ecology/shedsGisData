basinCharacteristics
====================

# Description

This repo calculates statistics of spatial data within hydrologic catchment delineations in support of the models and web applications created by the Conte Ecology Group. A combination of ArcPy and R scripts are used to process spatial data and assign spatially averaged statistics to catchment polygons. Within each delineation, a unique catchment identifier is assigned values for basin characteristics such as land cover or geology variables.


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

The sub-repositories in `\basinCharacteristics` are grouped by general function. Each sub-folder contains stand-alone scripts and spatial data sources used to create layers for a user-defined spatial range. The layers created in each sub-repo are defined by the scripting process and not necessarily the data source or the layer definition. For example, multiple sub-repos exist that access the same source layers from SSURGO because the scripting process differs significantly enough to warrant separation. 

The exception to this setup is the `\zonalStatistics` sub-folder which calculates the statistics for the user-defined version of the catchments shapefile. This sub-repo accepts the output layers from all of the others, as outlined in the "Sample Workflow" section. Upon initial setup of this repo, some folders must be created manually on the user's local machine. Navigate to the `\basinCharacteristics\zonalStatistics` repo and create a folder for spatial data: `\gisFiles`. In this directory create two folders: `\vectors` and `\rasters`. Adhering to this naming scheme is necessary for code to run properly.

An up-to-date, descriptive list of the current sub-repos is maintained in the `Covariate Data Status - High Res Delineation.xls` file in this repository. This spreadsheet provides the metadata for the final layers and the spatial ranges for which they are being used. A duplicate `.csv` version of this file is currently maintained for the purpose of specifying and accessing the conversion factors for final output of basin characteristics.


# Sample Workflow

The steps below outline an example workflow to create basin characteristics for spatial data layers using the U.S. Fish & Wildlife National Wetlands Inventory surface water data as an example for the first couple of steps. Basin characteristics are calculated for the Northeast High Resolution Delineation (HRD) of catchments.

1. Navigate to the `\basinCharacteristics\fwsWetlands` repo. Follow the instructions in the repo's `README` file for downloading & unzipping data, setting user inputs, and executing the code (`\scrpits\fwsWetlands.py`) in ArcPython. This information is unique to each sub-repo and is contained in the `README` files. Processed spatial data layers (ESRI GRID format) are output to `basinCharacteristics\fwsWetlands\gisFiles\Northeast\outputFiles`.

2. Copy the output spatial layers from step 1 to the `\basinCharacteristics\zonalStatistics\gisFiles\rasters` directory.

3. Repeat steps 1 and 2 for any other spatial layers outside of the `\fwsWetlands` repo to be calculated for catchments shapefile.

4. Copy the externally created catchments shapefile (`NortheastHRD_AllCatchments.shp`) to the `\basinCharacteristics\zonalStatistics\gisFiles\vectors` directory.

5. Navigate to the `\basinCharacteristics\zonalStatistics` sub-repo. The `README` file in this repo contains specific information on running the spatial averaging scripts. 

6. Open the `\scripts` subfolder

7. Specify the version-specific inputs in the `basinCharacteristics\zonalStatistics\scripts\HRD_INPUTS.txt` file.

8. Run the `HRD1_zonalStatisticsProcessing.py` script in ArcPython. This script calculates the statistics for each spatial layer within the zones of the catchments shapefile.

9. Run the `HRD2_delineateUpstreamCatchments.R` script in R, generating a list of upstream catchments for each individual catchment in the shapefile. This script only needs to be run once initially and is specific to the the catchments shapefile.

10. Run the `HRD3_calculateUpstreamStatistics.R` script in R, calculating the upstream average of the spatial data variables for each catchment.

11. Run the `HRD4_statsFileGenerator.R` script in R, formatting and converting basin characteristics for output.


# Contact Info

Kyle O'Neil  
koneil@usgs.gov  
(413) 863-3829  

