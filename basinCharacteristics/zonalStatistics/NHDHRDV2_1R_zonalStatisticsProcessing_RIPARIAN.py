#Import System Modules:
import arcpy
from arcpy import env
from arcpy.sa import *

# ==============
# Specify Inputs
# ==============

# User input file
inputsFilePath = "C:/KPONEIL/GitHub/projects/shedsData/basinCharacteristics/zonalStatistics/INPUTS_NHDHRDV2_RIPARIAN.txt"

# Raster directory
raster_directory = "C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics/gisFiles/rasters"

# Vector directory
vector_directory = "C:/KPONEIL/HRD/V2/products/riparianBuffers.gdb"

# Template for rasterizing polygons
rasterTemplate = "C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics/gisFiles/versions/NHDHRDV2/catchmentRasters.gdb/Catchments01"

# =========================
# Read use specified inputs
# =========================

# Open file with input parameters
with open (inputsFilePath, "r") as myfile:
    lines = myfile.readlines()

outputName          = lines[1] .replace('outputName', '')         .replace('=', '').replace('\n','').replace('"','').replace(' ','')
catchmentsFileNames = lines[4] .replace('catchmentsFileNames', '').replace('=', '').replace('c(','').replace(')','').replace('\n','').replace('"','').replace(' ','').split(",")
zoneField           = lines[7] .replace('zoneField', '')          .replace('=', '').replace('\n','').replace('"','').replace(' ','')
statType            = lines[10].replace('statType', '')           .replace('=', '').replace('\n','').replace('"','').replace(' ','')
discreteRasters     = lines[13].replace('discreteRasters', '')    .replace('=', '').replace('c(','').replace(')','').replace('\n','').replace('"','').replace(' ','').split(",")
continuousRasters   = lines[14].replace('continuousRasters', '')  .replace('=', '').replace('c(','').replace(')','').replace('\n','').replace('"','').replace(' ','').split(",")
baseDirectory       = lines[17].replace('baseDirectory', '')      .replace('=', '').replace('\n','').replace('"','').replace(' ','')


# ===========
# Folder prep
# ===========
# Check if folders exist, create them if they don't

# Parent directories
# ------------------
# Main versions directory
version_directory = baseDirectory + "/versions"
if not arcpy.Exists(version_directory): arcpy.CreateFolder_management(baseDirectory, "versions")

# Main gisFiles directory
gisFiles_directory = baseDirectory + "/gisFiles"
if not arcpy.Exists(gisFiles_directory): arcpy.CreateFolder_management(baseDirectory, "gisFiles")

# GIS files versions directory
gisVersion_directory = gisFiles_directory + "/versions"
if not arcpy.Exists(gisVersion_directory): arcpy.CreateFolder_management(gisFiles_directory, "versions")


#  Run-specific folders
# ---------------------
# Run-specific gisFiles directory
working_directory = gisVersion_directory + "/" + outputName
if not arcpy.Exists(working_directory): arcpy.CreateFolder_management(gisVersion_directory, outputName)

# Set the run database. Create one if it doesn't exist.
rasters_db = working_directory + "/projectedRasters.gdb"
if not arcpy.Exists(rasters_db): arcpy.CreateFileGDB_management (working_directory, "projectedRasters", "CURRENT")

# Set the run database. Create one if it doesn't exist.
catRast_db = working_directory + "/catchmentRasters.gdb"
if not arcpy.Exists(catRast_db): arcpy.CreateFileGDB_management (working_directory, "catchmentRasters", "CURRENT")

# Run-specific output folder.
outputVersion_directory = version_directory + "/" + outputName
if not arcpy.Exists(outputVersion_directory): arcpy.CreateFolder_management(version_directory, outputName)

# Run-specific GIS tables.
gisTables_directory = outputVersion_directory + "/gisTables"
if not arcpy.Exists(gisTables_directory): arcpy.CreateFolder_management(outputVersion_directory, "gisTables")

# Run-specific R tables.
rTables_directory = outputVersion_directory + "/rTables"
if not arcpy.Exists(rTables_directory): arcpy.CreateFolder_management(outputVersion_directory, "rTables")

# Run-specific completed statistics.
completedStats_directory = outputVersion_directory + "/completedStats"
if not arcpy.Exists(completedStats_directory): arcpy.CreateFolder_management(outputVersion_directory, "completedStats")


# Name the map and dataframe for removing layers
# ----------------------------------------------
mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd)[0]



# Check raster list
# -----------------

# Master list of rasters
rasterList = discreteRasters + continuousRasters

# Remove NAs if there are any
if "NA" in rasterList: rasterList.remove("NA")


