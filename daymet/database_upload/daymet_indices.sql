CREATE INDEX daymet_featureid_year_idx ON data.daymet(featureid, date_part('year'::text, date));
CREATE INDEX daymet_featureid_fkey ON data.daymet(featureid);

