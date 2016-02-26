import arcpy
from arcpy import env
from arcpy.sa import *

# =============
# Define Inputs
# =============

# Parent project directory
baseDirectory = "C:/KPONEIL/HRD/V2"

# Hydrologic region being processed
regionHUC2 = "01"

# The path to the DSL DEM
demFilePath = "F:/KPONEIL/SourceData/topography/umass/dem"

# The folder with the the DEM tiles used to fill the missing area
nedDirectory = "F:/KPONEIL/SourceData/topography/ned"

# ==============
# Pre-processing
# ==============
#Set paths
nedDEMFolder = nedDirectory + "/NHDH" + regionHUC2

processing_db  = baseDirectory + "/gisFiles/NHDH" + regionHUC2 + "/processing.gdb"
boundaries_db  = baseDirectory + "/gisFiles/NHDH" + regionHUC2 + "/boundaries.gdb"
delineation_db = baseDirectory + "/gisFiles/NHDH" + regionHUC2 + "/arcHydroInput.gdb"
boundaryFilePath = boundaries_db + "/processingBoundary" + regionHUC2										

# Define consistent spatial reference
sourceDescribe = arcpy.Describe(demFilePath)
sourceSR = sourceDescribe.SpatialReference


# ======================
# Process DEM from UMass
# ======================
# Clip the Umass DEM to the boundary
arcpy.env.snapRaster = demFilePath
outExtractByMask = ExtractByMask(demFilePath, 
									boundaryFilePath)
outExtractByMask.save(processing_db + "/umassDEM" + regionHUC2)


# Create a polygon outline of the DEM
outCon = Con(outExtractByMask, 1, "", "VALUE >= -9999")

umassOutline = arcpy.RasterToPolygon_conversion(outCon, 
													boundaries_db + "/umassDEMOutline" + regionHUC2, 
													"NO_SIMPLIFY",
													"VALUE")

# Delete temp files from memory
arcpy.Delete_management(outCon)			
																					

# ===================================
# Create boundary of area without DEM
# ===================================													

missingAreaRaw = arcpy.Erase_analysis(boundaryFilePath,
										umassOutline,
										processing_db + '/missingAreaRaw' + regionHUC2)

missingArea = arcpy.MultipartToSinglepart_management(missingAreaRaw,
															processing_db + '/missingArea' + regionHUC2)

# Trim out the very small polygons
missingDEMZone = arcpy.FeatureClassToFeatureClass_conversion (missingArea, 
																boundaries_db, 
																"missingDEMZone" + regionHUC2, 
																""" "Shape_Area" >= """ + str(250000) )	

arcpy.Delete_management(missingAreaRaw)		
arcpy.Delete_management(missingArea)	


# Check missingDEMZone
count =  int(arcpy.GetCount_management(missingDEMZone).getOutput(0)) 

if count > 0:

	# ================
	# Process new DEMs
	# ================
	arcpy.env.workspace = nedDEMFolder
	rasterList = arcpy.ListRasters("*", "GRID")

	demsToMerge = []
	for j in range(len(rasterList)): 

		arcpy.env.snapRaster = demFilePath
		demPrj = arcpy.ProjectRaster_management(nedDEMFolder + "/" + str(rasterList[j]), 
													processing_db + "/dem" + str(j) + "prj_" + regionHUC2,
													sourceSR, 
													"BILINEAR", 
													30,
													"", "", "")

		# Clip to missing area
		outExtract = ExtractByMask(demPrj, 
									missingDEMZone)
		outExtract.save(processing_db + "/demExtr" + str(j) + "_" + regionHUC2)

		demsToMerge.append(processing_db + "/demExtr" + str(j) + "_" + regionHUC2)

		arcpy.Delete_management(demPrj)


	# ============
	# Mosaic DEMs
	# ===========
	demsToMerge.append(processing_db + "/umassDEM" + regionHUC2)

	arcpy.env.snapRaster = processing_db + "/umassDEM" + regionHUC2
	fullDEM = arcpy.MosaicToNewRaster_management(demsToMerge,
													delineation_db, 
													"dem" + regionHUC2,
													sourceSR,
													"32_BIT_FLOAT", 
													30, 
													1, 
													"LAST",
													"LAST")
else:
	fullDEM = arcpy.CopyRaster_management(processing_db + "/umassDEM" + regionHUC2,
											delineation_db + "/dem" + regionHUC2
											,"","","","","","32_BIT_FLOAT")



# ===================
# Create DEM boundary
# ===================

outCon = Con(fullDEM, 1, "", "VALUE >= -9999")

demOutline = arcpy.RasterToPolygon_conversion(outCon, 
												boundaries_db + "/demOutline" + regionHUC2, 
												"NO_SIMPLIFY",
												"VALUE")
