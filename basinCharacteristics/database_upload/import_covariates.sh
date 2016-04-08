#!/bin/bash
# imports covariates to existing db table 'data.covariates'
# csv file must have columns [featureid, variable, value, zone]

# usage: $ ./append_covariates.sh <db name> <path to covariates directory>
# example: $ ./append_covariates.sh conte_dev /conte/data/covariates/20150129


set -eu
set -o pipefail

DB=$1
FOLDER=$2

# Convert featureid column types to big integer so they can handle the type "double" values from the shapefiles
psql -d $DB -c "ALTER TABLE data.covariates ALTER COLUMN featureid TYPE BIGINT;"

# Loop through tables to upload
for TABLE in zonalStatsForDB_Catchments01 zonalStatsForDB_Catchments02 zonalStatsForDB_Catchments03 zonalStatsForDB_Catchments04 zonalStatsForDB_Catchments05 zonalStatsForDB_Catchments06 zonalStatsForDB_riparianBufferDetailed200ft_01 zonalStatsForDB_riparianBufferDetailed200ft_02 zonalStatsForDB_riparianBufferDetailed200ft_03 zonalStatsForDB_riparianBufferDetailed200ft_04 zonalStatsForDB_riparianBufferDetailed200ft_05 zonalStatsForDB_riparianBufferDetailed200ft_06
do 
	# Define the file name
	FILENAME=$FOLDER/$TABLE.csv

	# Import the data from the CSV
	echo Importing covariates data for $TABLE table...
	psql -v ON_ERROR_STOP=1 -1 -d $DB -c "\COPY data.covariates FROM '$FILENAME' DELIMITER ',' CSV HEADER NULL AS 'NA';" || { echo "Failed to import covariates csv file"; exit 1; }

done

# Update internal query statistics and reclaim unused space in the table pages
echo Cleaning up...
psql -d $DB -c "VACUUM ANALYZE;"
