import arcpy
from arcpy import env
from arcpy.sa import *

# ==============
# Specify inputs
# ==============
baseDirectory  = "C:/KPONEIL/GitHub/projects/basinCharacteristics/fwsWetlands"
states         = ["MA", "CT", "RI", "ME", "NH", "VT", "NY", "DE", "MD", "NJ", "PA", "VA", "WV", "OH", "KY", "TN", "NC"]
stateNames     = ["District of Columbia", "Massachusetts", "Connecticut", "Rhode Island", "Maine", "New Hampshire", "Vermont", "New York", "Delaware", "Maryland", "New Jersey", "Pennsylvania", "Virginia", "West Virginia", "Ohio", "Kentucky", "Tennessee", "North Carolina"]
wetlandsFolder = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/land/fwsWetlands/rawData/"
statesFile     = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/political/states/States.shp"
outputName     = "NHDHRDV2"

# ===========
# Folder prep
# ===========

# Create general folders if they don't exist
# ------------------------------------------
# Set the main GIS directory. Create one if it doesn't exist.
main_directory = baseDirectory + "/gisFiles"
if not arcpy.Exists(main_directory): arcpy.CreateFolder_management(baseDirectory, "gisFiles")


# Create run specific folders if they don't exist
# -----------------------------------------------
# Set the run sub-folder. Create one if it doesn't exist.
working_directory = main_directory + "/" + outputName
if not arcpy.Exists(working_directory): arcpy.CreateFolder_management(main_directory, outputName)

# Set the run database. Create one if it doesn't exist.
working_db = working_directory + "/processingFiles.gdb"
if not arcpy.Exists(working_db): arcpy.CreateFileGDB_management (working_directory, "processingFiles", "CURRENT")

# Set the output folder. Create one if it doesn't exist.
output_folder = working_directory + "/outputFiles"
if not arcpy.Exists(output_folder): arcpy.CreateFolder_management(working_directory, "outputFiles")

# Set the run raster folder. Create one if it doesn't exist.
working_raster = working_directory + "/rasters"
if not arcpy.Exists(working_raster): arcpy.CreateFolder_management(working_directory, "rasters")

# Name the map and dataframe for removing layers
# ----------------------------------------------
mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd)[0]


# ===================
# Create Range Raster
# ===================
# Generates a blank raster of the entire range. This raster will serve as the template to which the state rasters will be mosaicked.

spatial_ref = arcpy.Describe(wetlandsFolder + "/" + states[1] + "_wetlands.gdb/" + states[1] + "_Wetlands").spatialReference

# Project the states file to match the wetlands			
arcpy.Project_management(statesFile, working_db + "/statesFilePrj", spatial_ref)

arcpy.Sort_management(working_db + "/statesFilePrj",
						working_db + "/statesSort",
						[["AREA", "DESCENDING"]])

arcpy.DeleteIdentical_management(working_db + "/statesSort", "STATE")

arcpy.management.MakeFeatureLayer(working_db + "/statesSort", "selectStates")
for sN in stateNames:
    query = """ "STATE" = '""" + sN +"""'"""
    arcpy.management.SelectLayerByAttribute("selectStates", "ADD_TO_SELECTION", query)																			
	
arcpy.FeatureClassToGeodatabase_conversion("selectStates", working_db)

arcpy.Dissolve_management(working_db + "/selectStates", working_db + "/WaterbodyRange","#", "#", "SINGLE_PART", "DISSOLVE_LINES")

# Calculate the field that determines the raster value
arcpy.AddField_management("WaterbodyRange", "rasterVal", "SHORT")
arcpy.CalculateField_management ("WaterbodyRange", "rasterVal", 0, "PYTHON_9.3")	


# Create template for the final raster
arcpy.PolygonToRaster_conversion("WaterbodyRange", 
										"rasterVal", 
										working_db + "/rangeRaster", 
										"MAXIMUM_COMBINED_AREA", 
										"NONE", 
										30)


arcpy.mapping.RemoveLayer(df, arcpy.mapping.ListLayers(mxd, "statesFilePrj", df)[0] )
arcpy.mapping.RemoveLayer(df, arcpy.mapping.ListLayers(mxd, "statesSort", df)[0] )
arcpy.mapping.RemoveLayer(df, arcpy.mapping.ListLayers(mxd, "selectStates", df)[0] )


