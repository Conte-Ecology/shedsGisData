#!/bin/bash
# Import Impoundment Zone Layer from Shapefile to PostGIS
# usage: ./import_detailed_flowlines.sh <dbname> <path/to/gis/dir>
# example: ./import_impoundment_zones.sh conte_dev /conte/data/gis/impoundment_zones

set -eu

DB=$1
WD=$2

TABLE=gis.impoundment_zones_100m

# Define files
FILE=$WD/impoundedZones100m.shp

FILE_WGS=$WD/impoundedZones100m_wgs84.shp

# Check that input shapefile exists
if [ ! -e $FILE ]; then
  echo Could not find input shapefile: $FILE
  exit 1
fi

# convert shapefile from EPSG:5070 (NAD83 Albers) to EPSG:4326
if [ ! -e $FILE_WGS ]; then
  echo Converting $FILE to WGS84
  ogr2ogr -f "ESRI Shapefile" $FILE_WGS $FILE -s_srs EPSG:5070 -t_srs EPSG:4326
else
    echo WGS84 file already exists: $FILE_WGS
fi

# Dump transformed shapefile into database
echo Importing $FILE_WGS layer to database $DB...
shp2pgsql -s 4326:4326 -g geom -I -a -t 2D $FILE_WGS $TABLE | psql -d $DB -q


# Update internal query statistics and reclaim unused space in the table pages
echo Cleaning up...
psql -d $DB -c "VACUUM ANALYZE;"
