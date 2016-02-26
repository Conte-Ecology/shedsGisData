# ==================
# Define user Inputs
# ==================

# Parent project directory
baseDirectory = "C:/KPONEIL/HRD/V2"

# Hydrologic region being processed
regionHUC2 = "01"

# Product version
version = "2"


# ====================
#   Delineation Zone
# ====================

postProcessing_db = baseDirectory + "/gisFiles/NHDH" + regionHUC2 + "/postProcessing.gdb"


# Copy layers
# -----------
flowlines = arcpy.FeatureClassToFeatureClass_conversion(baseDirectory + "/gisFiles/NHDH" + regionHUC2 + "/arcHydro/vectors.gdb/Layers/DrainageLineFinal" + regionHUC2, 
															postProcessing_db,
															"DrainageLineFinal" + regionHUC2)

catchments = arcpy.FeatureClassToFeatureClass_conversion(baseDirectory + "/gisFiles/NHDH" + regionHUC2 + "/arcHydro/vectors.gdb/Layers/Catchment" + regionHUC2, 
															postProcessing_db,
															"Catchment" + regionHUC2)


# Make feature layers
# -------------------
arcpy.MakeFeatureLayer_management(flowlines, "flowlinesLyr")
arcpy.MakeFeatureLayer_management(catchments, "catchmentsLyr")


# Add fields
# ----------
arcpy.AddField_management("flowlinesLyr", "FEATUREID", "LONG")
arcpy.AddField_management("flowlinesLyr", "Source", "TEXT")

arcpy.AddField_management("catchmentsLyr", "FEATUREID", "LONG")
arcpy.AddField_management("catchmentsLyr", "NextDownID", "LONG")
arcpy.AddField_management("catchmentsLyr", "Source", "TEXT")


# Calculate Fields
# ----------------

# Flowlines
arcpy.CalculateField_management ("flowlinesLyr", "FEATUREID", "!HydroID!", "PYTHON_9.3")
arcpy.CalculateField_management ("flowlinesLyr", "Source", ' "Delineation" ', "VB")


# Catchments
arcpy.AddJoin_management("catchmentsLyr", "GridID", "flowlinesLyr", "GridID")

arcpy.CalculateField_management ("catchmentsLyr", 
									"Catchment" + regionHUC2 + ".FEATUREID",
									"!DrainageLineFinal" + regionHUC2 + ".FEATUREID!",
									"PYTHON_9.3")

arcpy.CalculateField_management ("catchmentsLyr", 
									"Catchment" + regionHUC2 + ".NextDownID", 
									"!DrainageLineFinal" + regionHUC2 + ".NextDownID!", 
									"PYTHON_9.3")									

arcpy.RemoveJoin_management("catchmentsLyr")
									
arcpy.CalculateField_management ("catchmentsLyr", "Source", ' "Delineation" ', "VB")


delineationCatchments = arcpy.CopyFeatures_management("catchmentsLyr", 
														postProcessing_db + "/delineationCatchments" + regionHUC2)
			
delineationFlowlines = arcpy.CopyFeatures_management("flowlinesLyr", 
														postProcessing_db + "/delineationFlowlines" + regionHUC2)					

# Delete Processing Layers														
arcpy.Delete_management("flowlinesLyr")
arcpy.Delete_management("catchmentsLyr")
arcpy.Delete_management(flowlines)
arcpy.Delete_management(catchments)


	
# Get maximum FEATUREID 
maxDelinFIDTable = arcpy.Statistics_analysis(delineationCatchments, 
											postProcessing_db + "/maxDelinFID" + regionHUC2, 
											[["FEATUREID", "MAX"]])
		
field = "MAX_FEATUREID"
cursor = arcpy.SearchCursor(maxDelinFIDTable)
for row in cursor:
    maxDelinFEATUREID = int(row.getValue(field))


if maxDelinFEATUREID >= 5000000: 
	print("Catchment FEATUREID exceeds the threshold for Coastal Catchment FEATUREIDs. Do not proceed without addressing this issue!")






# ============
# Coastal Zone
# ============

flowCoast = baseDirectory + "/gisFiles/NHDH" + regionHUC2 + "/arcHydro/vectors.gdb/Layers/DrainageLineCoast" + regionHUC2

catCoast = baseDirectory + "/gisFiles/NHDH" + regionHUC2 + "/arcHydro/vectors.gdb/Layers/CatchmentCoast" + regionHUC2

fillCoast = baseDirectory + "/gisFiles/NHDH" + regionHUC2 + "/arcHydro/vectors.gdb/Layers/CatchmentFill" + regionHUC2


if arcpy.Exists(flowCoast) + arcpy.Exists(catCoast) + arcpy.Exists(fillCoast): runCoastal = True
else: runCoastal = False


