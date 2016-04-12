Daymet Climate Data
===================

# Description
This repo assigns the Daymet climate record to the hydrologic catchments in the 
NHDHRDV2 dataset. The Daymet data are daily time series of climate variables as 
distributed through the [ORNL DAAC](https://daymet.ornl.gov/). Each catchment 
gets daily records for precipitation(mm), minimum and maximum temperature 
(degrees C), water vaport pressure (Pa), incident solar radiation (W/m2), snow 
water equivalent (kg/m2), and day length (seconds) over the observed period of 
1980 - 2014. The 1km x 1km gridded data are spatially assigned to the catchment 
polygons by using the custom 
[zonalDaymet package](https://github.com/Conte-Ecology/zonalDaymet).


# Software Requirements

R version 3.1.2  
Current R libraries:  
  - `maptools`
  - `devtools`
  - `zonalDaymet` (custom package)


# Workflow
The database is initially populated with the 1980-2014 climate records. When 
the new data is released annually thereafter, the process is re-run for just 
that year. Step 1 may not be necessary to repeat if shapefiles still exist 
from previous years.

1. Project the zones shapefiles into the Daymet spatial reference (Lambert 
Conformal Conic) as defined on the 
[Data Documentation Page](https://daymet.ornl.gov/datasupport.html). Save all 
of the projected shapefiles to use into the same directory. Currently, the 
script is structured to read zone shapefiles with the name format 
"Catchments[`HYDRO_REGIONS`]_Daymet.shp", referencing one of the input variables 
in step 2. An example of one shapefile name is "Catchments01_Daymet.shp". If this
naming scheme is altered, it should be reflected in the part of the script that 
reads the shapefiles.

2. Set the variables in the "Specify Inputs" section:

 |  Variable Name    | Description                                                                          | Example                                |
 |:-----------------:| ------------------------------------------------------------------------------------ | -------------------------------------- |
 |`START_YEAR`       | The first year of the time period to assign                                          | `1980`                                 |
 |`END_YEAR`         | The last year of the time period to assign                                           | `2014`                                 |
 |`HYDRO_REGIONS`    | The two-digit numeric ID of the hydrologic catchments                                | `c("01", "02", "03", "04", "05", "06")`|
 |`VARIABLES`        | The abbreviated variable names to process (as defined in the Daymet mosaic files)    | `c("tmax", "tmin", "prcp")`            |
 |`DAYMET_DIRECTORY` | The path to the directory where downloaded NetCDF mosaic files will be saved         | `"C:/Data/Climate/Daymet/Input"`       |
 |`SPATIAL_DIRECTORY`| The path to the directory where the zones shapefiles are saved                       | `"C:/Data/Spatial/Hydro/Catchments"`   |
 |`DATABASE_PATH`    | The filepath to the output database to which the `HYDRO_REGIONS` ID will be appended | `"C:/Data/Climate/Daymet/Output"`      |
 |`TABLE_NAME`       | The name of the table in the database to output                                      | `"climateRecord"`                      |
 |`ZONE_FIELD`       | The unique ID field for the catchments                                               | `"FEATUREID"`                          |

3. If the Daymet NetCDF mosaic layers have not yet been downloaded, run the 
`downloadMosaic` function to do so.

4. Execute the averaging section of the script to assign climate records to the 
catchments.

5. Transfer the SQLite databases to a dataset-specific directory on the server 
(e.g. `/home/kyle/data/daymet/1980-2014`).

6. Execute the shell scripts setup to populate the postgres database with the 
records from the SQLite databases: <br>
*Initial database upload*
> cd /home/kyle/scripts/db/daymet <br>
> ./import_daymet.sh sheds_new /home/kyle/data/daymet/1980-2014 <br>

  *Subsequent year upload* <br>
  > cd /home/kyle/scripts/db/daymet <br>
  > ./import_daymet.sh sheds_new /home/kyle/data/daymet/2015 <br>


# Methods

## Averaging 
When multiple Daymet cell centroid coordinates fall into a spatial 
zone, the average of the records are assigned to the `ZONE_FIELD` ID. If a single 
cell centroid falls within the zone, that record is assigned to the `ZONE_FIELD` ID. If 
no cell centroids fall within the zone, then the point nearest to the zone 
centroid is used to assign the record to the `ZONE_FIELD` ID.

## Output
The records are output as SQLite databases defined separately by 
hydrologic zone IDs (`HYDRO_REGIONS`). These SQLite databases get uploaded 
to the primary SHEDS database through a series of Postgres scripts.

## Functions
Function-specific descriptions can be found on the 
[zonalDaymet package](https://github.com/Conte-Ecology/zonalDaymet) page. 


# Contact Info
Kyle O'Neil  
koneil@usgs.gov 



