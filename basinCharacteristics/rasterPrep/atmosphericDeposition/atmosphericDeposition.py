import arcpy
from arcpy.sa import *
from arcpy import env

# ==============
# Specify inputs
# ==============
baseDirectory      = "C:/KPONEIL/GitHub/projects/basinCharacteristics/atmosphericDeposition"
catchmentsFilePath = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/streamStructure/NHDHRDV2/products/hydrography.gdb/regionBoundary"
sourceFolder       = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/deposition/nadp/spatial"
outputName         = "NHDHRDV2"


# ---------------
# Folder creation
# ---------------

# Create GIS files folder
gisFilesDir = baseDirectory + "/gisFiles"
if not arcpy.Exists(gisFilesDir): arcpy.CreateFolder_management(baseDirectory, "gisFiles")

# Create version folder
versionDir = gisFilesDir + "/" + outputName
if not arcpy.Exists(versionDir): arcpy.CreateFolder_management(gisFilesDir, version)

# Create version database
geoDatabase = versionDir + "/workingFiles.gdb"
if not arcpy.Exists(geoDatabase): arcpy.CreateFileGDB_management(versionDir, "workingFiles.gdb")

# Create output folder
outputDir = versionDir + "/outputFiles"
if not arcpy.Exists(outputDir): arcpy.CreateFolder_management(versionDir, "outputFiles")

rasterList = ["dep_no3_2011", "dep_so4_2011"]

# --------------------------
# Prepare the boundary layer
# --------------------------

# Create regional outline
if not arcpy.Exists(geoDatabase + "/outline"):
	outline = arcpy.Dissolve_management(catchmentsFilePath, 
											geoDatabase + "/outline",
											"#", 
											"#", 
											"SINGLE_PART", 
											"DISSOLVE_LINES")
else: outline = geoDatabase + "/outline"

# Buffer outline
if not arcpy.Exists(geoDatabase + "/boundary"):
	boundary = arcpy.Buffer_analysis(outline, 
										geoDatabase + "/boundary", 
										"1 Kilometers", 
										"#", 
										"#", 
										"ALL")
else: boundary = geoDatabase + "/boundary"

# Reproject the boundary to match the covariate raster
if not arcpy.Exists(geoDatabase + "/boundaryProj"):
	boundaryProj = arcpy.Project_management(boundary, 
											geoDatabase + "/boundaryProj", 
											sourceFolder + "/" + rasterList[0] + ".tif")
else: boundaryProj = geoDatabase + "/boundaryProj"

# -------------------
# Process the rasters
# -------------------

for r in range(len(rasterList)):

	# Trim raster to boundary
	# -----------------------
	# Define the raster file path
	rasterFilePath = sourceFolder + "/" + rasterList[r] + ".tif"

	# Trim the raster to the boundary	
	arcpy.env.extent = rasterFilePath
	extractedRaster  = ExtractByMask(rasterFilePath, boundaryProj)
	
	# Save the trimmed raster
	extractedRaster.save(outputDir + "/" + rasterList[r])