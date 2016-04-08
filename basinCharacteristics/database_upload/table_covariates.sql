CREATE TABLE IF NOT EXISTS data.covariates(
  featureid INTEGER NOT NULL,
  variable varchar(40) NOT NULL,
  value REAL,
  zone varchar(40) NOT NULL
);

ALTER TABLE data.covariates
  ADD CONSTRAINT covariates_featureid_fkey FOREIGN KEY (featureid) REFERENCES gis.catchments (featureid);
CREATE INDEX fki_covariates_featureid_fkey ON covariates (featureid);
CREATE INDEX covariates_zone_idx ON covariates (zone);
