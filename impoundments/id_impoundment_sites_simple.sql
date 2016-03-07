


-- Select & simplify flowlines for snapping
-- ========================================
-- Combination of the above 2
-- This is currently working:
--   It selects the flowlines near (within 75m) of a location point
--   simplifies the flowlines from multilinestring to linestring
SELECT
  COALESCE(simple.featureid || '.' || simple.path[1]::text, simple.featureid::text) as id, -- concatenate the featureid and the path (keeps multiple geoms assigned to original featureid)
  simple.simple_geom as geom, -- simplified geom
  ST_GeometryType(simple.simple_geom) as geom_type, --simplified geom type
  ST_AsEWKT(simple.simple_geom) as geom_wkt  -- Well-known text representation of the geometry with SRID meta data
  INTO gis.select_lines  -- OUTPUT
FROM (
  SELECT
    dumped.*, -- all rows
    (dumped.geom_dump).geom as simple_geom, -- the geometry
    (dumped.geom_dump).path as path -- the position of the geometry inside the collection
  FROM (
    SELECT *, ST_Dump(geom) AS geom_dump 
	FROM (
	  SELECT * 
      FROM gis.detailed_flowlines
      WHERE featureid IN (
        SELECT DISTINCT featureid 
        FROM gis.detailed_flowlines, data.locations_imp 
        WHERE ST_Intersects(ST_Buffer(data.locations_temp.geom::geography, 75), gis.detailed_flowlines.geom::geography)
      )
	) as monkey
  ) as dumped
) AS simple;
--output table: gis.select_lines


SELECT DISTINCT featureid 
    FROM gis.detailed_flowlines, data.locations_imp 
    WHERE ST_Intersects(ST_Buffer(data.locations_temp.geom::geography, 75), gis.detailed_flowlines.geom::geography)























-- =================================================
-- =================================================
-- =================================================
-- test intersecting points with detailed_flowines
-- =================================================
-- =================================================
-- =================================================

SELECT * INTO TEMPORARY locations_temp FROM public.locations;
ALTER TABLE locations_temp ADD COLUMN geom geometry(POINT,4326);
UPDATE locations_temp SET geom = ST_SetSRID(ST_MakePoint(longitude,latitude),4326);
CREATE INDEX idx_loc_dum_geom ON locations_temp USING GIST(geom);



SELECT * 
     FROM gis.detailed_flowlines
     WHERE featureid IN (
        SELECT DISTINCT featureid 
        FROM gis.detailed_flowlines, locations_temp 
        WHERE ST_Intersects(ST_Buffer(locations_temp.geom::geography, 75), gis.detailed_flowlines.geom::geography)
      )












-- SNAP POINTS TO A LINE
-- =====================
SELECT 
   DISTINCT ON (pt_id) 
   pt_id, 
   ln_id, 
   ST_AsText(
     ST_line_interpolate_point(
       ln_geom, 
       ST_line_locate_point(ln_geom, pt_geom) 
     )
   ) 
   INTO gis.snapped_locations
 FROM
   (
   SELECT 
     ln.geom AS ln_geom, 
     pt.geom AS pt_geom, 
     ln.id AS ln_id, 
     pt.id AS pt_id, 
     ST_Distance(ln.geom, pt.geom) AS d 
   FROM 
     locations_temp pt, 
     gis.select_lines ln 
   WHERE 
     ST_DWithin(pt.geom::geography, ln.geom::geography, 50.0) 
   ORDER BY
     pt_id,d
   ) AS subquery;
   

-- Add geometry
ALTER TABLE gis.snapped_locations ADD COLUMN geom geometry(POINT,4326);
UPDATE gis.snapped_locations SET geom = ST_SetSRID(ST_GeomFromText(st_astext),4326);
CREATE INDEX idx_snap_loc_geom ON gis.snapped_locations USING GIST(geom);   
   
-- Select points near impoundment zones
SELECT pt_id, ln_id INTO testPoints
  FROM gis.snapped_locations, gis.impoundment_zones_100m
  WHERE ST_Intersects(ST_Buffer(snapped_locations.geom::geography, 1)  , impoundment_zones_100m.geom);