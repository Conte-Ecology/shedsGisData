# =============
# Define Inputs
# =============
# Parent project directory
baseDirectory = "C:/KPONEIL/HRD/V2"

# List all hydro regions processed
hydroRegions = ['01', '02', '03', '04', '05', '06']

# ===================
# Specify directories
# ===================
sourceDirectory   = baseDirectory + "/gisFiles/postProcessing/Edits.gdb"
outputGeodatabase = baseDirectory + "/products/NHDHRDV2.gdb"
outputDirectory   = baseDirectory + "/products/shapefiles"

# Make hydro region outlines
for region in hydroRegions:

	currentCats = sourceDirectory + "/correctedCats" + region
	currentStreams = sourceDirectory + "/correctedFlowlines" + region

	# Export to geodatabase
	finalCats    = arcpy.CopyFeatures_management(currentCats,    outputGeodatabase + "/Catchments" + region)
	finalStreams = arcpy.CopyFeatures_management(currentStreams, outputGeodatabase + "/Flowlines" + region)

	# Add area to catchments
	# ----------------------
	arcpy.AddField_management(finalCats, 
								"AreaSqKM", 
								"DOUBLE")
								
	arcpy.CalculateField_management(finalCats, 
										"AreaSqKM", 
										"!SHAPE.AREA@SQUAREKILOMETERS!", 
										"PYTHON")
	

	# Add length to flowlines
	# -----------------------
	arcpy.AddField_management(finalStreams, 
								"LengthKM", 
								"DOUBLE")
								
	arcpy.CalculateField_management(finalStreams, 
										"LengthKM", 
										"!SHAPE.LENGTH@KILOMETERS!", 
										"PYTHON")

										
	# Create boundaries
	# -----------------
	arcpy.Dissolve_management(finalCats,
								outputGeodatabase + "/regionBoundary" + region, 
								"#", "#",
								"MULTI_PART")									
										
										
		
	# Export files to shapefile
	# -------------------------
	arcpy.FeatureClassToShapefile_conversion(finalCats,    outputDirectory)							
	arcpy.FeatureClassToShapefile_conversion(finalStreams, outputDirectory)										