if runCoastal == True:

	# Copy layers
	# -----------
	flowlines = arcpy.FeatureClassToFeatureClass_conversion(flowCoast, 
																postProcessing_db,
																"DrainageLineCoast" + regionHUC2)

	catchments = arcpy.FeatureClassToFeatureClass_conversion(catCoast, 
																postProcessing_db,
																"CatchmentCoast" + regionHUC2)

	fillCatchments = arcpy.FeatureClassToFeatureClass_conversion(fillCoast, 
																	postProcessing_db,
																	"CatchmentFill" + regionHUC2)


	# Make feature layers
	# -------------------
	arcpy.MakeFeatureLayer_management(flowlines, "flowlinesLyr")
	arcpy.MakeFeatureLayer_management(catchments, "catchmentsLyr")
	arcpy.MakeFeatureLayer_management(fillCatchments, "fillLyr")


	# Add fields
	# ----------
	arcpy.AddField_management("flowlinesLyr", "FEATUREID", "LONG")
	arcpy.AddField_management("flowlinesLyr", "Source", "TEXT")

	arcpy.AddField_management("catchmentsLyr", "FEATUREID", "LONG")
	arcpy.AddField_management("catchmentsLyr", "NextDownID", "LONG")
	arcpy.AddField_management("catchmentsLyr", "Source", "TEXT")

	arcpy.AddField_management("fillLyr", "FEATUREID", "LONG")
	arcpy.AddField_management("fillLyr", "NextDownID", "LONG")
	arcpy.AddField_management("fillLyr", "Source", "TEXT")


	# Calculate Fields
	# ----------------

	# Flowlines
	arcpy.CalculateField_management ("flowlinesLyr", "FEATUREID", """ [HydroID] + """ + str(maxDelinFEATUREID), "VB")
	arcpy.CalculateField_management ("flowlinesLyr", "Source", ' "Coastal" ', "VB")

	arcpy.SelectLayerByAttribute_management ("flowlinesLyr", "NEW_SELECTION", "NOT(NextDownID = -1)")
	arcpy.CalculateField_management ("flowlinesLyr", "NextDownID", """ [NextDownID] + """ + str(maxDelinFEATUREID), "VB")
	arcpy.SelectLayerByAttribute_management ("flowlinesLyr", "CLEAR_SELECTION")



	# Catchments
	arcpy.AddJoin_management("catchmentsLyr", "GridID", "flowlinesLyr", "GridID")

	arcpy.CalculateField_management ("catchmentsLyr", 
										"CatchmentCoast" + regionHUC2 + ".FEATUREID",
										"!DrainageLineCoast" + regionHUC2 + ".FEATUREID!",
										"PYTHON_9.3")

	arcpy.CalculateField_management ("catchmentsLyr", 
										"CatchmentCoast" + regionHUC2 + ".NextDownID", 
										"!DrainageLineCoast" + regionHUC2 + ".NextDownID!", 
										"PYTHON_9.3")									

	arcpy.RemoveJoin_management("catchmentsLyr")
										
	arcpy.CalculateField_management ("catchmentsLyr", "Source", ' "Coastal" ', "VB")


	# Get maximum FEATUREID 
	maxCoastFIDTable = arcpy.Statistics_analysis("catchmentsLyr", 
												postProcessing_db + "/maxCoastalFID" + regionHUC2, 
												[["FEATUREID", "MAX"]])
			
	field = "MAX_FEATUREID"
	cursor = arcpy.SearchCursor(maxCoastFIDTable)
	for row in cursor:
		maxFEATUREID = int(row.getValue(field))



	# Coastal Fill Layer	
		
	# FEATUREID field
	arcpy.CalculateField_management ("fillLyr", "FEATUREID", """ [OBJECTID] + """ + str(maxFEATUREID), "VB")
	arcpy.CalculateField_management ("fillLyr", "NextDownID", -1, "PYTHON_9.3")						
	arcpy.CalculateField_management ("fillLyr", "Source", ' "Coastal Fill" ', "VB")								
								
						
																				
												
	allCoastalCatchments = arcpy.Merge_management(["catchmentsLyr", "fillLyr"], 
														postProcessing_db + "/allCoastalCatchments" + regionHUC2)									
																		
	allCoastalFlowlines = arcpy.CopyFeatures_management("flowlinesLyr", 
															postProcessing_db + "/allCoastalFlowlines" + regionHUC2)					
														
															
															
	# Delete Processing Layers														
	arcpy.Delete_management("flowlinesLyr")
	arcpy.Delete_management("catchmentsLyr")
	arcpy.Delete_management("fillLyr")
	arcpy.Delete_management(flowlines)
	arcpy.Delete_management(catchments)
	arcpy.Delete_management(fillCatchments)




	# Merge sections
	# --------------
	allCatchments = arcpy.Merge_management([delineationCatchments, allCoastalCatchments], 
														postProcessing_db + "/Catchments" + regionHUC2)	

	allFlowlines = arcpy.Merge_management([delineationFlowlines, allCoastalFlowlines], 
														postProcessing_db + "/Flowlines" + regionHUC2)														
else:													
	allCatchments = arcpy.CopyFeatures_management(delineationCatchments, 
															postProcessing_db + "/Catchments" + regionHUC2)			
	allFlowlines  = arcpy.CopyFeatures_management(delineationFlowlines, 
															postProcessing_db + "/Flowlines" + regionHUC2)	




# =================
# Adjust FEATUREIDs
# =================
# Adjust the FEATUREIDs to be unique to hydro region and product version

