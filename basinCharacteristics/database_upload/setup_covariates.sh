#!/bin/bash
# creates covariate table schema in database
# csv file created from RData file from conte-web-app/web/r/catchments_zonal_stats.R

# usage: $ ./setup_covariates.sh <db name>

set -eu
set -o pipefail

DB=$1

echo Creating covariates table schema...
psql -v ON_ERROR_STOP=1 -1 -d $DB -f table_covariates.sql -q || { echo "Failed to create data.covariates table"; exit 1; }
