import arcpy
from arcpy.sa import *
from arcpy import env

# ==============
# Specify inputs
# ==============

baseDirectory      = "C:/KPONEIL/GitHub/projects/basinCharacteristics/prism"
catchmentsFilePath = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/streamStructure/NHDHRDV2/products/hydrography.gdb/regionBoundary"
sourceFolder       = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/climate/prism/spatial"
outputName         = "NHDHRDV2"


# ---------------
# Folder creation
# ---------------

# Create GIS files folder
gisFilesDir = baseDirectory + "/gisFiles"
if not arcpy.Exists(gisFilesDir): arcpy.CreateFolder_management(baseDirectory, 
                                                                "gisFiles")

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

# List of rasters and their output names
rasterList =  [ ["PRISM_ppt_30yr_normal_800mM2_01_asc.asc", "jan_prcp_mm"], 
				["PRISM_ppt_30yr_normal_800mM2_02_asc.asc", "feb_prcp_mm"],
				["PRISM_ppt_30yr_normal_800mM2_03_asc.asc", "mar_prcp_mm"],
				["PRISM_ppt_30yr_normal_800mM2_04_asc.asc", "apr_prcp_mm"],
				["PRISM_ppt_30yr_normal_800mM2_05_asc.asc", "may_prcp_mm"],
				["PRISM_ppt_30yr_normal_800mM2_06_asc.asc", "jun_prcp_mm"],
				["PRISM_ppt_30yr_normal_800mM2_07_asc.asc", "jul_prcp_mm"],
				["PRISM_ppt_30yr_normal_800mM2_08_asc.asc", "aug_prcp_mm"],
				["PRISM_ppt_30yr_normal_800mM2_09_asc.asc", "sep_prcp_mm"],
				["PRISM_ppt_30yr_normal_800mM2_10_asc.asc", "oct_prcp_mm"],
				["PRISM_ppt_30yr_normal_800mM2_11_asc.asc", "nov_prcp_mm"],
				["PRISM_ppt_30yr_normal_800mM2_12_asc.asc", "dec_prcp_mm"],
				["PRISM_tmax_30yr_normal_800mM2_annual_asc.asc", "ann_tmax_c"],
				["PRISM_tmin_30yr_normal_800mM2_annual_asc.asc", "ann_tmin_c"] ]


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
										"25 Kilometers", 
										"#", 
										"#", 
										"ALL")
else: boundary = geoDatabase + "/boundary"

# Reproject the boundary to match the covariate raster
if not arcpy.Exists(geoDatabase + "/boundaryProj"):
	boundaryProj = arcpy.Project_management(boundary, 
											geoDatabase + "/boundaryProj", 
											sourceFolder + "/" + rasterList[0][0],)
else: boundaryProj = geoDatabase + "/boundaryProj"

# ------------------
# Process the raster
# ------------------

for r in range(len(rasterList)):

	# Trim the raster to the boundary	
	rasterFilePath = sourceFolder + "/" + rasterList[r][0]
	arcpy.env.extent = rasterFilePath
	extractedRaster = ExtractByMask(rasterFilePath, boundaryProj)
	extractedRaster.save(outputDir + "/" + rasterList[r][1])