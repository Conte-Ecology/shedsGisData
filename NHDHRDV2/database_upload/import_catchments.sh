#!/bin/bash
# imports catchments shapefile to table gis.catchments
# converts to WGS84 first, if necessary

# usage: $ ./import_catchments.sh <db name> <path to catchments folder>
# example: $ ./import_catchments.sh conte_dev /conte/data/gis/catchments

set -eu

DB=$1
WD=$2

TABLE=gis.catchments
WGS=_wgs84.shp

# Convert column types to big integer so they can handle the type "double" values from the shapefiles
psql -d $DB -c "ALTER TABLE gis.catchments ALTER COLUMN featureid TYPE BIGINT;"
psql -d $DB -c "ALTER TABLE gis.catchments ALTER COLUMN nextdownid TYPE BIGINT;"

# Loop through catchment layers to upload
for LAYER in Catchments01 Catchments02 Catchments03 Catchments04 Catchments05 Catchments06
do
	# Define files
	FILE=$WD/$LAYER.shp
	FILE_WGS=$WD/$LAYER$WGS

	# Check that input shapefile exists
	if [ ! -e $FILE ]; then
	  echo Could not find input shapefile: $FILE
	  exit 1
	fi

	# convert shapefile from EPSG:5070 (NAD83 Albers) to EPSG:4326
	if [ ! -e $FILE_WGS ]; then
	  echo Converting $FILE to WGS84
	  ogr2ogr -f "ESRI Shapefile" $FILE_WGS $FILE -s_srs EPSG:5070 -t_srs EPSG:4326 -fieldTypeToString real
	else
	  echo WGS84 file already exists: $FILE_WGS
	fi

	# Dump transformed shapefile into database
	echo Importing $FILE_WGS layer to database $DB...
	shp2pgsql -s 4326:4326 -g geom -a -t 2D $FILE_WGS $TABLE | psql -d $DB -q
done

# Create spatial index
psql -d $DB -c "CREATE INDEX catchments_geom_gist ON gis.catchments USING gist(geom);"

# Update internal query statistics and reclaim unused space in the table pages
echo Cleaning up...
psql -d $DB -c "VACUUM ANALYZE;"
