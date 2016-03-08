#!/bin/bash
# creates a csv identifying tidally influenced sites
# csv file is named "tidal_sites.csv" and the header is "id"

# usage: $ ./id_tidal_sites.sh <db name> <path to output directory>
# example: $ ./id_tidal_sites.sh sheds_new /conte/data/qaqc

set -eu
set -o pipefail

# Set variables
DB=$1
FOLDER=$2

#
echo Identifying tidally influenced sites...

# Link to postgres
# Create a temporary table for creating an indexed geometry column
# Find the sites that intersect the tidal layer and write to csv
psql -d $DB -c "
SELECT * INTO TEMPORARY locations_temp FROM public.locations;
ALTER TABLE locations_temp ADD COLUMN geom geometry(POINT,4326);
UPDATE locations_temp SET geom = ST_SetSRID(ST_MakePoint(longitude,latitude),4326);
CREATE INDEX idx_loc_dum_geom ON locations_temp USING GIST(geom);

COPY (
  SELECT locations_temp.id
  FROM locations_temp, tidal_zones
  WHERE ST_Intersects(locations_temp.geom, tidal_zones.geom)
) TO STDOUT WITH CSV HEADER " > $FOLDER/tidal_sites.csv
