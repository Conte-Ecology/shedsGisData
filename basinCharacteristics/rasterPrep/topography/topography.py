import arcpy
from arcpy.sa import *
from arcpy import env

# ==============
# Specify inputs
# ==============
baseDirectory  = "C:/KPONEIL/GitHub/projects/basinCharacteristics/topography"
demFilePath = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/topography/NHDHRDV2/dem"
outputName = "NHDHRDV2"


# ---------------
# Folder creation
# ---------------

# Create GIS files folder
gisFilesDir = baseDirectory + "/gisFiles"
if not arcpy.Exists(gisFilesDir): arcpy.CreateFolder_management(baseDirectory, "gisFiles")

# Create version folder
versionDir = gisFilesDir + "/" + outputName
if not arcpy.Exists(versionDir): arcpy.CreateFolder_management(gisFilesDir, outputName)

# Create output folder
outputDir = versionDir + "/outputFiles"
if not arcpy.Exists(outputDir): arcpy.CreateFolder_management(versionDir, "outputFiles")


# --------------
# Create rasters
# --------------
# Generate the slope raster
outSlope = Slope(demFilePath, "PERCENT_RISE")
outSlope.save(outputDir + "/slope_pcnt")

# Move the DEM & rename
arcpy.CopyRaster_management(demFilePath,
								outputDir + "/elevation")

