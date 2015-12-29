import arcpy
from arcpy.sa import *
from arcpy import env

# ==============
# Specify inputs
# ==============
baseDirectory      = "C:/KPONEIL/GitHub/projects/basinCharacteristics/nlcdLandCover"
catchmentsFilePath = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/streamStructure/NHDHRDV2/products/hydrography.gdb/regionBoundary"
rasterFilePath     = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/land/nlcd/spatial/nlcd_2006_landcover_2011_edition_2014_03_31/nlcd_2006_landcover_2011_edition_2014_03_31.img"
reclassTable       = "C:/KPONEIL/GitHub/projects/shedsData/basinCharacteristics/rasterPrep/nlcdLandCover/reclassTable.csv"
outputName         = "NHDHRDV2"
keepFiles          = "YES"


# ===========
# Folder prep
# ===========

# Create general folders if they don't exist
# ------------------------------------------
# Create GIS files folder
gisFilesDir = baseDirectory + "/gisFiles"
if not arcpy.Exists(gisFilesDir): arcpy.CreateFolder_management(baseDirectory, 
                                                                "gisFiles")


# Create run specific folders if they don't exist
# -----------------------------------------------
# Create version folder
versionDir = gisFilesDir + "/" + version
if not arcpy.Exists(versionDir): arcpy.CreateFolder_management(gisFilesDir, 
                                                               version)

# Create version database
geoDatabase = versionDir + "/workingFiles.gdb"
if not arcpy.Exists(geoDatabase): arcpy.CreateFileGDB_management(versionDir, 
                                                                  "workingFiles.gdb")

# Create output folder
outputDir = versionDir + "/outputFiles"
if not arcpy.Exists(outputDir): arcpy.CreateFolder_management(versionDir, 
                                                               "outputFiles")


# =====================
# Raster pre-processing
# =====================

# Trim the raster to processing boundary
# --------------------------------------

# Create regional outline
outline = arcpy.Dissolve_management(catchmentsFilePath, 
										geoDatabase + "/outline",
										"#", 
										"#", 
										"SINGLE_PART", 
										"DISSOLVE_LINES")

# Buffer outline
boundary = arcpy.Buffer_analysis(outline, 
									geoDatabase + "/boundary", 
									"1 Kilometers", 
									"#", 
									"#", 
									"ALL")

# Reproject the boundary to match the NLCD raster
boundaryProj = arcpy.Project_management(boundary, 
										geoDatabase + "/boundaryProj", 
										rasterFilePath)

# Trim the raster to the boundary	
arcpy.env.extent = rasterFilePath
rangeRaster = ExtractByMask(rasterFilePath, boundaryProj)	

# Reproject the raster
# --------------------

# Get spatial references
catchSpatialRef  = arcpy.Describe(catchmentsFilePath).spatialReference.name
rasterSpatialRef = arcpy.Describe(rasterFilePath).spatialreference.name

# Reproject if necessary
if rasterSpatialRef != catchSpatialRef:	
	projectedRaster = arcpy.ProjectRaster_management(rangeRaster, 
													 geoDatabase + "/rangeRasterPrj",
													 catchmentsFilePath)
else: projectedRaster = rangeRaster

# ==========================
# Create categorical rasters
# ==========================

# Set directory
arcpy.env.workspace = geoDatabase

# List of column names
fieldList = arcpy.ListFields(reclassTable)

# Category position and count
fieldCount = range(2, len(fieldList))

# Loop through categories and reclassify raster
for i in fieldCount:

	print(i)
	
	# Category name
	category = fieldList[i]

	# Reclassify the raster
	# ---------------------
	recRaster = ReclassByTable(projectedRaster, 
								reclassTable,
								"Value",
								"Value", 
								str(category.name), 
								"NODATA")

	# Remove cells specified as -9999
	# -------------------------------
	# Count number of unique values
	uniqueValues = arcpy.GetRasterProperties_management(recRaster, 
														"UNIQUEVALUECOUNT")

	# If there are more than 2 unique values (1 & 0), then the others get removed
	if int(uniqueValues.getOutput(0)) > 2:
		
		# There should only be 2 unique values (1 and 0). Any more indicate 
		#	that other cells need to be removed
		outCon = Con(recRaster, recRaster, "", "VALUE = 0 OR VALUE = 1")
		outCon.save(outputDir + "/"+ str(category.name))
		
		# Delete the temporary object
		del(outCon)
	
	else: recRaster.save(outputDir + "/" + str(category.name))
	
	# Delete the temporary object
	# ---------------------------
	del(recRaster)

# If specified, delete processing files
if keepFiles == "NO":
	arcpy.Delete_management(geoDatabase)

