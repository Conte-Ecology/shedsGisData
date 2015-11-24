Zonal Statistics
================

## Description

This repo stores the necessary scripts and files to calculate basin characteristics for the layers created in the `\rasterPrep` directory. Both ArcPy and R scripts are used in series to generate the final output statistics. The repo is structured to handle different delinieation versions separately, while products from the same network dataset, such as different hydrologic regions, are grouped together. Differing layer structures like catchments and riparian buffers require a slightly different series of scripts, but still fall under the same parent repo defined by version.

Each version will have a series of scripts that must be run in the specified order. Scripts are named by the version grouping, a number indicating the order in the series, and the title of the script preceded by an underscore. For exmple, `NHDHRDV2_1_zonalStatisticsProcessing.py` is the first script in the High Resolution Delineation Versoin 2 (NHDHRDV2) series and its main prupose is to process the raw layers and run them through the "Zonal Statistics" tool in ArcPython. Each series is described below in depth in the "Current Versions" section. Each time a new version is added, this README file should be updated. 



## NHD High Resolution Delineation - Version 2

#### Description
This section calculates the basin characteristics for the catchments and riparian buffers. Two values are calculated for each individual polygon:

1. Local - The spatial average of the variable within the individual catchment polygon
2. Upstream - The spatial average (weighted by indiviudal area) of all of the local values calculated for all of the catchments in the upstream network including the specified catchment 

In addition to the values for each catchment, the percent of the catchment area with data is calculated for each catchment. This accounts for cases where there is missing raster data within the catchment boundary. This is determined by dividing the "AREA" column output by the Zonal Statistics tool by the area of the rasterized version of the catchments.

#### Required tools, packages, etc.

**ArcPy Tools**
  - ArcGIS Spatial Analyst

**R Packages**
  - `reshape2`
  - `foreign`
  - `tcltk`
  - `dplyr`
  - `lazyeval`

### **Catchments**

This process defines some layers that will be used in other sections and should be executed first. Typically for large layers the ArcPy script may take a few days to run due to some computationally intensive GIS procedures.


#### Steps to Run
1.  The text file used to specify common user inputs is created. This file will be used across all scripts in the series. See the current `INPUTS_NHDHRDV2.txt` in the `zonalStatistics` repo for sample formatting. The table below describes the vairables to be changed. Do not add extra lines or change the structure of this file other than changing the variable values.
 
 |    Object Name          |                        Description                                                                  |       Example                       |
 |:-----------------------:| --------------------------------------------------------------------------------------------------- |------------------------------------ |
 | `outputName`            |  Name associated with this particular version                                                       | `"NHDHRDV2"`                        |
 | `catchmentsFileNames`   |  Names of the catchments shapefile (without extension)                                              | `c("Catchments01", "Catchments02")` |
 | `zoneField`             |  Name of the field used to identify features ("Zone Field")                                         | `"FEATUREID"`                       |
 | `statType`              |  Statistic to calculate                                                                             | `"MEAN"`                            |
 | `discreteRasters`       |  List of the discrete data layers (e.g. land cover) to calculate the statistic for                  | `c("forest", "agriculture")`        |
 | `continuousRasters`     |  List of the continuous data layers (e.g. climate) to calculate the statistic for                   | `c("ann_tmax_c", "elevation")`      |
 | `baseDirectory`         |  The file path (with forward slashes) to the base directory where all of the files will be written  | `"C:/User/Data/basinCharacteristcs"`|
 
2. **NHDHRDV2_1_zonalStatisticsProcessing.py** - Script to calculate statistics on the specified raster(s) for each of the catchments in the polygon shapefile. 

  Open this script and set the `inputsFilePath` variable to the path of the inputs `.txt` file created in Step 1. Set the `raster_directory` variable to the path to the folder containing all of the value rasters. The rasters should be copied from the `\outputFolder` directories from repos in the `\rasterPrep` directory. Set the `vector_directory` variable to the path to the folder containing all of the polygon shapefiles representing the zones. Run the script in Arc Python. Allow script to run completely  before moving on to the next script. This script does the following:
    1. Reads user-specified inputs from Step 1  
    2. Sets up the folder structure used by the rest of the scripts in the series  
    3. Projects & resamples the rasters to match the zone layer (catchments) ensuing consistency of spatial references
    4. Rasterizes the zone polygon so it can be used to directly compare area in each catchment with or without raster data
    5. Calculates the specified statistic (e.g. "MEAN") for each zone in the zone shapefile using the "Zonal Statistics" tool
    6. Adds -9999 values for zones that are not assigned any value ensuring that all values from the input catchments file are account for
    7. Outputs the specified spatial statistic for all of the catchments as `.dbf` tables in the `\gisTables` folder in the run-specific versions folder (e.g. `zonalStatistics\versions\NHDHRDV2\gisTables\forest.dbf`)
    
  Example output:

  | FEATUREID | COUNT  |    AREA    |    MEAN    |
  |  :-----:  | ------ | ---------- | ---------- |
  |   350854  |   6    | 9608.108   | 0.00000000 |
  |   350855  |   1    | 1601.351   | 0.00000000 |
  |   350881  |  327   | 523641.872 | 0.20795107 |
  |   350888  |  105   | 168141.886 | 0.03809524 |
  |   350891  |  83    | 132912.157 | 0.22891566 |
  |   350897  |   6    | 9608.108   | 0.16666667 |


