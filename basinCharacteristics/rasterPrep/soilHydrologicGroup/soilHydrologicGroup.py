import arcpy

# ==============
# Specify inputs
# ==============

baseDirectory = "C:/KPONEIL/GitHub/projects/basinCharacteristics/soilHydrologicGroup"
states = ["MA", "CT", "RI", "ME", "NH", "VT", "NY", "DE", "MD", "NJ", "PA", "VA", "WV", "DC", "NC", "TN", "KY", "OH"]
sourceFolder = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/land/nrcsSSURGO/spatial"
outputName = "NHDHRDV2"


# Define Hydrologic Group classifications (selection code in 1st column and name in 2nd column)
hydroGroups = [ [""" "hydro_grp" = 'A' """, 															 	  	 "a" ],
				[""" "hydro_grp" = 'A' OR "hydro_grp" = 'B' """, 											  	 "ab"],
				[""" "hydro_grp" = 'C' OR "hydro_grp" = 'D' OR "hydro_grp" = 'C/D' """, 					  	 "cd"],
				[""" "hydro_grp" = 'D' """, 															 	  	 "d1"],
				[""" "hydro_grp" = 'A/D' OR "hydro_grp" = 'B/D' OR "hydro_grp" = 'C/D' OR "hydro_grp" = 'D' """, "d4"] ]



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



# ===================
# Create Range Raster
# ===================

# Create a list of the state polygons
statePolyList = []
for k in range(len(states)):
	statePolyList.append(sourceFolder + "/" + "gssurgo_g_" + states[k] + ".gdb/SAPOLYGON")

# Merge state boundaries
arcpy.Merge_management(statePolyList, vectorDB + "/SoilsStates")

# Create regional outline
arcpy.Dissolve_management(vectorDB + "/SoilsStates", 
                          vectorDB + "/SoilsRange",
						  "#", 
						  "#", 
						  "SINGLE_PART", 
						  "DISSOLVE_LINES")

# Calculate the field that determines the raster value
arcpy.AddField_management("SoilsRange", "rasterVal", "SHORT")
arcpy.CalculateField_management ("SoilsRange", "rasterVal", 0, "PYTHON_9.3")	

# Create template for the final raster
arcpy.PolygonToRaster_conversion("SoilsRange", 
									"rasterVal", 
									rasterFolder + "/rangeRaster", 
									"MAXIMUM_COMBINED_AREA", 
									"NONE", 
									30)


										
# ========================
# Create the state rasters
# ========================
for i in range(len(states)): 

	# Copy the Mapunit polygon to the current directory for editing
	mupolyTable = sourceFolder + "/" + "gssurgo_g_" + states[i] + ".gdb/MUPOLYGON"
	arcpy.FeatureClassToFeatureClass_conversion(mupolyTable, 
												vectorDB, 
												"MUPOLYGON_" + states[i])

	# Add the field that will be taken from the tables
	arcpy.AddField_management("MUPOLYGON_" + states[i], 
								"hydro_grp", 
								"TEXT")


	# Join "component" table to the polygon
	# -------------------------------------
	# Add table to map
	componentTable = sourceFolder + "/" + "gssurgo_g_" + states[i] + ".gdb/component"
	addTable = arcpy.mapping.TableView(componentTable)
		
	#Export tables to new tables so the original tables don't get accidentally altered
	arcpy.TableToTable_conversion(addTable, tableDB, "component_" + states[i])
		
	# Join tables to polygon
	arcpy.AddJoin_management("MUPOLYGON_" + states[i], 
	                         "mukey", 
							 "component" + "_" + states[i], 
							 "mukey")

	
	# Generate polygon of desired classifications
	# -------------------------------------------
	# Calculate the texture field in the Mapunit polygon
	arcpy.CalculateField_management ("MUPOLYGON_" + states[i], 
	                                 "hydro_grp", 
									 "!hydgrp!", 
									 "PYTHON_9.3")	
	
	for j in range(len(hydroGroups)):
	
		# Select out the categories for Hydrologic Group classifications
		statePolyGrp = arcpy.FeatureClassToFeatureClass_conversion (vectorDB + "/MUPOLYGON_" + states[i], 
																	vectorDB, 
																	"hydgrp_" + hydroGroups[j][1] + "_" + states[i], 
																	hydroGroups[j][0])

		# Rasterize the state polygon
		# ---------------------------
		# Calculate the field that determines the raster value
		arcpy.AddField_management(statePolyGrp, "rasterVal", "SHORT")
		arcpy.CalculateField_management (statePolyGrp, "rasterVal", 1, "PYTHON_9.3")
					
		# Set the extent																			 
		arcpy.env.extent = rasterFolder + "/rangeRaster"

		# Convert to raster
		arcpy.PolygonToRaster_conversion(statePolyGrp, 
										"rasterVal", 
										rasterFolder + "/hydgrp_" + hydroGroups[j][1] + "_" + states[i], 
										"MAXIMUM_COMBINED_AREA", 
										"NONE", 
										30)
											
		# Remove grouped state polygon
		arcpy.mapping.RemoveLayer(df, 
		                          arcpy.mapping.ListLayers(mxd, 
								                           "hydgrp_" + hydroGroups[j][1] + "_" + states[i], 
								                            df)[0] 
								  )
	
	# Remove main state polygon
	arcpy.mapping.RemoveLayer(df, 
	                          arcpy.mapping.ListLayers(mxd, 
							                           "MUPOLYGON_"  + states[i], 
													   df)[0] 
							  )
# End state loop








# ==================										
# Mosaic the rasters
# ==================										

# Loop through each hydrologic group classification
# -------------------------------------------------
for m in range(len(hydroGroups)):

	mosaicList = [rasterFolder + "/rangeRaster"]
		
	for s in range(len(states)): 
		mosaicList.append(rasterFolder + "/hydgrp_" + hydroGroups[m][1] + "_" + states[s])
	del s
		
	# Set processing extent for rasterization
	arcpy.env.extent = rasterFolder + "/rangeRaster"
		
	arcpy.MosaicToNewRaster_management(mosaicList,
										outputFolder, 
										"hydrogroup_" + hydroGroups[m][1],
										rasterFolder + "/rangeRaster",
										"8_BIT_UNSIGNED", 
										30, 
										1, 
										"MAXIMUM",
										"FIRST")
