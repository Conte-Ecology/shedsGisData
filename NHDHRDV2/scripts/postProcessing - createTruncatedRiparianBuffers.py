# =============
# Define Inputs
# =============
# Parent project directory
baseDirectory = "C:/KPONEIL/HRD/V2"

# List all hydro regions processed
hydroRegions = ['04', '05', '02', '01']

# List buffer distances
bufferDistancesFT = ['50', '100', '200']


# ===========
# Directories
# ===========
# Product database
hydrography_db = baseDirectory + "/products/hydrography.gdb"

# Interim file database
workspace_db = baseDirectory + "/gisFiles/postProcessing/workspace.gdb"

# Arc Hydro vectors geodatabase
riparian_db = baseDirectory + "/products/riparianBuffers.gdb"
if not arcpy.Exists(riparian_db): arcpy.CreateFileGDB_management (baseDirectory + "/products", "riparianBuffers", "CURRENT")


# ===================
# Truncated Flowlines
# ===================
# Loop through hydro regions
for region in hydroRegions:

	flowlines = hydrography_db + "/Flowlines" + region
		
	catchments = hydrography_db + "/Catchments" + region
	
	# Loop through buffers
	for buffer in bufferDistancesFT:

		# Create raw buffer
		truncBuffer = arcpy.Buffer_analysis(flowlines, 
												workspace_db + "/truncatedBuffer" + buffer + "ft_" + region, 
												buffer, 
												"FULL", 
												"ROUND", 
												"NONE")
		
		# Assign buffers to catchments
		intersect = arcpy.Intersect_analysis ([truncBuffer, catchments], 
												workspace_db + "/truncatedCatBufIntersect" + buffer + "ft_" + region, 
												"ALL", 
												"", "")
		
		# Select only buffers that pair to the correct catchment
		selection = arcpy.FeatureClassToFeatureClass_conversion(intersect, 
																	workspace_db, 
																	"truncatedIntersectSelect" + buffer + "ft_" + region,
																	"""FEATUREID = FEATUREID_1""")
		
		# Finalize buffer layer
		truncatedFinal = arcpy.Dissolve_management(selection,
														riparian_db + "/riparianBuffer" + buffer + "ft_" + region,
														"FEATUREID", 
														"#",
														"MULTI_PART",
														"DISSOLVE_LINES")
		
		# Add field for area in square kilometers
		arcpy.AddField_management(truncatedFinal, 
								"AreaSqKM", 
								"DOUBLE")
								
		arcpy.CalculateField_management(truncatedFinal, 
										"AreaSqKM", 
										"!SHAPE.AREA@SQUAREKILOMETERS!", 
										"PYTHON")
																									
											
											