3. **NHDHRDV2_2_delineateUpstreamCatchments.R** - Script that generates a list of the upstream catchments for each catchment in the shapefile

  Open this script and set the `inputsFilePath` variable to the path of the inputs `.txt` file created in Step 1. Run the script in R. It does the following:
    1. Reads user-specified inputs from Step 1
    2. Determines if catchments have already been delineated and halts the script if the file already exists in the proper directory
    3. Uses the catchment relationships built into the shapefile ("NextDownID" field) to generate a delineation of the network from each catchment
    4. Formats the result as a list of lists with each sublist named by the primary (most downstream) catchment (`delineatedCatchments$'730076'`)
    5. Saves the output as an `.RData` file with the object named `delineatedCatchments` in the `\versions` directory (e.g. `zonalStatistics\versions\NHDHRDV2\delineatedCatchments\Delineation_Catchments01.RData`)

  Example output:
  ```R
  str(delineatedCatchments)
    List of 373074
      $ 730076 : int [1:7] 730076 730086 730080 730091 730087 730085 730095
      $ 730077 : int 730077
      $ 730086 : int [1:3] 730086 730085 730095
      $ 730080 : int [1:3] 730080 730091 730087
  ```


4. **NHDHRDV2_3_calculateUpstreamStatistics.R** - Script that calculates the upstream average of all basin characteristics

  Open this script and set the `inputsFilePath` variable to the path of the inputs `.txt` file created in Step 1. Run the script in R. This script does the following:
    1. Reads user-specified inputs from Step 1.
    2. Reads the two versions of the catchment areas (vector and raster). The vector area is the actual area, while raster area is used for determining the area containing raster data for each basin characteristic.
    3. Reads the ArcPy output `.dbf` tables for each of the rasters specified in the inputs text file.
    4. Converts all -9999 values to NA
    5. Calculates the percent of the catchment area that has contributing raster data for each local catchment. This accounts for catchments where only a small portion of the raster is present and output stats are effectively NA.
    6. Uses the delineated catchments object to calculate the upstream average of each basin characteristic (weighted by area) as well as the percent of the area with data.
    7. Outputs two `.csv` files, 1 upstream and 1 local, for each variable into the `\rTables` directory. Files are grouped by the zonal polygons shapefile names (e.g. `zonalStatistics\versions\NHDHRDV2\rTables\Catchments01\upstream_forest.csv`). 
  
  Example output:
  
  | FEATUREID |     MEAN    | percentAreaWithData |
  | :-------: | ----------- | ------------------- |
  | 730236    |	0.24288425	|  0.654682783        |
  | 730243    |	0.052083333	|  3.098773402        |
  | 730246    |	0.237735849	|  0.936120106        |
  | 730252    |	0.400487975	|  11.82605111        |
  | 730254    |	0.412833724	|  93.07699015        |

5. **NHDHRDV2_3a_calculateUpstreamStatistics (TNC Dams).R** - Script that calculates the upstream count of dams defined by TNC. This script is optional and depends on the TNC dams analysis.

  Open this script and set the `inputsFilePath` variable to the path of the inputs `.txt` file created in Step 1. Set the path to the results table from the matching version of the barrier analysis repo (`barrierStatsFilePath <- 'C:/KPONEIL/GitHub/projects/basinCharacteristics/tncDams/outputTables/barrierStats_NHDHRDV2.dbf.dbf'`) as well as the path specifying the catchments missing data(`missingDataFilePath <- 'C:/KPONEIL/GitHub/projects/basinCharacteristics/tncDams/outputTables/barrierStatsNAs_NHDHRDV2.dbf'`). Run the script in R. This script does the following:
    1. Reads user-specified inputs from Step 1.
    2. Uses the delineated catchments object to calculate the number of barriers of each type located upstream from each catchment.
    3. Changes the values for the catchments specified in the `missingDataFilePath` 
    4. Outputs two `.csv` files, 1 upstream and 1 local, containing a count of each barrier type into the `\rTables` directory (e.g. `zonalStatistics\versions\NortheastHRD\rTables\upstream_deg_barr_1.csv`). 
  
  Example output:
  
  | FEATUREID | deg_barr_1  |
  | :-------: | ----------- |
  | 730236    |     0	      |
  | 730243    |   	0	      |
  | 730246    |   	1	      |
  | 730252    |   	0	      |
  | 730254    |	    1	      |


