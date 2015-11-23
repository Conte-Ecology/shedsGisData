Zonal Statistics
================

## Description

This repo stores the necessary scripts and files to calculate basin characteristics for the layers created in the `\basinCharacteristics` parent directory. Both ArcPy and R scripts are used in series to generate the final output statistics. The repo is set up to handle different versions of basin characteristics such as catchments or riparian buffers separately. Each version will have a series of scripts that must be run in the specified order. Scripts are named by letters indicating the series, a number indicating the order in the series, and the title of the script preceded by an underscore. For exmple, `NHDHRDV2_1_zonalStatisticsProcessing.py` is the first script in the High Resolution Delineation Versoin 2 (NHDHRDV2) series and its main prupose is to process the raw layers and run them through the "Zonal Statistics" tool in ArcPython. Each series is described below in depth in the "Current Versions" section. Each time a new version is added, this README file should be updated. 

Prior to running any scripts, two spatial data directories must be created. One directory holds the the rasters to calculate stats for and the other holds the polygon shapefiles specifying the zones to calculate stats over. It is suggested practice to create these directories in a `zonalStatistics\gisFiles` sub-folder with the names `rasters` and `vactors`. Each version will point to these directories for spatial data. The rasters should be copied from the `\outputFolder` directories from other repos in the `\basinCharacteristics` parent directory. If this is the case, no pre-processing is necessary for the spatial files.  All other folders are created within the scripts.


## Current Versions:

### **Catchments for High Resolution Delineation**

#### Repo
`basinCharacteristcs\zonalStatistics\version\NHDHRDV2`

#### Description
This section calculates the basin characteristics for the catchments. Two values are calculated for each individual catchment:

1. Local - The spatial average of the variable within the individual catchment polygon
2. Upstream - The spatial average (weighted by indiviudal catchment area) of all of the local values calculated for all of the catchments in the upstream network including the specified catchment 

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

  Open this script and set the `inputsFilePath` variable to the path of the inputs `.txt` file created in Step 1. Set the `raster_directory` variable to the path to the folder containing all of the value rasters. Set the `vector_directory` variable to the path to the folder containing all of the polygon shapefiles representing the zones. Run the script in Arc Python. Allow script to run completely  before moving on to the next script. This script does the following:
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
    7. Outputs two `.csv` files, 1 upstream and 1 local, for each variable into the `\rTables` directory. Files are grouped by the zonal polygons shapefile ID (e.g. `zonalStatistics\versions\NHDHRDV2\rTables\Catchments01\upstream_forest.csv`). 
  
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
    3. Outputs two `.csv` files, 1 upstream and 1 local, containing a count of each barrier type into the `\rTables` directory (e.g. `zonalStatistics\versions\NortheastHRD\rTables\upstream_deg_barr_1.csv`). 
  
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
  2. NULL will include the variables from the `rasterList` object in the `HRD_INPUTS.txt` file
  3. Manually list the variables to output (e.g. `c("forest", "agriculture")`)
  Set the `activateThreshold` variable to `TRUE` or `FALSE`. This variable determines if entries with less than a specified percent of the area with data will be set to NA. Set the `missingDataThreshold` to a percentage value of the minimum allowable area with data for values to remain valid. Zones with less than this percent of the area with data will be set to NA.
  
  The script does the following:
    1. Reads the individual `.csv` files according to the `outputVariables` object. 
    2. Converts each basin characteristic to the output units according to factors in the `Covariate Data Status - High Res Delineation.csv` file.
    3. Selects values below the `missingDataThreshold` and converts them to NA.
    4. Outputs an a long format dataframe for each zones shapefile. This file is saved to the `\completedStats` folder (e.g. `\zonalStatistics\versions\NHDHRDV2HRD\completedStats\zonalStatsForDB_Catchments01`).
  
#### Next Steps
Next steps include the possibility of adding new variables or a new delineation resolution.



### **Riparian Buffers for High Resolution Flowlines**

#### Repo
`basinCharacteristcs\zonalStatistics\version\NHDHRDV2`

#### Description

This section calculates the basin characteristics for riparian buffer zones based on the high resolution delineation. For each buffer, 2 values are calculated:

