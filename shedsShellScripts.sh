
# Upload Shell commands


# Create a dummy database with same template as "sheds_new"
psql -c "CREATE DATABASE practice WITH TEMPLATE sheds_new OWNER kyle;"



# =============
# Table Updates
# =============




# Covariates
# ----------

psql -d sheds_new -c "ALTER TABLE data.covariates ADD COLUMN riparian_distance_ft int"
psql -d sheds_new -c "ALTER TABLE data.covariates DROP CONSTRAINT featureid_variable_zone_key;"
psql -d sheds_new -c "ALTER TABLE data.covariates ADD CONSTRAINT featureid_variable_zone_riparian_key UNIQUE (featureid, variable, zone, riparian_distance_ft);"



# =======
# Uploads
# =======


# Catchments 
# ----------
cd /home/kyle/scripts/db/gis/catchments
./import_catchments.sh sheds_new /home/kyle/data/gis/catchments

# Covariates
# ----------
cd /home/kyle/scripts/db/covariates
./import_covariates.sh sheds_new /home/kyle/data/covariates/20151123





# Daymet upload
# -------------
cd /home/kyle/scripts/db/daymet
./import_daymet.sh practice /home/kyle/data/daymet






# Detailed flowlines upload
# -------------------------
cd /home/kyle/scripts/db/gis/hrd_flowlines
./import_hrdflowlines.sh practice /home/kyle/data/gis/hrd_detailed_flowlines

psql -c "CREATE DATABASE lines WITH TEMPLATE sheds_new OWNER kyle;"
psql -c "CREATE DATABASE covars WITH TEMPLATE lines OWNER kyle;"

