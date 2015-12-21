# ==============
# Specify Inputs
# ==============

# Directory to write to
baseDirectory = "C:/KPONEIL/SHEDS/impoundments"

# NHDHRDV2 hydrologic regions
hydroRegions = ["01", "02", "03", "04", "05", "06"]

# Length downstream from impoundments to identify (in meters)
zoneDistM = 50


# ======================
# XXXXXXXXXXXXXXXXXXXXXX
# ======================

# Create version geodatabase
networkDirectory = baseDirectory + "/network" + str(zoneDistM) + "m.gdb"
if not arcpy.Exists(networkDirectory): arcpy.CreateFileGDB_management (baseDirectory, "network" + str(zoneDistM) + "m", "CURRENT")

catchmentDirectory = baseDirectory + "/catchmentProcessing" + str(zoneDistM) + "m.gdb"
if not arcpy.Exists(catchmentDirectory): arcpy.CreateFileGDB_management (baseDirectory, "catchmentProcessing" + str(zoneDistM) + "m", "CURRENT")

# Full path to the impoundments layer
impoundments = networkDirectory + "/impoundments"


impoundedZones = baseDirectory + "/impoundedZones" + str(zoneDistM) + "m.shp"




tablesToMerge = []


for region in hydroRegions:

	catchments = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/streamStructure/NHDHRDV2/products/hydrography.gdb/catchments" + region
	arcpy.MakeFeatureLayer_management(catchments, "catchments_lyr")



	arcpy.SelectLayerByLocation_management ("catchments_lyr",
												"CROSSED_BY_THE_OUTLINE_OF",
												impoundedZones,
												"", 
												"NEW_SELECTION")


	arcpy.SelectLayerByLocation_management ("catchments_lyr",
												"INTERSECT",
												impoundments,
												"",
												"SUBSET_SELECTION")

	arcpy.TableToTable_conversion("catchments_lyr", 
									catchmentDirectory, 
									"pourPoints_" +  region)											

	tablesToMerge.append(catchmentDirectory + "/pourPoints_" +  region)										