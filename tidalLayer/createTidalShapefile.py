import arcpy
from arcpy import env

# ==============
# Specify inputs
# ==============
baseDirectory = "C:/KPONEIL/SHEDS/tidalFilter"
states = ["ME", "NH", "MA", "RI", "CT", "NY", "NJ", "PA", "DE", "MD", "VA", "NC"]
wetlandsFolder = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/land/fwsWetlands/rawData/"
statesFile = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/political/states/States.shp"


# Set the run database. Create one if it doesn't exist.
working_db = baseDirectory + "/processingFiles.gdb"
if not arcpy.Exists(working_db): arcpy.CreateFileGDB_management (baseDirectory, "processingFiles", "CURRENT")




# Create list of rasters to be mosaicked
tidalZones = []
	
for s in range(len(states)):
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
																	
	tidalZones.append(working_db + "/tidal_" + states[s])													
						

mergedPolygons = arcpy.Merge_management(tidalZones, 
										working_db + "/tidal_All")
						
						
arcpy.Dissolve_management(mergedPolygons, 
							baseDirectory + "/tidalZones.shp",
							"", "", 
							"SINGLE_PART", 
							"")	
							
arcpy.Dissolve_management(mergedPolygons, 
							baseDirectory + "/tidalZonesMulti.shp",
							"", "", 
							"MULTI_PART", 
							"")								