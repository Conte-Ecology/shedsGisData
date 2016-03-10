
-- This script is inclomplete. The snapping works to within <1m of the flowlines,
--   but does not snap exactly. This may be resolved with a small buffer around
--   points, but the script also seems to be too computationally intensive.


--================================================================================
--                          CURRENT WORKING SECTION
--================================================================================

-- Small Test Inputs:
-- ==================
-- locations: locations_imp 
-- flowlines: gis.select_lines


-- Full Test Inputs:
-- =================
-- locations: public.locations_test 
-- flowlines: gis.detailed_flowlines



SELECT * INTO TEMPORARY locations_temp FROM public.locations;
ALTER TABLE locations_temp ADD COLUMN geom geometry(POINT,4326);
UPDATE locations_temp SET geom = ST_SetSRID(ST_MakePoint(longitude,latitude),4326);
CREATE INDEX idx_loc_dum_geom ON locations_temp USING GIST(geom);

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
        FROM gis.detailed_flowlines, locations_temp 
        WHERE ST_Intersects(ST_Buffer(locations_temp.geom::geography, 75), gis.detailed_flowlines.geom::geography)
      )
	) as monkey
  ) as dumped
) AS simple;
--output table: gis.select_lines






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
  
  
  
  
  
  
--DROP TABLE gis.snapped_locations;
--DROP TABLE gis.select_lines;
  
  
  
  

-- Points are off slightly off of the line (<1m). Can do a small, 1-2 m buffer around snapped points
--   to get this to work


   
-- ========================================================
-- ========================================================
-- ========================================================  
--             CHUNKS OF CODE IN PROGRESS
-- ========================================================
-- ========================================================
-- ========================================================
   
   
   
   
   
   
   

-- =============================
-- Construction of snapping tool
-- =============================
   
-- Selects flowlines within a distance of the locations. These are then used for snapping (cuts down on computation).
SELECT * 
FROM imp_flowlines_test
WHERE featureid IN (
  SELECT DISTINCT featureid 
  FROM imp_flowlines_test, locations_imp 
  WHERE ST_Intersects(ST_Buffer(locations_imp.geom::geography, 250), imp_flowlines_test.geom::geography)
);

-- Convert to linestring from multilinestring

-- 1. return the set of geometry rows that make up a geometry
-- 2. split apart the geometry and it's position in the complex geometry (e.g. multilinestring)
-- 3. Create multiple rows from the multiple pieces of the multilinestring
SELECT
  COALESCE((simple.featureid || '.' || simple.path[1]::text)::float, simple.featureid) as id, -- concatenate the featureid and the path (keeps multiple geoms assigned to original featureid)
  simple.simple_geom as geom, -- simplified geom
  ST_GeometryType(simple.simple_geom) as geom_type, --simplified geom type
  ST_AsEWKT(simple.simple_geom) as geom_wkt  -- Well-known text representation of the geometry with SRID meta data
  INTO complex
FROM (
  SELECT
    dumped.*, -- all rows
    (dumped.geom_dump).geom as simple_geom, -- the geometry
    (dumped.geom_dump).path as path -- the position of the geometry inside the collection
  FROM (
    SELECT *, ST_Dump(geom) AS geom_dump FROM imp_flowlines_test -- returns the rows that make up the geometry: imp_flowlines_test.geom
  ) as dumped
) AS simple;







   

   
   
   
   


-- 1. Snap point to high res flowlines
-- 2. Intersect snapped points with impounded areas


SELECT 
   DISTINCT ON (pt_id) 
   pt_id, 
   ln_id, 
   ST_AsText(
     ST_line_interpolate_point(
       ln_geom, 
       ST_line_locate_point(ln_geom, vgeom)
     )
   ) 
 FROM
   (
   SELECT 
     ln.the_geom AS ln_geom, 
     pt.the_geom AS pt_geom, 
     ln.id AS ln_id, 
     pt.id AS pt_id, 
     ST_Distance(ln.the_geom, pt.the_geom) AS d 
   FROM 
     point_table pt, 
     line_table ln 
   WHERE 
     ST_DWithin(pt.the_geom, ln.the_geom, 10.0) 
   ORDER BY
     pt_id,d
   ) AS subquery;
   
   
   
   
   
   
 -- For SHEDS:
 
