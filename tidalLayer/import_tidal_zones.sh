#!/bin/bash
# Imports tidal zone shapefile to table gis.tidal_zones
# converts to WGS84 first, if necessary

# usage: $ ./import_tidal_zones.sh <db name> <path to tidal zones directory>
# example: $ ./import_tidal_zones.sh conte_dev /conte/data/gis/tidal_zones


set -eu

DB=$1
WD=$2

TABLE=gis.tidal_zones

# Define files
FILE=$WD/tidalZones.shp
FILE_WGS=$WD/tidalZones_wgs84.shp

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
