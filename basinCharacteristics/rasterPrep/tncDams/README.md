TNC Dams
========

This script calculates the total number of dams, by barrier type, in each 
catchment. The dams are defined by the Nature Conservancy and have been snapped 
to the high resolution flowlines by the UMass Land Ecology Lab for the Designing 
Sustainable Landscapes Project.

This repo is different than the other basin characteristics in that it requires 
the shapefile of the catchments over which the dams will be counted. In this way, 
output is version specific.

## Data Sources
| Layer           | Source                               |
|:-----:          | ------                               |
| dams shapefile  | UMass Land Ecology Lab - DSL Project |
| Catchments      | Conte Ecology Group - NHDHRDV2       |

## Steps to Run:

The folder structure is set up within the scripts. In general, the existing 
structure in the repo should be followed.

1. Open the script `tncDams.py`

2. Change the values in the "Specify inputs" section of the script
 - `baseDirectory` is the path to the `\tncDams` folder (current parent working 
 directory)
 - `polygonsFile` is the catchments to assign the dams to
 - `damsFile` is the shapefile depicting the location of the dams
 - `outputName` is the name that will be associated with this particular run of 
 the tool (e.g. `NHDHRDV2` for all High Resolution Catchments)
 - `zoneField` is the field name of the the catchments unique identifier

3. Run the script in ArcPython. It does the following:
 - Sets up the folder structure in the specified directory
 - Removes impoundments not snapped to the flowlines or approved for use
 - Spatially joins the catchments to the dams
 - Counts the number of dams in each catchment
 - Saves the completed tables to the `tncDams\outputTables` directory


## Output Table

#### Dam count
*Table name:* barrierStats <br>
*Description:* This table provides columns for each barrier degree as defined by
the Nature Conservancy. The total number of dams of each barrier degree is 
provided for each catchment as outlined in the example table:

| Rowid  | OID  | DELINID | FREQUENCY | SUM_DEG_BARR_1 | SUM_DEG_BARR_2 | SUM_DEG_BARR_3 | SUM_DEG_BARR_4 | SUM_DEG_BARR_5 | SUM_DEG_BARR_6 | SUM_DEG_BARR_7 |
|:-----: |:----:|:-------:|:---------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|
|  1     | 0    | 100000  |    1      |       0        |       0        |       0        |       0        |       0        |       0        |       0        |
|  2     | 0    | 100001  |    1      |       0        |       0        |       0        |       0        |       0        |       0        |       0        |
|  3     | 0    | 100002  |    1      |       0        |       0        |       0        |       0        |       0        |       0        |       0        |
|  4     | 0    | 100003  |    3      |       3        |       0        |       0        |       0        |       0        |       0        |       0        |


## Notes

- The scrpit is specific to the dams shapefile and should be tested for 
compatibility with any new files.