# Loop through catchments files
for catchmentsFileName in catchmentsFileNames:

	# Add Catchments shapefile to map
	# -------------------------------
	addLayer = arcpy.mapping.Layer(vector_directory + "/" + catchmentsFileName)
	arcpy.mapping.AddLayer(df, addLayer, "AUTO_ARRANGE")

	# Create catchment-specific geodatabases
	catTables_db = gisTables_directory + "/" + catchmentsFileName + ".gdb"
	if not arcpy.Exists(catTables_db): arcpy.CreateFileGDB_management (gisTables_directory, catchmentsFileName, "CURRENT")
	
	# Main versions directory
	catTables_directory = gisTables_directory + "/" + catchmentsFileName
	if not arcpy.Exists(catTables_directory): arcpy.CreateFolder_management(gisTables_directory, catchmentsFileName)
	
	
	# ==========================
	# Rasterize Catchments Layer
	# ==========================
	zonalRaster = catRast_db + "/" + catchmentsFileName

	# If the zonal shapefile has not been rasterized, then do so.
	if not arcpy.Exists(zonalRaster):
		
		arcpy.env.snapRaster = rasterTemplate
		
		arcpy.FeatureToRaster_conversion(vector_directory + "/" + catchmentsFileName, 
											zoneField, 
											zonalRaster, 
											30)

		# Generate the attribute field
		arcpy.BuildRasterAttributeTable_management(zonalRaster, "NONE")
		
		# Get raster cell size
		cellSize = int(arcpy.GetRasterProperties_management(zonalRaster, "CELLSIZEX").getOutput(0))
			
		# Add area
		arcpy.AddField_management(zonalRaster, "AreaSqKM", "DOUBLE")
		arcpy.CalculateField_management(zonalRaster, "AreaSqKM", "[COUNT]*900/1000000", "VB", "#")
			
		# Add zoneField
		arcpy.AddField_management(zonalRaster, zoneField, "DOUBLE")
		arcpy.CalculateField_management(zonalRaster, zoneField, "!VALUE!", "PYTHON_9.3")	

	# Save the rasterized catchment areas	
	if not arcpy.Exists(catTables_directory + "/" + "catRasterAreas.dbf"):
		arcpy.TableToTable_conversion(zonalRaster, 
										catTables_directory, 
										"catRasterAreas.dbf")
	
	
	
	# ==================================
	# Reproject & Resample Value Rasters
	# ==================================
	# The value rasters should match the catchment raster
	
	# Define the template cell size
	cellX = int(arcpy.GetRasterProperties_management(zonalRaster, "CELLSIZEX").getOutput(0))

	# List rasters that have already been projected
	arcpy.env.workspace = rasters_db
	projectedRasters = [x.encode('UTF8') for x in arcpy.ListRasters()]

	# Check if any of the rasters need to be projected/resampled
	if not(set(rasterList) <= set(projectedRasters)):

		# List rasters that need to be projected
		rastersToProject = [x for x in rasterList if x not in projectedRasters]

		# Set directory
		arcpy.env.workspace = raster_directory

		# Loop through all rasters
		for raster in rastersToProject:
			
			arcpy.env.snapRaster = zonalRaster
			
			# Project and resample discrete (categorical) rasters with appropriate resampling method
			if (raster in discreteRasters):
				arcpy.ProjectRaster_management(raster_directory + "/" + raster, 
												rasters_db + "/" + raster,  
												zonalRaster,
												"NEAREST",
												cellX,
												"#","#","#")
			# Project and resample continuous rasters with appropriate resampling method		
			if (raster in continuousRasters):
				arcpy.ProjectRaster_management(raster_directory + "/" + raster, 
												rasters_db + "/" + raster,  
												zonalRaster,
												"BILINEAR",
												cellX,
												"#","#","#")


	# ====================
	# Run Zonal Statistics
	# ====================
	for raster in rasterList: # raster loop
		
		# -------------------------
		# Run zonal statistics tool
		# -------------------------
		#Name layers:
		outTable = catTables_db + "/" + raster

		# Run zonal statistics over each layer using the rasterized catchments file
		ZonalStatisticsAsTable(zonalRaster,
									"Value",
									rasters_db + "/" + raster,
									outTable,
									"DATA",
									statType)	

		# Add field for zoneField
		arcpy.AddField_management(outTable, zoneField, "DOUBLE")
		arcpy.CalculateField_management (outTable, zoneField, "!VALUE!", "PYTHON_9.3")

		
		# --------------------------------------
		# Calculate catchments with missing data
		# --------------------------------------
		# Join the output file to the catchments file
		attributeJoin = arcpy.AddJoin_management (catchmentsFileName + ".shp", 
													zoneField, 
													outTable, 
													zoneField)
		
		# Define the query
		qry = raster +  "."  + zoneField + ' IS NULL'
		
		arcpy.SelectLayerByAttribute_management (attributeJoin, "NEW_SELECTION", qry)
		
		missingVals = arcpy.TableToTable_conversion(catchmentsFileName + ".shp",
													catTables_db,
													raster + "_" + "MissingValues")
		
		# Remove the join & clear the selection
		arcpy.RemoveJoin_management(catchmentsFileName + ".shp")
		arcpy.SelectLayerByAttribute_management(catchmentsFileName + ".shp", "CLEAR_SELECTION")
		
		# Add a new field for the table to match the zonal statistics output table
		arcpy.AddField_management(missingVals, "AREA", "DOUBLE")
		arcpy.AddField_management(missingVals, statType, "DOUBLE")

		arcpy.CalculateField_management (missingVals, "AREA", 0, "PYTHON_9.3")
		arcpy.CalculateField_management (missingVals, statType, -9999, "PYTHON_9.3")							
				

		# Append the missing values to the existing table
		arcpy.Append_management(missingVals, 
									outTable, 
									"NO_TEST")


		arcpy.TableToTable_conversion(outTable,
										catTables_directory,
										raster + ".dbf")