# This script is an evolution of the original "createRiparianBuffers.py" script.
#   It is designed to create riparian buffers for flowline layers too large to process.
#   These layers end up 


import numpy as np

# =============
# Define Inputs
# =============
# Parent project directory
baseDirectory = "C:/KPONEIL/HRD/V2"

# List all hydro regions processed
hydroRegions = ['01', '02', '03', '04', '05', '06']

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
for region in hydroRegions:

	# Prepare regional hydrography layers
	# -----------------------------------
	detailedFlowlines = hydrography_db + "/detailedFlowlines" + region
	
	arcpy.MakeFeatureLayer_management(detailedFlowlines, "detailedFlowlines_lyr")
	
	catchments = arcpy.FeatureClassToFeatureClass_conversion(hydrography_db + "/Catchments" + region, 
																workspace_db, 
																"catchments" + region)
	
	
	# Add fields for sectioning
	# -------------------------
	arcpy.AddField_management(catchments, "Y", "DOUBLE")
	arcpy.CalculateField_management(catchments, "Y", "!shape.centroid.Y!", "PYTHON_9.3")
	arcpy.AddField_management(catchments, "Processed", "SHORT")
	arcpy.CalculateField_management(catchments, "Processed", 0, "PYTHON_9.3")
	
	
	# Determine sections
	# ------------------
	extent = arcpy.Describe(catchments).extent
	south = extent.YMin
	north = extent.YMax

	sections = np.linspace(north, south, 8)

	arcpy.MakeFeatureLayer_management(catchments, "catchments_lyr")
	

	for x in range(len(sections)-1):

		# Isolate catchments section
		# --------------------------
		selectCats = arcpy.FeatureClassToFeatureClass_conversion(catchments, 
																	workspace_db, 
																	"selectCats" + str(x+1) + "_" + region,
																	""""Processed" = 0 AND "Y" >= """ + str(sections[x+1]))
		# Prevent errors in the Union tool
		arcpy.RepairGeometry_management(selectCats)		
		
		
		# Mark processed section in regional catchments
		arcpy.SelectLayerByAttribute_management ("catchments_lyr", 
													"NEW_SELECTION",
													""""Processed" = 0 AND "Y" >= """ + str(sections[x+1]))
																
		arcpy.CalculateField_management("catchments_lyr", "Processed", 1, "PYTHON_9.3")
				
		arcpy.SelectLayerByAttribute_management ("catchments_lyr", "CLEAR_SELECTION")
					

		# Isolate flowlines section
		# -------------------------
		arcpy.SelectLayerByLocation_management ("detailedFlowlines_lyr",
												"WITHIN",
												selectCats,
												"", 
												"NEW_SELECTION")
	
		selectLines = arcpy.FeatureClassToFeatureClass_conversion("detailedFlowlines_lyr", 
																		workspace_db, 
																		"selectLines" + str(x+1) + "_" + region)
	
		arcpy.SelectLayerByAttribute_management ("detailedFlowlines_lyr", "CLEAR_SELECTION")
	
		# Generate buffers
		for buffer in bufferDistancesFT:
		
			# Create raw buffer
			detailedBuffer = arcpy.Buffer_analysis(selectLines, 
													workspace_db + "/detailedBuffer" + buffer + "ft" + str(x+1) + "_" + region, 
													buffer + " FEET", 
													"FULL", 
													"ROUND", 
													"NONE")
		
			# Prevent errors in the Union tool								
			arcpy.RepairGeometry_management (detailedBuffer)	

			# Pair buffers with catchments
			union = arcpy.Union_analysis([detailedBuffer, selectCats], 
											workspace_db + "/detailedBufCatUnion" + buffer + "ft" + str(x+1) + "_" + region,
											"ALL",
											"#",
											"GAPS")
			
			# Select only buffers and ensure that they pair to the correct catchment	
			unionFinal = arcpy.FeatureClassToFeatureClass_conversion(union, 
																		workspace_db, 
																		"detailedUnionFinal" + buffer + "ft" + str(x+1) + "_" + region,
																		"""NOT(FEATUREID_1 = 0) AND FEATUREID = FEATUREID_1""" )
																		
			# Finalize buffer layer
			detailedFinal = arcpy.Dissolve_management(unionFinal,
														workspace_db + "/riparianBufferDetailed" + buffer + "ft" + str(x+1) + "_" + region,
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

	# Clean up layers
	arcpy.Delete_management("detailedFlowlines_lyr")												
	arcpy.Delete_management("catchments_lyr")												


	# Merge sections together to create final buffer layer
	for buffer in bufferDistancesFT:	
		
		# List layers to merge
		toMerge = []
		for x in range(len(sections)-1):
		
			toMerge.append(workspace_db + "/riparianBufferDetailed" + buffer + "ft" + str(x+1) + "_" + region)
		
		# Merge sections
		arcpy.Merge_management(toMerge, 
								riparian_db + "/riparianBufferDetailed" + buffer + "ft_" + region)
		
		