1. Local - The spatial average of the variable within the individual buffer polygon
2. Upstream - The spatial average (weighted by indiviudal buffer area) of all of the local values calculated for all of the buffers in the upstream network including the specified reach 

The scripts in this section are dependent on some elements of the overall HRD zonal statistics process, which should be completed first for all layers and ranges used in this section. First, the rasters are processed in the HRD section to be resampled and reprojected to match the catchments and each other. The scripts in this section rely on these previously processed rasters, pointing to the repo that contains the existing files. Second, the network delineation is identical to the HRD network. The `NortheastHRD_delineatedCatchments.RData` file from that section is referenced directly from this section. These steps are taken primarily to save time and data storage space. The riparian versions of the scripts are labelled as such and should be run in the same sequential order. 


#### Required tools, packages, etc.

**ArcPy Tools**
  - ArcGIS Spatial Analyst
  - ArcGIS Spatial Analyst Supplemental tools, v1.3 - http://blogs.esri.com/esri/arcgis/2013/11/26/new-spatial-analyst-supplemental-tools-v1-3/

**R Packages**
  - `reshape2`
  - `foreign`
  - `tcltk`
  - `dplyr`
  - `lazyeval`

#### Steps to Run
1. The text file used to specify common user inputs is created. This file will be used across all scripts in the series. See the current `INPUTS_NHDHRDV2.txt` in the `zonalStatistics` repo for sample formatting. The table below describes the vairables to be changed. Do not add extra lines or change the structure of this file other than changing the variable values.

 |    Object Name          |                        Description                                                                  |       Example                       |
 |:-----------------------:| --------------------------------------------------------------------------------------------------- |------------------------------------ |
 | `outputName`            |  Name associated with this particular version                                                       | `"NHDHRDV2"`                        |
 | `catchmentsFileNames`   |  Names of the catchments shapefile (without extension)                                              | `c("riparianBufferDetailed50ft_01", "riparianBufferDetailed50ft_02")` |
 | `zoneField`             |  Name of the field used to identify features ("Zone Field")                                         | `"FEATUREID"`                       |
 | `statType`              |  Statistic to calculate                                                                             | `"MEAN"`                            |
 | `discreteRasters`       |  List of the discrete data layers (e.g. land cover) to calculate the statistic for                  | `c("forest", "agriculture")`        |
 | `continuousRasters`     |  List of the continuous data layers (e.g. climate) to calculate the statistic for                   | `c("ann_tmax_c", "elevation")`      |
 | `baseDirectory`         |  The file path (with forward slashes) to the base directory where all of the files will be written  | `"C:/User/Data/basinCharacteristcs"`|



 
2. **NHDHRDV2_1R_zonalStatisticsProcessing_RIPARIAN.py** - Script to calculate statistics on the specified raster(s) for each of the polygons in the buffer shapefile. 

  Open this script and set the `inputsFilePath` variable to the path of the inputs `.txt` file created in Step 1. Run the script in Arc Python. Allow script to run completely before moving on to the next. It does the following:
    1. Reads user-specified inputs from Step 1
    2. Sets up the folder structure used by other scripts in this version
    3. Reprojects the zone and HUC polygons as needed to ensure spatial consistency
    4. Calculates the mean value for each zone in the zone shapefile (sectioned by HUC6 into file sizes that will not crash Arc)
    5. Joins all of the sections and elminiates duplicate features
    6. Adds -9999 values for zones that are not assigned any value to account for all buffers in original shapefile
    7. Calculates the areas for the buffer polygons in the shapefile
    8. Outputs the specified spatial statistic for all of the buffers as `.dbf` tables in the `\gisTables` folder in the run-specific versions folder (e.g. `zonalStatistics\versions\riparianBuffers\gisTables\forest_50ft.dbf`)
    9. Outputs the polygon areas as a `.dbf` file.
  
  Example output:

  | FEATUREID | COUNT  |    AREA    |    MEAN    |
  |  :-----:  | ------ | ---------- | ---------- |
  |   350854  |   6    | 9608.108   | 0.00000000 |
  |   350855  |   1    | 1601.351   | 0.00000000 |
  |   350881  |  327   | 523641.872 | 0.20795107 |
  |   350888  |  105   | 168141.886 | 0.03809524 |
  |   350891  |  83    | 132912.157 | 0.22891566 |
  |   350897  |   6    | 9608.108   | 0.16666667 |



