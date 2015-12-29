import arcpy
from arcpy.sa import *
from arcpy import env

# ==============
# Specify inputs
# ==============
baseDirectory      = "C:/KPONEIL/GitHub/projects/basinCharacteristics/nlcdTreeCanopy"
catchmentsFilePath = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/streamStructure/NHDHRDV2/products/hydrography.gdb/regionBoundary"
rasterFilePath 	   = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/land/nlcd/spatial/nlcd_2011_USFS_tree_canopy_2011_edition_2014_03_31/cartographic_product/nlcd2011_usfs_treecanopy_cartographic_3-31-2014.img"
outputName         = "NHDHRDV2"
statesFilePath     = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/political/states/States.shp"


# ===========
# Folder prep
# ===========

# Create GIS files folder
gisFilesDir = baseDirectory + "/gisFiles"
if not arcpy.Exists(gisFilesDir): arcpy.CreateFolder_management(baseDirectory, "gisFiles")

# Create version folder
versionDir = gisFilesDir + "/" + version
if not arcpy.Exists(versionDir): arcpy.CreateFolder_management(gisFilesDir, version)

# Create version database
working_db = versionDir + "/processingFiles.gdb"
if not arcpy.Exists(working_db): arcpy.CreateFileGDB_management(versionDir, "processingFiles.gdb")

# Create output folder
outputDir = versionDir + "/outputFiles"
if not arcpy.Exists(outputDir): arcpy.CreateFolder_management(versionDir, "outputFiles")


# ================
# Define functions
# ================

# Reproject a shapefile ("toBeProjected") to the same projection as another layer ("sourceProjection").
def match_projection_shp(sourceProjection, toBeProjected, outputFilePath):

	sourcePrj = sourceProjection
	toBePrj = toBeProjected

	# Get source projection info	
	sourcePrjDescribe = arcpy.Describe(sourcePrj)
	sourcePrjSR = sourcePrjDescribe.SpatialReference
	sourcePrjSRName = sourcePrjSR.Name

	# Get current projection info
	toBePrjDescribe = arcpy.Describe(toBePrj)
	toBePrjSR = toBePrjDescribe.SpatialReference
	toBePrjSRName = toBePrjSR.Name

	if not arcpy.Exists(outputFilePath):
		if not toBePrjSRName == sourcePrjSRName:

			projectedObject = arcpy.Project_management(toBePrj, 
													outputFilePath, 
													sourcePrj)
		else: projectedObject = arcpy.Copy_management(toBePrj, outputFilePath)
		
	else: projectedObject = outputFilePath
	
	return projectedObject


# ==========================
# Prepare the boundary layer
# ==========================

statesPrj = match_projection_shp(catchmentsFilePath, statesFilePath, working_db + "/states_catProj")

arcpy.MakeFeatureLayer_management(statesPrj, "statesPrj_Lyr")

selectStates = arcpy.SelectLayerByLocation_management("statesPrj_Lyr", "INTERSECT", catchmentsFilePath, "#", "NEW_SELECTION")

boundary = arcpy.Dissolve_management(selectStates, 
										working_db + "/boundary", 
										"#", 
										"#", 
										"MULTI_PART")

boundaryPrj = match_projection_shp(rasterFilePath, boundary, working_db + "/boundary_rastProj")


# ===============================
# Trim the raster to the boundary	
# ===============================
arcpy.env.extent = rasterFilePath
trimmedRaster = ExtractByMask(rasterFilePath, boundaryPrj)
trimmedRaster.save(outputDir + "/tree_canopy")