-- Test Locations
psql -d sheds_new -c "CREATE TABLE data.locations_imp(
                        fid int,
                        id int,
                        latitude real,
                        longitude real
                     );"
 
cd /home/kyle/scripts/db/locations_dummy
./import_locations_imp.sh sheds_new /home/kyle/data/locations_dummy/imp_zone_test_pts.csv	
 
 
-- Test Flowlines (smaller size)
psql -d sheds_new -c "CREATE TABLE gis.imp_flowlines_test(
                        featureid bigint,
						objectid bigint,
                        shape_leng real,
                        lengthkm real,
                        geom geometry NOT NULL
                     );"

--Upload spatial layer
cd /home/kyle/scripts/db/gis/impoundment_zones
./import_detailed_flowlines_imp.sh sheds_new /home/kyle/data/imp_zone
 
 
 
 
 
--Impoundment intersecting
 
 
psql -d sheds_new -c "ALTER TABLE data.locations_imp ADD COLUMN geom geometry(POINT,4326);"
psql -d sheds_new -c "UPDATE data.locations_imp SET geom = ST_SetSRID(ST_MakePoint(longitude,latitude),4326);"
psql -d sheds_new -c "CREATE INDEX idx_loc_imp_geom ON data.locations_imp USING GIST(geom);"
 
 
 -- rename: point_table = locations
 -- rename: line_table = detailed_flowlines

psql -d sheds_new -c "SELECT description, latitude, longitude
						FROM locations_dummy, tidal_zones
						WHERE ST_Intersects(locations_dummy.geom, tidal_zones.geom);"

 
SELECT id, latitude, longitude
   FROM locations_imp, imp_flowlines_test
   WHERE ST_AsText(
          ST_line_locate_point(imp_flowlines_test.geom, locations_imp.geom)
		  );
 
 
SELECT ST_AsText(ST_Line_Interpolate_Point(foo.the_line, ST_Line_Locate_Point(foo.the_line, ST_GeomFromText('POINT(4 3)'))))
FROM (SELECT ST_GeomFromText('LINESTRING(1 2, 4 5, 6 7)') As the_line) As foo; 
 
SELECT ST_AsText(ST_Line_Interpolate_Point(imp_flowlines_test.geom, ST_Line_Locate_Point(gis.imp_flowlines_test.geom, locations_imp.geom)))
FROM imp_flowlines_test, locations_imp;

-- imp_flowlines_test.geom isn't a line




-- imp_flowlines_test = detailed flowlines
-- impoundment_zones = the impounded zone range (100m)
-- locations_imp = location points

SELECT ST_GeometryType(complex.geom) FROM complex;


SELECT ST_AsText((imp_flowlines_test.geom))
  FROM imp_flowlines_test
  WHERE featureid = 201482211;

SELECT ST_AsText((imp_flowlines_test.geom))
  FROM imp_flowlines_test;
  
  
  
  
 
-- Select nearest line, or line within a buffer distance
SELECT name,ref,type,ST_Distance(ST_Buffer(r.geom,20),ST_SetSRID(ST_MakePoint(lon, lat),4326)) 
FROM roads r 
ORDER BY 4 ASC 
LIMIT 1;
 
SELECT featureid,ST_Distance(ST_Buffer(locations_imp.geom::geography, 10),imp_flowlines_test.geom::geography)
FROM imp_flowlines_test, locations_imp 
ORDER BY 2 ASC;
LIMIT 1;

SELECT featureid, ST_Distance(locations_imp.geom::geography, imp_flowlines_test.geom::geography)
FROM imp_flowlines_test, locations_imp 
ORDER BY 2 ASC;
LIMIT 1;


ST_Intersects(geometry A, geometry B)




-- Basic selection of points downstream of dams
SELECT DISTINCT id, uniqueid 
FROM impoundment_zones, locations_imp
WHERE ST_Intersects(ST_Buffer(impoundment_zones.geom::geography, 50), locations_imp.geom::geography);







-- Selects flowlines within a distance of the locations. These are then used for snapping (cuts down on computation).


SELECT * FROM imp_flowlines_test

SELECT *
FROM imp_flowlines_test, locations_imp
WHERE ST_Intersects(ST_Buffer(locations_imp.geom::geography, 250), imp_flowlines_test.geom::geography);

   
   
   
   
   
   
   