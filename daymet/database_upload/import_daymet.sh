#!/bin/bash
#usage: ./import_daymet.sh <db_name> <path to daymet folder>
#example: ./import_daymet.sh conte_dev /conte/data/daymet

set -eu

DB=$1
FOLDER=$2

# Change column type to accomodate longer FEATUREIDs
psql -d $DB -c "ALTER TABLE data.daymet ALTER COLUMN featureid TYPE BIGINT;"

# Loop through Daymet databases
for FILE in NHDHRDV2_01 NHDHRDV2_02 NHDHRDV2_03 NHDHRDV2_04 NHDHRDV2_05 NHDHRDV2_06
do
	DAYMET=$FOLDER/$FILE

	# Export
	echo Streaming data from sqlite to $DB for $DAYMET
	./export_sqlite.sh $DAYMET | psql -d $DB -c "COPY data.daymet FROM STDIN WITH CSV"
done

# Update internal query statistics and reclaim unused space in the table pages
echo Cleaning up...
psql -d $DB -c "VACUUM ANALYZE;"
