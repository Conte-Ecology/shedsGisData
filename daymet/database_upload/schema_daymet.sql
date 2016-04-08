CREATE SCHEMA IF NOT EXISTS data;

DROP TABLE IF EXISTS data.daymet;

CREATE TABLE data.daymet (
  featureid INTEGER,
  date DATE,
  tmax REAL,
  tmin REAL,
  prcp REAL,
  dayl REAL,
  srad REAL,
  vp REAL,
  swe REAL
);

