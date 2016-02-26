import arcpy
from arcpy import env
import arcpy.cartography as CA

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
sourceDirectory   = baseDirectory + "/gisFiles/postProcessing/manualEdits.gdb"

productFolder = baseDirectory + "/products"
if not arcpy.Exists(productFolder): arcpy.CreateFolder_management(baseDirectory + "/products")

# Arc Hydro vectors geodatabase
hydrography_db = productFolder + "/products.gdb"
if not arcpy.Exists(hydrography_db): arcpy.CreateFileGDB_management (productFolder, "products", "CURRENT")

# Arc Hydro vectors geodatabase
workspace_db = baseDirectory + "/gisFiles/postProcessing/workspace.gdb"
if not arcpy.Exists(workspace_db): arcpy.CreateFileGDB_management (baseDirectory + "/gisFiles/postProcessing", "workspace", "CURRENT")

boundaryList = []

# Make hydro region outlines
for region in hydroRegions:

	# Update status
	print(region)

	# Catchments
	# ==========
	currentCats = sourceDirectory + "/correctedCats" + region
	
	# Disable z + m values
	arcpy.env.outputMFlag = "Disabled"
	arcpy.env.outputZFlag = "Disabled"
	
	# Export to geodatabase	
	finalCats  = arcpy.FeatureClassToFeatureClass_conversion(currentCats, 
																hydrography_db, 
																"Catchments" + region)
		
	# Add area 
	arcpy.AddField_management(finalCats, 
								"AreaSqKM", 
								"DOUBLE")
								
	arcpy.CalculateField_management(finalCats, 
										"AreaSqKM", 
										"!SHAPE.AREA@SQUAREKILOMETERS!", 
										"PYTHON")
	
	# Delete unnecessary fields
	arcpy.DeleteField_management(finalCats, 
									"Shape_Leng")
	

	
	# Flowlines
	# =========
	currentStreams = sourceDirectory + "/correctedFlowlines" + region

	# Smooth the flowlines to follow a more natural path
	simplifedLine = CA.SimplifyLine(currentStreams, 
										workspace_db + "/simplifyFlowlines" + region, 
										"BEND_SIMPLIFY", 
										"60 Meters",
										"FLAG_ERRORS",
										"KEEP_COLLAPSED_POINTS",
										"CHECK")

	smoothedLine = arcpy.SmoothLine_cartography(simplifedLine,
													workspace_db + "/smoothedFlowlines" + region,
													"PAEK",
													"60 Meters",
													"FIXED_CLOSED_ENDPOINT",
													"FLAG_ERRORS")
					
	
	# Disable z + m values
	arcpy.env.outputMFlag = "Disabled"
	arcpy.env.outputZFlag = "Disabled"
	
	# Export to geodatabase	
	finalLines  = arcpy.FeatureClassToFeatureClass_conversion(smoothedLine, 
																hydrography_db, 
																"Flowlines" + region)
		
	# Add length
	arcpy.AddField_management(finalLines, 
								"LengthKM", 
								"DOUBLE")
								
	arcpy.CalculateField_management(finalLines, 
										"LengthKM", 
										"!SHAPE.LENGTH@KILOMETERS!", 
										"PYTHON")

	# Delete unnecessary fields
	arcpy.DeleteField_management(finalLines, 
									["Shape_Leng", "SimLnFLag", "InLine_FID", "SmoLnFLag"])	

	
	# Region Boundary
	# ===============
	arcpy.Dissolve_management(finalCats,
								hydrography_db + "/regionBoundary" + region, 
								"#", "#",
								"MULTI_PART")	


	boundaryList.append(hydrography_db + "/regionBoundary" + region)							

# Full Region Boundary
# ====================
boundaryMerge = arcpy.Merge_management(boundaryList, 
										workspace_db + "/mergeRegionBoundaries")

arcpy.Dissolve_management(boundaryMerge,
								hydrography_db + "/regionBoundary", 
								"#", "#",
								"MULTI_PART")