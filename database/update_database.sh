# ====================
# Edit Existing Tables
# ====================

# ----------
# Catchments
# ----------
# Upload spatial layers
cd /home/kyle/scripts/db/gis/catchments
./import_catchments.sh sheds_new /home/kyle/data/gis/catchments


# ----------
# Covariates
# ----------
# Add a column to indicate riparian zone and update the constraint
psql -d sheds_new -c "ALTER TABLE data.covariates ADD COLUMN riparian_distance_ft int"
psql -d sheds_new -c "ALTER TABLE data.covariates DROP CONSTRAINT featureid_variable_zone_key;"
psql -d sheds_new -c "ALTER TABLE data.covariates ADD CONSTRAINT featureid_variable_zone_riparian_key UNIQUE (featureid, variable, zone, riparian_distance_ft);"

# Upload tables
cd /home/kyle/scripts/db/covariates
./import_covariates.sh sheds_new /home/kyle/data/covariates/20151211


# ------
# Daymet
# ------
# Drop indexes for upload
psql -d sheds_new -c "DROP INDEX daymet_featureid_fkey;"
psql -d sheds_new -c "DROP INDEX daymet_featureid_year_idx;"

# Upload databases
cd /home/kyle/scripts/db/daymet
./import_daymet.sh sheds_new /home/kyle/data/daymet

# Re-create index after deleting it for upload
psql -d sheds_new -c "CREATE INDEX daymet_featureid_year_idx ON data.daymet USING btree (featureid, date_part('year'::text, date));"

# Add a constraint to ensure there are no duplicate entries
psql -d sheds_new -c "ALTER TABLE data.daymet ADD CONSTRAINT featureid_date_key UNIQUE (featureid, date);"



# ==========
# New Tables
# ==========

# ------------------
# Detailed flowlines
# ------------------
# Create table
psql -d sheds_new -c "CREATE TABLE gis.detailed_flowlines(
                        featureid bigint references gis.catchments(featureid),
                        shape_leng real,
                        lengthkm real,
                        geom geometry NOT NULL
                     );"

#Upload spatial layer
cd /home/kyle/scripts/db/gis/detailed_flowlines
./import_detailed_flowlines.sh sheds_new /home/kyle/data/gis/detailed_flowlines					 

# Create index on featureid
psql -d sheds_new -c "CREATE INDEX detailed_flowlines_featureid_idx ON gis.detailed_flowlines USING btree (featureid);"


# -------------------
# Truncated flowlines
# -------------------
# Create table
psql -d sheds_new -c "CREATE TABLE gis.truncated_flowlines(
						source varchar(20),
                        featureid bigint references gis.catchments(featureid),
                        nextdownid bigint,
                        shape_leng real,
                        lengthkm real,
                        geom geometry NOT NULL
                     );"

# Upload spatial layer
cd /home/kyle/scripts/db/gis/truncated_flowlines
./import_truncated_flowlines.sh sheds_new /home/kyle/data/gis/truncated_flowlines

# Create index on featureid
psql -d sheds_new -c "CREATE INDEX truncated_flowlines_featureid_idx ON gis.truncated_flowlines USING btree (featureid);"


# -----------
# Tidal Zones
# -----------					 
# Create table
psql -d sheds_new -c "CREATE TABLE gis.tidal_zones(
                        fid int ,
                        geom geometry NOT NULL,
						id int
                     );"

# Upload spatial layer
cd /home/kyle/scripts/db/gis/tidal_zones
./import_tidal_zones.sh sheds_new /home/kyle/data/gis/tidal_zones					 


# ---------------
# Impounded Zones
# ---------------
# Create table
psql -d sheds_new -c "CREATE TABLE gis.impoundment_zones_100m(
                        uniqueid int,
                        lengthm real,
                        zonedistm int,
                        geom geometry NOT NULL
                     );"

# Upload spatial layer				 
cd /home/kyle/scripts/db/gis/impoundment_zones					 
./import_impoundment_zones.sh sheds_new /home/kyle/data/gis/impoundment_zones




# =================
# Delete Old Tables
# =================

# This table is replaced with "gis.truncated_flowlines"
psql -d sheds_new -c "DROP TABLE gis.flowlines"

# This table is replaced with the "gis.detailed_flowlines"
psql -d sheds_new -c "DROP TABLE gis.hrd_flowlines"

# The featureid is now a column in the high res flowlines
psql -d sheds_new -c "DROP TABLE gis.hrd_flowlines_featureid"

		

		
		
		
		
# ===========
# For Testing
# ===========

# Create a dummy database with same template as "sheds_new"
psql -c "CREATE DATABASE practice WITH TEMPLATE sheds_new OWNER kyle;"
		
					
					
					
					
					
					