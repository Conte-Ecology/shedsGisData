# ===========
# User Inputs
# ===========
regionHUC2 = "01"

baseDirectory = "C:/KPONEIL/HRD/V2"

minAreaSqKM = 0.5

sourceFolder = "F:/KPONEIL/SourceData/NHDplus/NHDHighres/NHDH" + regionHUC2

# ==============
# Pre-processing
# ==============
# Define directories
processing_db  = baseDirectory + "/gisFiles/NHDH" + regionHUC2 + "/processing.gdb"
boundaries_db  = baseDirectory + "/gisFiles/NHDH" + regionHUC2 + "/boundaries.gdb"
delineation_db = baseDirectory + "/gisFiles/NHDH" + regionHUC2 + "/arcHydroInput.gdb"

# Define outline file
demOutline = boundaries_db + "/demOutline" + regionHUC2


# =====================
# Water body processing
# =====================
arcpy.env.workspace = sourceFolder
workspaces = arcpy.ListWorkspaces("*", "FileGDB")

toMergeHUC4 = []
for j in range(len(workspaces)): 

	# Get HUC4 ID
	split1 = workspaces[j].split("\\NHDH")[1]
	huc4 = split1.split(".gdb")[0]	
	
	# 390 = LakePond, 436 = Reservoir, 493 = Estuary
	arcpy.FeatureClassToFeatureClass_conversion (workspaces[j] + "/Hydrography/NHDWaterbody", 
													processing_db, 
													"openWater" + "_" + huc4, 
													""" "FType" = 390 OR 
														"FType" = 436 OR 
														"FType" = 493 """)										
														
	toMergeHUC4.append(str(processing_db + "/openWater_" + huc4))

# Merge and re-project waterbodies
rawWaterbodies = arcpy.Merge_management(toMergeHUC4, 
											processing_db + "/rawAllWaterbodies" + regionHUC2)

mergedWaterbodies  =  arcpy.Project_management(rawWaterbodies, 
												processing_db + "/allWaterbodies" + regionHUC2, 
												demOutline)				
																													

# Trim to DEM boundary
arcpy.MakeFeatureLayer_management(mergedWaterbodies, "allWaterbodiesLyr")

arcpy.SelectLayerByLocation_management ("allWaterbodiesLyr", 
											"COMPLETELY_WITHIN",
											demOutline)

allWBs = arcpy.FeatureClassToFeatureClass_conversion ("allWaterbodiesLyr", 
														processing_db, 														
														"waterbodies" + regionHUC2)

# Calculate area field								
arcpy.AddField_management       (allWBs, "AreaSqKM", "DOUBLE")
arcpy.CalculateField_management (allWBs, "AreaSqKM", "!SHAPE.AREA@SQUAREKILOMETERS!", "PYTHON_9.3")


arcpy.FeatureClassToFeatureClass_conversion (allWBs, 
												delineation_db, 
												"largeWaterbodies" + regionHUC2, 
												""" "AreaSqKM" >= """ + str(minAreaSqKM) )								

											
# Delete processing files
# -----------------------
arcpy.Delete_management(mergedWaterbodies)		
arcpy.Delete_management(rawWaterbodies)
arcpy.Delete_management("allWaterbodiesLyr")

for i in range(len(toMergeHUC4)):
	arcpy.Delete_management(toMergeHUC4[i])		