3. **RB2_calculateUpstreamStatistics.R** - Script that calculates the upstream average of all basin characteristics

  Open this script in R and set the `baseDirectory` variable to the path up to and including the `zonalStatistics` folder and run the script. This script does the following:
    1. Reads user-specified inputs from Step 1
    2. Reads the ArcPy output tables for each of the rasters specified in the `RB_INPUTS.txt` file
    3. Converts all -9999 values to NA
    4. Uses the delineated catchments object to calculate the upstream average of each basin characteristic (weighted by area)
    5. Outputs two `.csv` files named by `bufferID`, 1 upstream and 1 local, for each variable into the `\rTables` directory (e.g. `zonalStatistics\versions\riparianBuffers\rTables\upstream_forest_50ft.csv`)
    
  Example output:

  | FEATUREID |    MEAN      |
  |  :-----:  | ------------ |
  |   730243  |      0       |
  |   730254  |  0.296062992 |
  |   730258  |       0.25   |
  |   730259  |  0.029126214 |
  |   730260  |  0.266112266 


4. **RB3_statsFileGenerator.R** - Script that generates useable `.RData` files of basin characteristics values

  Open this script in R and set the `baseDirectory` variable to the path up to and including the `\zonalStatistics` folder and run the script. Specify the variables to include in `outputVariables`. There are 3 options for specifying the variables to output:
  1. "ALL" will include all of the variables present in the folder
  2. NULL will include the variables from the `rasterList` object in the `RB_INPUTS.txt` file
  3. Manually list the variables to output (e.g. `c("forest", "agriculture")`)
  
  The script does the following:
    1. Reads the individual `.csv` files according to the `outputVariables` object. 
    2. Converts each basin characteristic to the output units according to factors in the `Covariate Data Status - High Res Delineation.csv` file.
    3. Outputs an `.RData` file with two dataframes: `LocalStats` and `UpstreamStats`. This file is names with the date it was run and output to the `\completedStats` folder (e.g. `\zonalStatistics\versions\riparianBuffers\completedStats\zonalStatsRiparianBuffer_50ft_2015-04-10.RData`).
    4. Outputs an a long format dataframe for input into the web system database. This file is names with the date it was run and output to the `\completedStats` folder (e.g. `\zonalStatistics\versions\riparianBuffers\completedStats\zonalStatsForDB_riparianBuffers50ft_2015-04-10.RData`).
  

#### Next Steps
Next steps include the possibility of adding new variables, changing buffer distances, or creating contiguous buffers to avoid overlapping polygons (though other errors are likely to occur with this update).



### **Point Delineation for MassDOT Project**

#### Repo
`basinCharacteristcs\zonalStatistics\version\pointDelineation`

#### Description

This version calculates the basin characteristics for the delineated basins for the culverts and flow gages used in the MassDOT Culvert Project. based on the high resolution delineation. For each basin, the spatial average of the basin characteristcs and the percent of the catchment area with data are calculated. This accounts for cases where there is missing raster data within the catchment boundary.

The scripts in this section are dependent on the raster processing completed in the HRD section (resampling and reprojecting each raster to match the catchments and each other). The scripts in this section point to the repo that contains the existing files. These steps are taken primarily to save time and data storage space.

#### Required tools, packages, etc.

**ArcPy Tools**
  - ArcGIS Spatial Analyst
  - ArcGIS Spatial Analyst Supplemental tools, v1.3 - http://blogs.esri.com/esri/arcgis/2013/11/26/new-spatial-analyst-supplemental-tools-v1-3/

**R Packages**
  - `dplyr`
  - `foreign`

#### Steps to Run

