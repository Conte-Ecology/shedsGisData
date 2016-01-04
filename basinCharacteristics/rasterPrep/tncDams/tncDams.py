# ==============
# Specify inputs
# ==============

# Define directories
baseDirectory = "C:/KPONEIL/GitHub/projects/basinCharacteristics/tncDams"
polygonsFile = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/streamStructure/NHDHRDV2/products/hydrography.gdb/Catchments"
damsFile = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/connectivity/tnc/TNC Dams - High Resolution Flowlines/Dams_ALL_highres.shp"
outputName = "NHDHRDV2"
zoneField = "FEATUREID"

# ===============
# Folder creation
# ===============

# Create GIS files folder
gisFilesDir = baseDirectory + "/gisFiles"
if not arcpy.Exists(gisFilesDir): arcpy.CreateFolder_management(baseDirectory, "gisFiles")

# Output table folder
outputTablesDir = baseDirectory + "/outputTables"
if not arcpy.Exists(outputTablesDir): arcpy.CreateFolder_management(baseDirectory, "outputTables")

# Create version folder
versionDir = gisFilesDir + "/" + outputName
if not arcpy.Exists(versionDir): arcpy.CreateFolder_management(gisFilesDir, outputName)

# Create version database
geoDatabase = versionDir + "/processingFiles.gdb"
if not arcpy.Exists(geoDatabase): arcpy.CreateFileGDB_management(versionDir, "processingFiles.gdb")

# ----------------
# Define Functions
# ----------------

# Unique Values function	
def unique_values(table, field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})

		
# -------------------------------------------
# Only use dams that are snapped to flowlines
# -------------------------------------------
dams = arcpy.FeatureClassToFeatureClass_conversion(damsFile, 
													geoDatabase, 
													"damsOnHighRez",
													""" "Use" = 1 OR "Use" = 2 """ )

# ---------------------
# Link dams to polygons
# ---------------------
# Spatial join the polygons and dams file
arcpy.SpatialJoin_analysis(polygonsFile,
							dams,
							geoDatabase + "/spatialJoin",
							"JOIN_ONE_TO_MANY",
							"KEEP_ALL",
							"#",
							"CONTAINS")

# Convert to a table
rawTable = arcpy.TableToTable_conversion(geoDatabase + "/spatialJoin", 
											geoDatabase, 
											"rawSpatialJoin")

# -----------------------------------
# Count barrier types in each polygon
# -----------------------------------											
# Get unique barrier values
barriers = unique_values(dams, "DEG_BARR")
	
# Convert to TableView for selecting 
arcpy.MakeTableView_management(rawTable, "spJoin_TableView")								
		
# Field names list (for summary stats)		
barrierFields = []
								
for bar in barriers:

	# Add degree barrier fields to table
	arcpy.AddField_management("spJoin_TableView", 
								"DEG_BARR_" + str(bar), 
								"LONG")		
	
	# Select current barrier degrees
	arcpy.SelectLayerByAttribute_management("spJoin_TableView", 
												"NEW_SELECTION",
												""" "DEG_BARR" =  """ + str(bar) )
												
	# Count up barriers
	arcpy.CalculateField_management ("spJoin_TableView", 
										"DEG_BARR_" + str(bar), 
										1, 
										"PYTHON_9.3")	
	
	# Create list of field names
	barrierFields.append(["DEG_BARR_" + str(bar), "Sum"])										

# Clear out the selection
arcpy.SelectLayerByAttribute_management("spJoin_TableView", "CLEAR_SELECTION")							


# Output the table with number of barriers per polygon			
finalStats = arcpy.Statistics_analysis("spJoin_TableView", 
											geoDatabase + "/finalBarrierStats", 
											barrierFields, 
											zoneField)

# Because we want a DBF file and Arc's column limitations are pathetic...
for barF in barrierFields:											
	arcpy.AlterField_management(finalStats, "SUM_" + barF[0], barF[0], barF[0])

# Create output table readable into R
arcpy.TableToTable_conversion(finalStats, 
								outputTablesDir, 
								"barrierStats_" + outputName + ".dbf")