# Catchments
# ==========
catLayerID = "allCatchments" + regionHUC2
arcpy.MakeFeatureLayer_management(allCatchments, catLayerID)

# FEATUREIDs
# ----------
# Add the version and hydro region to the FEATUREID
arcpy.AddField_management(catLayerID, "FIDtext", "TEXT")
arcpy.CalculateField_management(catLayerID, "FIDtext", version + regionHUC2 + '!FEATUREID!', "PYTHON_9.3")


# NextDownIDs
# -----------
arcpy.AddField_management(catLayerID, "NDIDtext", "TEXT")

# Calculate cases with a downstream catchment
arcpy.SelectLayerByAttribute_management (catLayerID, "NEW_SELECTION", "NOT(NextDownID = -1)")
arcpy.CalculateField_management(catLayerID, "NDIDtext", version + regionHUC2 + '!NextDownID!', "PYTHON_9.3")

# Calculate cases without a downstream catchment
arcpy.SelectLayerByAttribute_management (catLayerID, "NEW_SELECTION", "NextDownID = -1")
arcpy.CalculateField_management(catLayerID, "NDIDtext", '!NextDownID!', "PYTHON_9.3")
arcpy.SelectLayerByAttribute_management (catLayerID, "CLEAR_SELECTION")


# Copy to shapefiles
# ------------------
arcpy.FeatureClassToShapefile_conversion(catLayerID,
											baseDirectory + "/gisFiles/NHDH" + regionHUC2)

catchmentShapefile = baseDirectory + "/gisFiles/NHDH" + regionHUC2 + "/" + catLayerID + ".shp"
																
# FEATUREID
arcpy.DeleteField_management(catchmentShapefile, "FEATUREID")									 
arcpy.AddField_management(catchmentShapefile, "FEATUREID", "LONG", 15)
arcpy.CalculateField_management(catchmentShapefile, "FEATUREID", '!FIDtext!', "PYTHON_9.3")

# NextDownID
arcpy.DeleteField_management(catchmentShapefile, "NextDownID")
arcpy.AddField_management(catchmentShapefile, "NextDownID", "LONG", 15)
arcpy.CalculateField_management(catchmentShapefile, "NextDownID", '!NDIDtext!', "PYTHON_9.3")



# Flowlines
# ==========
streamLayerID = "allFlowlines" + regionHUC2
arcpy.MakeFeatureLayer_management(allFlowlines, streamLayerID)


# FEATUREIDs
# ----------
# Add the version and hydro region to the FEATUREID
arcpy.AddField_management(streamLayerID, "FIDtext", "TEXT")
arcpy.CalculateField_management(streamLayerID, "FIDtext", version + regionHUC2 + '!FEATUREID!', "PYTHON_9.3")

# NextDownIDs
# -----------
arcpy.AddField_management(streamLayerID, "NDIDtext", "TEXT")

# Calculate cases with a downstream catchment
arcpy.SelectLayerByAttribute_management (streamLayerID, "NEW_SELECTION", "NOT(NextDownID = -1)")
arcpy.CalculateField_management(streamLayerID, "NDIDtext", version + regionHUC2 + '!NextDownID!', "PYTHON_9.3")

# Calculate cases without a downstream catchment
arcpy.SelectLayerByAttribute_management (streamLayerID, "NEW_SELECTION", "NextDownID = -1")
arcpy.CalculateField_management(streamLayerID, "NDIDtext", '!NextDownID!', "PYTHON_9.3")
arcpy.SelectLayerByAttribute_management (streamLayerID, "CLEAR_SELECTION")



# Copy to shapefile
# -----------------																
arcpy.FeatureClassToShapefile_conversion(streamLayerID,
											baseDirectory + "/gisFiles/NHDH" + regionHUC2)
										 
flowlineShapefile = baseDirectory + "/gisFiles/NHDH" + regionHUC2 + "/" + streamLayerID + ".shp"										 
										 
# FEATUREID
arcpy.DeleteField_management(flowlineShapefile, "FEATUREID")									 
arcpy.AddField_management(flowlineShapefile, "FEATUREID", "LONG", 15)
arcpy.CalculateField_management(flowlineShapefile, "FEATUREID", '!FIDtext!', "PYTHON_9.3")

# NextDownID
arcpy.DeleteField_management(flowlineShapefile, "NextDownID")
arcpy.AddField_management(flowlineShapefile, "NextDownID", "LONG", 15)
arcpy.CalculateField_management(flowlineShapefile, "NextDownID", '!NDIDtext!', "PYTHON_9.3")


										 
# Delete Fields
# -------------
# Catchments
deleteCatFields = ["HydroID", "GridID", "Id", "gridcode", "ORIG_FID", "FIDtext", "NDIDtext"]
arcpy.DeleteField_management(catchmentShapefile,
								deleteCatFields)

# Flowlines
deleteFlowFields = ["arcid", "from_node", "to_node", "HydroID", "GridID", "FIDtext", "NDIDtext"]
arcpy.DeleteField_management(flowlineShapefile, 
								deleteFlowFields)