1. **PD1_zonalStatisticsProcessing.py** - Script to calculate statistics on the specified raster(s) for each of the polygons in the buffer shapefile

  Open this script and set the `baseDirectory` variable to the path up to and including the `\zonalStatistics` folder. Unlike other versions, the user inputs are entered directly in the script file and not a separate input file. Set these inputs:
  
 |    Object Name          |                        Description                                                    |      Example                   |
 |:-----------------------:| ------------------------------------------------------------------------------------- |------------------------------- |
 | `outputName`            |  Name associated with this particular version                                         | `"pointDelineation"`            |
 | `catchmentsFilePath`    |  Name of the catchments shapefile (without extension) | `"C:/KPONEIL/delineation/northeast/pointDelineation/outputFiles/delin_basins_deerfield_2_17_2015.shp"` |
 | `zoneField`             |  Name of the field used to identify features ("Zone Field")                           | `"DelinID"`                  |
 | `statType`              |  Statistic to calculate                                                               | `"MEAN"`                       |
 | `rasterDirectory`       |  File path to the directory containing the rasters to run  | `"C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics/gisFiles/versions/NortheastHRD/projectedRasters.gdb"` |  
 | `rasterList`            |  List of the rasters to run | `["forest", "agriculture", "impervious", "fwswetlands", "fwsopenwater"]`   |

  Run the script in Arc Python. Allow script to run completely before moving on to the next script. This script does the following:
    1. Sets up the folder structure in the specified directory
    2. Reprojects the zone polygon as needed
    3. Calculates the mean value for each zone in the zone shapefile
    4. Adds -9999 values for zones that are not assigned any value
    5. Outputs the specified spatial statistic for all of the catchments as `.dbf` tables in the `\gisTables` folder in the run-specific versions folder (e.g. `zonalStatistics\versions\pointDelineation\gisTables\forest_MEAN.dbf`)
    
  Example output:

  | FEATUREID | COUNT  |    AREA    |    MEAN    |
  |  :-----:  | ------ | ---------- | ---------- |
  |   350854  |   6    | 9608.108   | 0.00000000 |
  |   350855  |   1    | 1601.351   | 0.00000000 |
  |   350881  |  327   | 523641.872 | 0.20795107 |
  |   350888  |  105   | 168141.886 | 0.03809524 |
  |   350891  |  83    | 132912.157 | 0.22891566 |
  |   350897  |   6    | 9608.108   | 0.16666667 | 
 
2. **PD2_finalizeZonalStatistics.R** - Script to pull together the results from the ArcPy processing and TNC dams processing (see repo: `basinCharacteristics\tncDams`)

  Open this script and set the `baseDirectory` variable to the path up to and including the `\zonalStatistics` folder. The user inputs are again entered directly in the script file and not a separate input file:

  |    Object Name          |                        Description                                                    |      Example                                                                                               |
  |:-----------------------:| ------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
  | `outputName`            |  Name associated with this particular version                                         | `"pointDelineation"`                                                                                       |
  | `catchmentsFilePath`    |  Name of the catchments shapefile (without extension)                                 | `"C:/KPONEIL/delineation/northeast/pointDelineation/outputFiles/delin_basins_deerfield_2_17_2015.shp"`     |
  | `zoneField`             |  Name of the field used to identify features ("Zone Field")                           | `"DelinID"`                                                                                                |
  | `statType`              |  Statistic to calculate                                                               | `"MEAN"`                                                                                                   |
  | `rasterList`            |  List of the rasters to run                                                           | `c("forest", "agriculture", "impervious", "fwswetlands", "fwsopenwater")`                                  |
  | `conversionValues`      |  List of values to multiply the raw input by to convert them to the desired output units. These values should match the order and count of the `rasterList` | `c(100, 100, 1, 100, 100)`           |
  | `damsFile`              |  File path to the barrier count output file for this version                          | `"C:/KPONEIL/GitHub/projects/basinCharacteristics/tncDams/outputTables/barrierStats_pointDelineation.dbf"` |  

  Run the script in R. This script does the following:
    1. Reads the ArcPy output tables for all specified basin characteristics
    2. Changes all -9999 values to NA
    3. Converts values according to specified factors
    4. Outputs a dataframe of all of the basin characteristics specified in `rasterList` (e.g. `versions\pointDelineation\completedStats\pointDelineationStats.RData`).

#### Next Steps

Next steps include the posssibility of adding new layers desired for the MassDOT Culvert Project. It is possible to set this script up according to the structure of other versions, mainly by moving the user inputs to a separate text file accessed by all of the scripts.