# ======================
# Generate State Rasters
# ======================
for j in range(len(states)): 

	# Open Water Classification Processing
	# ------------------------------------
	# Select the "open water" classification
	arcpy.FeatureClassToFeatureClass_conversion (wetlandsFolder + "/" + states[j] + "_wetlands.gdb/" + states[j] + "_Wetlands", 
																		working_db, 
																		"openWater_" + states[j], 
																		""" "WETLAND_TYPE" = 'Estuarine and Marine Deepwater' OR
																			"WETLAND_TYPE" = 'Freshwater Pond' OR 
																			"WETLAND_TYPE" = 'Lake' """)

	# Calculate the field that determines the raster value
	arcpy.AddField_management("openWater_" + states[j], "rasterVal", "SHORT")
	arcpy.CalculateField_management ("openWater_" + states[j], "rasterVal", 1, "PYTHON_9.3")

	# Set processing extent for rasterization
	arcpy.env.extent = working_db + "/rangeRaster"

	# Rasterize the polygon
	arcpy.PolygonToRaster_conversion("openWater_" + states[j], 
										"rasterVal", 
										working_db + "/open_" + states[j],
										"MAXIMUM_COMBINED_AREA", 
										"NONE", 
										30)
										
	
	# Wetlands Classification Processing
	# ------------------------------------------
	# Select the "all wetlands" classification
	arcpy.FeatureClassToFeatureClass_conversion (wetlandsFolder + "/" + states[j] + "_wetlands.gdb/" + states[j] + "_Wetlands", 
																		working_db, 
																		"wetlands_" + states[j], 
																		""" "WETLAND_TYPE" = 'Estuarine and Marine Wetland' OR 
																			"WETLAND_TYPE" = 'Freshwater Emergent Wetland' OR 
																			"WETLAND_TYPE" = 'Freshwater Forested/Shrub Wetland' """)
	# Calculate the field that determines the raster value
	arcpy.AddField_management("wetlands_" + states[j], "rasterVal", "SHORT")
	arcpy.CalculateField_management ("wetlands_" + states[j], "rasterVal", 1, "PYTHON_9.3")

	# Set processing extent for rasterization
	arcpy.env.extent = working_db + "/rangeRaster"
	
	# Rasterize the polygon
	arcpy.PolygonToRaster_conversion("wetlands_" + states[j], 
										"rasterVal", 
										working_db + "/wet_" + states[j],
										"MAXIMUM_COMBINED_AREA", 
										"NONE", 
										30)

	# Remove some layers from the map
	# -------------------------------
	arcpy.mapping.RemoveLayer(df, arcpy.mapping.ListLayers(mxd, "openWater_" + states[j], df)[0] )
	arcpy.mapping.RemoveLayer(df, arcpy.mapping.ListLayers(mxd, "wetlands_"  + states[j], df)[0] )								
# End polygon processing loop


# ==================
# Mosaicking Rasters
# ==================

# Open Water
# ----------

# Create list of rasters to be mosaicked
openList = [working_db + "/rangeRaster"]
	
# Loop through states adding rasters to the list
for s in range(len(states)): 
	openList.append(working_db + "/open_" + states[s])
del s
	
# Set processing extent for rasterization
arcpy.env.extent = working_db + "/rangeRaster"
	
# Mosaic rasters
arcpy.MosaicToNewRaster_management(openList,
									working_raster, 
									"openWaterExt",
									working_db + "/rangeRaster",
									"8_BIT_UNSIGNED", 
									30, 
									1, 
									"MAXIMUM",
									"FIRST")
	
outExtractOpen = ExtractByMask(working_raster + "/openWaterExt", "WaterbodyRange")
outExtractOpen.save(output_folder + "/fwsOpenWater")

# Wetlands
# --------

# Create list of rasters to be mosaicked
wetList = [working_db + "/rangeRaster"]
	
# Loop through states adding rasters to the list
for s in range(len(states)): 
	wetList.append(working_db + "/wet_" + states[s])
del s
	
# Set processing extent for rasterization
arcpy.env.extent = working_db + "/rangeRaster"

# Mosaic rasters
arcpy.MosaicToNewRaster_management(wetList,
									working_raster, 
									"wetlandsExt",
									working_db + "/rangeRaster",
									"8_BIT_UNSIGNED", 
									30,
									1,
									"MAXIMUM",
									"FIRST")

outExtractWet = ExtractByMask(working_raster + "/wetlandsExt", "WaterbodyRange")
outExtractWet.save(output_folder + "/fwsWetlands")

