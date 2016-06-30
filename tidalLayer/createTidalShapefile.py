import arcpy
from arcpy import env

# ==============
# Specify inputs
# ==============
baseDirectory = "C:/KPONEIL/SHEDS/tidalFilter"
states = ["ME", "NH", "MA", "RI", "CT", "NY", "NJ", "PA", "DE", "MD", "VA", "NC"]
wetlandsFolder = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/land/fwsWetlands/rawData/"
grid = "C:/KPONEIL/SHEDS/tidalFilter/source.gdb/grid_albers"


# ================
# Define functions
# ================
# Define function to delete all fields except the ones specified
def deleteExtraFields(layer, fieldsToKeep):
	fields = arcpy.ListFields(layer) 
	dropFields = [x.name for x in fields if x.name not in fieldsToKeep]
	arcpy.DeleteField_management(layer, dropFields)


# ==================
# Create tidal layer
# ==================
working_db = baseDirectory + "/processingFiles.gdb"
if not arcpy.Exists(working_db): arcpy.CreateFileGDB_management (baseDirectory, "processingFiles", "CURRENT")

# Create list of rasters to be mosaicked
tidalZones = []
	
# Loop through the states
for s in range(len(states)):

	# Create layer of just the tidal polygons
	arcpy.FeatureClassToFeatureClass_conversion (wetlandsFolder + "/" + states[s] + "_wetlands.gdb/" + states[s] + "_Wetlands",
																working_db,
																"tidal_" + states[s],
																""" ATTRIBUTE LIKE 'M%' OR 
																	ATTRIBUTE LIKE 'E%' OR 
																	ATTRIBUTE LIKE 'R1%' OR 
																	ATTRIBUTE LIKE 'L%Q%' OR
																	ATTRIBUTE LIKE 'L%T%' OR
																	ATTRIBUTE LIKE 'L%V%' OR
																	(ATTRIBUTE NOT LIKE '%/%' AND ATTRIBUTE LIKE 'L2__%R%') OR 
																	ATTRIBUTE LIKE 'L2%/__%R%' OR
																	ATTRIBUTE LIKE 'P%T%' OR 
																	ATTRIBUTE LIKE 'P%V%' OR 
																	(ATTRIBUTE NOT LIKE '%/%' AND ATTRIBUTE LIKE 'P__%R%') OR 
																	(ATTRIBUTE NOT LIKE '%/%' AND ATTRIBUTE LIKE 'P__%S%') OR
																	ATTRIBUTE LIKE 'P%/__%R%' OR 
																	ATTRIBUTE LIKE 'P%/__%S%' """)
	
	# Append the state tidal layer to list for further processing
	tidalZones.append(working_db + "/tidal_" + states[s])													
						
# Join the state polygons into one layer
mergedPolygons = arcpy.Merge_management(tidalZones, 
										working_db + "/tidal_All")
									

# Dissolve the layer									
dissolvedPolygons = arcpy.Dissolve_management(mergedPolygons, 
												working_db + "/tidalZonesAutomated",
												"", "", 
												"SINGLE_PART", 
												"")
							
# Divide the polygons into a manageable sizes 
tiledZones = arcpy.Intersect_analysis([dissolvedPolygons, grid],
										 baseDirectory + "tidalZonesTiled.shp",
										 "ONLY_FID",
										 "#",
										 "INPUT")
							
# Add an ID field
arcpy.AddField_management(tiledZones, "Id", "LONG")
arcpy.CalculateField_management(tiledZones, "Id", "[FID] + 1", "PYTHON_9.3")	

# Delete extra fields				
deleteExtraFields(tiledZones, 
				  ["FID", "Shape", "Id"])							
							
		

