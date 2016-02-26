# =============
# Define Inputs
# =============

# Parent project directory
baseDirectory = "C:/KPONEIL/HRD/V2"

# Hydrologic region being processed
regionHUC2 = "01"

# Directory containing the high resolution NHD folders
nhdDirectory = "F:/KPONEIL/SourceData/NHDplus/NHDHighres"

# Layer defining the projection to use
projectionDefinitionFile = "F:/KPONEIL/SourceData/topography/umass/dem"

# The DSL streams layer
streamsFile = "F:/KPONEIL/SourceData/topography/Topography_UMASS/dataInNortheast.gdb/allstreams"


# ==============
# Pre-processing
# ==============
# Define directories
sourceFolder = nhdDirectory + "/NHDH" + regionHUC2

processing_db  = baseDirectory + "/gisFiles/NHDH" + regionHUC2 + "/processing.gdb"
boundaries_db  = baseDirectory + "/gisFiles/NHDH" + regionHUC2 + "/boundaries.gdb"
delineation_db = baseDirectory + "/gisFiles/NHDH" + regionHUC2 + "/arcHydroInput.gdb"

# Define outline file
demOutline = boundaries_db + "/demOutline" + regionHUC2

# ==========================
# Process streams from UMass
# ==========================
arcpy.MakeFeatureLayer_management(streamsFile, "streamsLyr")

arcpy.SelectLayerByLocation_management ("streamsLyr", 
											"INTERSECT", 
											demOutline)

umassStreams = arcpy.FeatureClassToFeatureClass_conversion("streamsLyr", 
																processing_db , 
																"umassStreams" + regionHUC2)
															
													
arcpy.Delete_management("streamsLyr")
												

# ===============================
# Process streams in missing area
# ===============================

missingDEMSource = boundaries_db + "/missingDEMZone" + regionHUC2

# Check missingDEMZone
count =  int(arcpy.GetCount_management(missingDEMSource).getOutput(0)) 

if count > 0:

	arcpy.env.workspace = sourceFolder
	workspaces = arcpy.ListWorkspaces("*", "FileGDB")

	# Project missing area boundary to NHD streams projection
	missingDEMZone = arcpy.Project_management(missingDEMSource, 
												processing_db + "/missingDEMZoneNHDHPrj", 
												workspaces[0] + "/Hydrography/NHDFlowline")												
													
	toMergeHUC4 = []
	for j in range(len(workspaces)):

		# Get HUC4 ID
		split1 = workspaces[j].split("\\NHDH")[1]
		huc4 = split1.split(".gdb")[0]	
		
		arcpy.MakeFeatureLayer_management(workspaces[j] + "/Hydrography/NHDFlowline", 
											"flowlineLyr")

		arcpy.SelectLayerByLocation_management ("flowlineLyr", 
													"INTERSECT", 
													missingDEMZone)

		
		# Remove certain FTypes (566 = Coastline, 428 = Pipeline)
		arcpy.FeatureClassToFeatureClass_conversion ("flowlineLyr",
														processing_db,
														"missingStreams_" + huc4,
														""" NOT("FType" = 566 OR
																"FType" = 428) """)

		toMergeHUC4.append(str(processing_db + "/missingStreams_" + huc4))

		arcpy.Delete_management("flowlineLyr")
		

	# Merge and re-project 
	rawStreams = arcpy.Merge_management(toMergeHUC4, 
												processing_db + "/rawMissingStreams" + regionHUC2)

	mergedStreams  =  arcpy.Project_management(rawStreams, 
												processing_db + "/missingStreams" + regionHUC2, 
												umassStreams)	

												
	#missingDissolve = arcpy.Dissolve_management(mergedStreams, 
	#											processing_db + "/missingStreamsDissolve" + regionHUC2,
	#											"", "", 
	#											"SINGLE_PART", 
	#											"")											
												
	print("Once the missing streams layer has been created, manually check it for isolated stream segments. Where obvious, connect these to the network, otherwise delete them.")



# ==================================									
# Combine all stream layers and edit
# ==================================
if count > 0:
	rawStreams = arcpy.Merge_management([umassStreams, mergedStreams], 
											processing_db + "/allStreams" + regionHUC2)	
else: 	
	rawStreams = arcpy.FeatureClassToFeatureClass_conversion(umassStreams, 
																processing_db, 
																"allStreams" + regionHUC2)									