6. **NHDHRDV2_3b_percentAreaWithData_undev_forest.R** - Script that calculates percent of the area with data for the unique undeveloped forest layer. Setting raster cells to "No Data" in this layer (see [description](https://github.com/Conte-Ecology/shedsData/blob/master/basinCharacteristics/Covariate%20Data%20Status%20-%20High%20Res%20Delineation.xlsx)) results in an inaccurate calculation of percent area with data which must be corrected. This script is only run if the `undev_forest` variable is being processed.

  Open this script and set the `inputsFilePath` variable to the path of the inputs `.txt` file created in Step 1. Run the script in R. This script does the following:
    1. Reads the local and upstream CSV files for the `undev_forest` layer
    2. Replaces the `percentAreaWithData` column values with those from a comparable layer from the same data source (e.g. `forest`)

 
7. **NHDHRDV2_4_statsFileGenerator.R** - Script that generates long format CSV files for upload to SHEDS.

  Open this script and set the `inputsFilePath` variable to the path of the inputs `.txt` file created in Step 1. Specify the variables to include in `outputVariables`. There are 3 options for specifying the variables to output:
  1. "ALL" will include all of the variables present in the folder
  2. NULL will include the variables from the `discreteRasters` and `continuousRasters` objects in the `INPUTS_NHDHRDV2.txt` file
  3. Manually list the variables to output (e.g. `c("forest", "agriculture")`)
  Set the `activateThreshold` variable to `TRUE` or `FALSE`. This variable determines if entries with less than a specified percent of the area with data will be set to NA. Set the `missingDataThreshold` to a percentage value of the minimum allowable area with data for values to remain valid. Zones with less than this percent of the area with data will be set to NA.
  
  The script does the following:
    1. Reads the individual `.csv` files according to the `outputVariables` object. 
    2. Converts each basin characteristic to the output units according to factors in the `Covariate Data Status - High Res Delineation.csv` file.
    3. Selects values below the `missingDataThreshold` and converts them to NA.
    4. Outputs an a long format dataframe for each zones shapefile. This file is saved to the `\completedStats` folder (e.g. `\zonalStatistics\versions\NHDHRDV2HRD\completedStats\zonalStatsForDB_Catchments01`).
  
#### Next Steps
Next steps include the possibility of adding new variables or a new delineation resolution.





### **Riparian Buffers**

While this section may be altered to run independently from the previous "Catchments" section, the current setup works best if this is run after the basin characteristics have been processed for the catchments. In particular, the network delineation files and the value raster processing depends on results from the catchments section.


#### Steps to Run
1. The inputs file is set up according to Step 1 in the "Catchments" section and saved as a new file such as `INPUTS_NHDHRDV2_RIPARIAN.txt`.

 
2. **NHDHRDV2_1R_zonalStatisticsProcessing_RIPARIAN.py** - Script to calculate statistics on the specified raster(s) for each of the polygons in the buffer shapefile. 

  Running this script is the same as the similar script in step 2 of the "Catchments" section. The exception is the addition of the `rasterTemplate` input which should be set to one of the catchment raster layers created in the previous section. This serves the purpose of ensuring spatial constistency between the riparian buffer rasters and the value rasters. 


3. Check to make sure that the network delineation files exist from the "Catchments" section. The script in the next step will point to these files.


4. **NHDHRDV2_3R_calculateUpstreamStatistics_RIPARIAN.R** - Script that calculates the upstream average of all basin characteristics for the riparian buffers.

  Running this script is the same as running the similar script from step 4 in the "Catchments" section. The script itself contains some minor differences to account for the network delineation.


5. **NHDHRDV2_4_statsFileGenerator.R** - Script that generates useable `.RData` files of basin characteristics values

This script is designed to work for both catchments and riparian layers. Running this script is the same as in the previous "Catchments" section.
  

#### Next Steps
Next steps include the possibility of adding new variables, adding new buffer distances, or changing buffer polygon structure.
