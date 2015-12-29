import arcpy
from arcpy import env
from arcpy.sa import *

# ==============
# Specify inputs
# ==============

baseDirectory = "C:/KPONEIL/GitHub/projects/basinCharacteristics/soilDrainageClass"
states        = ["MA", "CT", "RI", "ME", "NH", "VT", "NY", "DE", "MD", "NJ", "PA", "VA", "WV", "DC", "NC", "TN", "KY", "OH"]
sourceFolder  = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/land/nrcsSSURGO/spatial"
outputName    = "NHDHRDV2"

# ===========
# Folder prep
# ===========

# Create general folders if they don't exist
# ------------------------------------------
# Set the main GIS directory. Create one if it doesn't exist.
main_directory = baseDirectory + "/gisFiles"
if not arcpy.Exists(main_directory): arcpy.CreateFolder_management(baseDirectory, 
                                                                   "gisFiles")

# Create run specific folders if they don't exist
# -----------------------------------------------
# Set the run-specific sub-folder. Create one if it doesn't exist.
working_directory = main_directory + "/" + outputName
if not arcpy.Exists(working_directory): arcpy.CreateFolder_management(main_directory, 
                                                                      outputName)

# Set the run-specific table database. Create one if it doesn't exist.
tableDB = working_directory + "/tables.gdb"
if not arcpy.Exists(tableDB): arcpy.CreateFileGDB_management (working_directory, 
                                                              "tables", 
															  "CURRENT")

# Set the run-specific vector database. Create one if it doesn't exist.
vectorDB = working_directory + "/vectors.gdb"
if not arcpy.Exists(vectorDB): arcpy.CreateFileGDB_management (working_directory, 
                                                               "vectors", 
															   "CURRENT")

## Set the run-specific raster folder. Create one if it doesn't exist.
rasterFolder = working_directory + "/rasters"
if not arcpy.Exists(rasterFolder): arcpy.CreateFolder_management(working_directory, 
                                                                 "rasters")

## Set the run-specific output folder. Create one if it doesn't exist.
outputFolder = working_directory + "/outputFiles"
if not arcpy.Exists(outputFolder): arcpy.CreateFolder_management(working_directory, 
                                                                 "outputFiles")


# Name the map and dataframe for removing layers
# ----------------------------------------------
mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd)[0]


# ========================
# Create the state rasters
# ========================
# Loop through states
for i in range(len(states)): 

	# Copy the Mapunit polygon to the current directory for editing
	mupolyTable = sourceFolder + "/" + "gssurgo_g_" + states[i] + ".gdb/MUPOLYGON"
	arcpy.FeatureClassToFeatureClass_conversion(mupolyTable, 
												vectorDB, 
												"MUPOLYGON_" + states[i])


	# Join "component" table to the polygon
	# -------------------------------------
	# Add table to map
	componenetTable = sourceFolder + "/" + "gssurgo_g_" + states[i] + ".gdb/component"
	addTable = arcpy.mapping.TableView(componentTable)
		
	# Export raw tables to new tables
	arcpy.TableToTable_conversion(addTable, tableDB, "component_" + states[i])
		
	# Join tables to polygon
	arcpy.AddJoin_management("MUPOLYGON_" + states[i], "mukey", 
	                         "component" + "_" + states[i], 
							 "mukey")

	
	# Generate state rasters
	# ----------------------
	# Convert the state polygon to a raster
	arcpy.PolygonToRaster_conversion("MUPOLYGON_" + states[i], 
											"component_" + states[i] + ".drainagecl", 
											rasterFolder + "/TempDC_" + states[i], 
											"MAXIMUM_COMBINED_AREA", 
											"NONE", 
											30)
												
	# Reclassify the raster by Drainage Class
	outReclassify = Reclassify(rasterFolder + "/TempDC_" + states[i], 
								"component_" + states[i] + ".dra", 
								"'Excessively drained' 1; 'Somewhat excessively drained' 2; 'Well drained' 3; 'Moderately well drained' 4; 'Somewhat poorly drained' 5; 'Poorly drained' 6; 'Very poorly drained' 7", 
								"NODATA")				
								
	# Save the output 
	outReclassify.save(rasterFolder + "/DrnCls_" + states[i])
	
	# Remove some layers from the map
	# -------------------------------
	arcpy.mapping.RemoveLayer(df, 
	                          arcpy.mapping.ListLayers(mxd, 
							                           "TempDC_" + states[i], 
													   df)[0] 
							  )
	arcpy.mapping.RemoveLayer(df, 
	                          arcpy.mapping.ListLayers(mxd, 
							                           "MUPOLYGON_"  + states[i], 
													   df)[0] 
							  )


# ==================										
# Mosaic the rasters
# ==================										
# Generate the list of rasters to mosaic
mosaicList = []
for s in range(len(states)): 
	mosaicList.append(rasterFolder + "/DrnCls_" + states[s])
del s

# Run the mosaic tool over all state rasters
arcpy.MosaicToNewRaster_management(mosaicList,
									outputFolder, 
									"drainageclass",
									"#",
									"8_BIT_UNSIGNED", 
									30, 
									1, 
									"MAXIMUM",
									"FIRST")