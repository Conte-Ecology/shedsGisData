# =============
# Define Inputs
# =============
# Parent project directory
baseDirectory = "C:/KPONEIL/HRD/V2"

# List all hydro regions processed
hydroRegions = ['01', '02', '03', '04', '05', '06']


# =================
# Setup directories
# =================
# Arc Hydro vectors geodatabase
workspace_db = baseDirectory + "/gisFiles/postProcessing/workspace.gdb"

hydrography_db = baseDirectory + "/products/hydrography.gdb"

# =================
# Process Flowlines
# =================
for region in hydroRegions:

	print(region)

	# Existing Layers
	# ===============
	highResLines = baseDirectory + "/gisFiles/NHDH" + region + "/arcHydroInput.gdb/delineationStreams" + region
	
	catchments = hydrography_db + "/Catchments" + region


	# The next section is computationally intensive and may throw an error on machines with less memory.

	# Detailed Lines
	# ==============
	# Creates one feature per reach
	dissolveLines = arcpy.Dissolve_management(highResLines,
												workspace_db + "/dissolve" + region,
												"#", "#",
												"MULTI_PART",
												"UNSPLIT_LINES")
												
	# Establish link between flowlines and catchments
	intersect = arcpy.Intersect_analysis([dissolveLines, catchments],
											workspace_db + "/intersect" + region,
											"ALL",
											"#",
											"INPUT")
	
	# Dissolves flowlines by the catchments they fall inside
	detailedLines = arcpy.Dissolve_management(intersect,
												hydrography_db + "/detailedFlowlines" + region,
												"FEATUREID", 
												"#",
												"MULTI_PART",
												"#")
	
	# Add a field for length in kilometers
	arcpy.AddField_management(detailedLines, 
								"LengthKM", 
								"DOUBLE")

	arcpy.CalculateField_management(detailedLines, 
										"LengthKM", 
										"!SHAPE.LENGTH@KILOMETERS!", 
										"PYTHON")
