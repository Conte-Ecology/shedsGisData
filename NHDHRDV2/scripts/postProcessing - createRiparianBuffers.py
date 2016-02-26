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


# ==================
# Detailed Flowlines
# ==================
# Memory intensive procedures on large layers make this section relatively unstable. If an error occurs, try rerunning after a reboot.
for region in hydroRegions:

	detailedFlowlines = hydrography_db + "/detailedFlowlines" + region
		
	catchments = hydrography_db + "/Catchments" + region
	
	for buffer in bufferDistancesFT:
	
		# Create raw buffer
		detailedBuffer = arcpy.Buffer_analysis(detailedFlowlines, 
												workspace_db + "/detailedBuffer" + buffer + "ft_" + region, 
												buffer + " FEET", 
												"FULL", 
												"ROUND", 
												"NONE")
	
		# Prevent errors in the Union tool								
		arcpy.RepairGeometry_management (detailedBuffer)										
		arcpy.RepairGeometry_management (catchments)											
		
		# Assign buffers to catchments
		union = arcpy.Union_analysis([detailedBuffer, catchments], 
										workspace_db + "/detailedBufCatUnion" + buffer + "ft_" + region,
										"ALL",
										"#",
										"GAPS")
		
		# Select only buffers and ensure that they pair to the correct catchment																
		unionFinal = arcpy.FeatureClassToFeatureClass_conversion(union, 
																	workspace_db, 
																	"detailedUnionFinal" + buffer + "ft_" + region,
																	"""NOT(FEATUREID_1 = 0) AND FEATUREID = FEATUREID_1""" )															
			
		# Finalize buffer layer
		detailedFinal = arcpy.Dissolve_management(unionFinal,
													riparian_db + "/riparianBufferDetailed" + buffer + "ft_" + region,
													"FEATUREID_1",
													"#",
													"MULTI_PART",
													"#")							
									
		# Adjust name of FEATUREID field
		arcpy.AlterField_management(detailedFinal, 'FEATUREID_1', 'FEATUREID')			
		
		# Add field for area in square kilometers
		arcpy.AddField_management(detailedFinal, 
									"AreaSqKM", 
									"DOUBLE")
								
		arcpy.CalculateField_management(detailedFinal, 
											"AreaSqKM", 
											"!SHAPE.AREA@SQUAREKILOMETERS!", 
											"PYTHON")