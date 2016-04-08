#!/bin/bash
# Import high resolution "detailed flowlines" shapefile to gis.detailed_flowlines
# converts to WGS84 first, if necessary

# usage: ./import_detailed_flowlines.sh <db name> <path to detailed flowlines directory>
# example: ./import_detailed_flowlines.sh conte_dev /conte/data/gis/detailed_flowlines

set -eu

DB=$1
WD=$2

TABLE=gis.detailed_flowlines
WGS=_wgs84.shp

# Loop through flowline layers
for LAYER in detailedFlowlines01 detailedFlowlines02 detailedFlowlines03 detailedFlowlines04 detailedFlowlines05 detailedFlowlines06 
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
psql -d $DB -c "CREATE INDEX detailed_flowlines_geom_gist ON $TABLE USING gist(geom);"

# Update internal query statistics and reclaim unused space in the table pages
echo Cleaning up...
psql -d $DB -c "VACUUM ANALYZE;"
