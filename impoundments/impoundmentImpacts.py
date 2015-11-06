# ==============
# Specify Inputs
# ==============
# Directory to write to
baseDirectory = "C:/KPONEIL/SHEDS/impoundments"

# NHDHRDV2 hydrologic regions
hydroRegions = ["01", "02", "03", "04", "05", "06"]

# Length downstream from impoundments to identify (in meters)
zoneDistM = 50

# Maximum distance (in meters) to snap dams to streams. This should 
snapDistanceM = 100

# Full path to the impoundments layer
impoundments = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/connectivity/tnc/TNC Dams - High Resolution Flowlines/Dams_ALL_highres.shp"

for region in hydroRegions:

	# Define layers and directories
	detailedFlowlines = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/streamStructure/NHDHRDV2/products/hydrography.gdb/detailedFlowlines" + region
	regionBoundary = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/streamStructure/NHDHRDV2/products/hydrography.gdb/regionBoundary" + region

	# Create version geodatabase
	workingDirectory = baseDirectory + "/processing" + region + ".gdb"
	if not arcpy.Exists(workingDirectory): arcpy.CreateFileGDB_management (baseDirectory, "processing" + region, "CURRENT")

	
	# ======================
	# Network Pre-processing
	# ======================

	# Select impoundments within the range
	# ------------------------------------
	arcpy.MakeFeatureLayer_management(impoundments, "impoundments_lyr")

	arcpy.SelectLayerByLocation_management ("impoundments_lyr",
												"INTERSECT",
												regionBoundary,
												"", 
												"NEW_SELECTION")

	# Only use "Use = 1" cases										
	selectImpoundments = arcpy.FeatureClassToFeatureClass_conversion("impoundments_lyr", 
																		workingDirectory, 
																		"impoundments",
																		""""Use" = 1""")																					

	arcpy.Delete_management("impoundments_lyr")															
	
	# Re-snap dams to fix cases of altered lines	
	snappedImpoundments = arcpy.Snap_edit(selectImpoundments,
											[[detailedFlowlines, "EDGE", str(snapDistanceM) + " Meters"]])

											
	# Select relevant flowlines
	# -------------------------

	impoundmentBuffers = arcpy.Buffer_analysis(snappedImpoundments, 
												workingDirectory + "/impoundmentBuffers", 
												str(zoneDistM + 50) + " Meters", 
												"FULL",
												"ROUND",
												"NONE")

	arcpy.MakeFeatureLayer_management(detailedFlowlines, "detailedFlowlines_lyr")											
												
	arcpy.SelectLayerByLocation_management ("detailedFlowlines_lyr",
												"INTERSECT",
												impoundmentBuffers,
												"", 
												"NEW_SELECTION")


	selectFlowlines = arcpy.FeatureClassToFeatureClass_conversion("detailedFlowlines_lyr", 
																	workingDirectory, 
																	"selectFlowlines")
												
												
	arcpy.Delete_management("detailedFlowlines_lyr")											
	
	# Segment lines into reaches
	# --------------------------
	dissolveLines = arcpy.Dissolve_management(selectFlowlines,
												workingDirectory + "/flowlines_dissolved",
												"#", "#",
												"MULTI_PART",
												"UNSPLIT_LINES")
			
												
												
	segmentedLines = arcpy.FeatureToLine_management(dissolveLines,
													   workingDirectory + "/flowlines_segmented",
													   "0.001 Meters",
													   "ATTRIBUTES")

	# Specify unique IDs
	arcpy.AddField_management(segmentedLines, "routeID", "LONG")
	arcpy.CalculateField_management (segmentedLines, "routeID", "!OBJECTID!", "PYTHON_9.3")
			
	# Create field for creating routes (ensures correct direction)
	arcpy.AddField_management(segmentedLines, "fromMeas", "SHORT")
	arcpy.CalculateField_management (segmentedLines, "fromMeas", 0, "PYTHON_9.3")

	# Create length field
	arcpy.AddField_management(segmentedLines, "LengthM", "DOUBLE")
	arcpy.CalculateField_management (segmentedLines, "LengthM", "!Shape_Length!", "PYTHON_9.3")
		
	# ==================
	# Linear Referencing	
	# ==================
	
	# Determine positions
	# -------------------
	# Create routes
	routes = arcpy.CreateRoutes_lr(segmentedLines,
										"routeID",
										workingDirectory + "/flowRoutes",
										"TWO_FIELDS",
										"fromMeas",
										"LengthM",
										"", "", "",
										"IGNORE",
										"INDEX")


	# Find the distance of the points along the routes
	locations = arcpy.LocateFeaturesAlongRoutes_lr(snappedImpoundments,
															routes,
															"routeID",
															str(zoneDistM) + " METERS", 
															workingDirectory + "/impoundmentLocations",
															"routeID POINT FMEAS TMEAS",	# <<<<<<<<<<<<<<<<<<<<<<<<< Check that this is correct
															"FIRST",
															"DISTANCE",
															"ZERO",
															"NO_FIELDS", #"FIELDS"
															"M_DIRECTON")
															
		


	# Add route length to event table
	# -------------------------------
	# Calculate length of routes
	arcpy.AddField_management(routes, "routeLengthM", "DOUBLE")
	arcpy.CalculateField_management (routes, "routeLengthM", "!Shape_Length!", "PYTHON_9.3")											
	
	# Copy to events
	arcpy.JoinField_management(locations, "routeID", routes, "routeID", "routeLengthM")													



	# Make the locations a Table View for actions
	arcpy.MakeTableView_management(locations, "locations_tbl")

	# Create field to specify zone end point
	arcpy.AddField_management("locations_tbl", "zoneM", "DOUBLE")


	# Non-confluence points
	# ---------------------
	arcpy.SelectLayerByAttribute_management ("locations_tbl", 
												"NEW_SELECTION", 
												"FMEAS + " + str(zoneDistM) + " <= routeLengthM")

	arcpy.CalculateField_management ("locations_tbl", 
										"zoneM", 
										"!FMEAS! + " + str(zoneDistM), 
										"PYTHON_9.3")

	arcpy.TableToTable_conversion("locations_tbl", 
									workingDirectory, 
									"nonConfluence")									

	# Create impounded zones 
	nonConfluenceZones = arcpy.MakeRouteEventLayer_lr (routes, 
														"routeID" , 
														"nonConfluence", 
														"routeID LINE FMEAS zoneM", 
														"nonConfluenceZones", 
														"#",  
														"NO_ERROR_FIELD", 
														"NO_ANGLE_FIELD")								

	# Convert to feature in geodatabase
	arcpy.FeatureClassToFeatureClass_conversion(nonConfluenceZones, 
													workingDirectory, 
													"nonConfluenceZone")
														
												

	# Confluence points
	# -----------------		
	arcpy.SelectLayerByAttribute_management ("locations_tbl", 
												"SWITCH_SELECTION")

	arcpy.CalculateField_management ("locations_tbl", 
										"zoneM", 
										"!routeLengthM!", 
										"PYTHON_9.3")								
		
	arcpy.TableToTable_conversion("locations_tbl", 
									workingDirectory, 
									"confluence")


	arcpy.Delete_management("locations_tbl")															








	arcpy.MakeTableView_management("confluence", "confluence_tbl")

	arcpy.AddField_management("confluence_tbl", "totalZoneM", "DOUBLE")	
	arcpy.CalculateField_management ("confluence_tbl", "totalZoneM", 0,	"PYTHON_9.3")

	count = 0

	while int(arcpy.GetCount_management("confluence_tbl").getOutput(0)) > 0:

		count = count + 1	
		
		# Make events of downstream zone points
		confluenceZones = arcpy.MakeRouteEventLayer_lr (routes, 
															"routeID" , 
															"confluence_tbl", 
															"routeID LINE FMEAS zoneM", 
															"confluenceZones" + "_" + str(count), 
															"#",  
															"NO_ERROR_FIELD", 
															"NO_ANGLE_FIELD")

		arcpy.FeatureClassToFeatureClass_conversion(confluenceZones, 
														workingDirectory, 
														"confluenceZone" + "_" + str(count))	

		# Create points at end of reaches for marking against confluence locations	
		allConfluencePts = arcpy.FeatureVerticesToPoints_management(confluenceZones,
																	workingDirectory + "/allConfluencePts", 
																	"END")

		# Calculate the total length of the zone through confluences
		arcpy.CalculateField_management (allConfluencePts,
											"totalZoneM",
											"!totalZoneM! + (!zoneM! - !FMEAS!)",
											"PYTHON_9.3")

		selectConfluencePts = arcpy.FeatureClassToFeatureClass_conversion(allConfluencePts, 
																			workingDirectory, 
																			"selectConfluencePts",
																			""" "totalZoneM" < """ + str(zoneDistM))
		
		# Calculate the length of the zone to mark
		arcpy.CalculateField_management (selectConfluencePts, 
											"zoneM", 
											str(zoneDistM) + " - !totalZoneM!", "PYTHON_9.3")

		# New FMEAS	starts from the confluence (start of the line)
		arcpy.CalculateField_management (selectConfluencePts, "FMEAS", 0, "PYTHON_9.3")


		# Update route information
		# ------------------------

		# Delete old fields
		arcpy.DeleteField_management(selectConfluencePts, 
									 ["RouteLengthM", "routeID"])
		
		# Select routes intersecting conluence point
		arcpy.SelectLayerByLocation_management ("flowRoutes",
													"INTERSECT",
													selectConfluencePts,
													"", 
													"NEW_SELECTION")

		# Create points based on start of intersecting routes
		headPts = arcpy.FeatureVerticesToPoints_management("flowRoutes",
															workingDirectory + "/headPts", 
															"START")	

		arcpy.SelectLayerByAttribute_management ("flowRoutes", "CLEAR_SELECTION")												


		
		
		# Join route info based on the head of the downstream point
		spatialJoin = arcpy.SpatialJoin_analysis(selectConfluencePts, 
													headPts, 
													workingDirectory + "/downStreams")

		# Delete old spatial join
		if arcpy.Exists("spatialJoinTable"):
			arcpy.Delete_management(spatialJoinTable)
			
		spatialJoinTable = arcpy.TableToTable_conversion(spatialJoin, 
															workingDirectory, 
															"spatialJoinTable")
				

		arcpy.Delete_management("confluence_tbl")
		
		arcpy.MakeTableView_management(spatialJoinTable, "confluence_tbl")										
													
		arcpy.SelectLayerByAttribute_management ("confluence_tbl", 
													"NEW_SELECTION", 
													"zoneM >= routeLengthM")

		arcpy.CalculateField_management ("confluence_tbl", 
											"zoneM", 
											"!routeLengthM!", 
											"PYTHON_9.3")

		arcpy.SelectLayerByAttribute_management ("confluence_tbl", 
													"CLEAR_SELECTION")

		arcpy.Delete_management(confluenceZones)
		arcpy.Delete_management(allConfluencePts)
		arcpy.Delete_management(selectConfluencePts)
		arcpy.Delete_management(headPts)
		arcpy.Delete_management(spatialJoin)

	
	# Delete table for next iteration	
	arcpy.Delete_management("confluence_tbl")


	# ================
	# Merge zone tiers
	# ================
	
	toMerge = [workingDirectory + "/nonConfluenceZone"]

	for i in range(1, count+1):
		toMerge.append(workingDirectory + "/confluenceZone" + "_" + str(i))

	mergedZones = arcpy.Merge_management(toMerge, 
											workingDirectory + "/allZones")

	arcpy.Dissolve_management(mergedZones, 
								baseDirectory + "/impoundedZones" + str(zoneDistM) + "m_" + region + ".shp",
								"", "", 
								"MULTI_PART", 
								"DISSOLVE_LINES")
								
	arcpy.Delete_management(nonConfluenceZones)	
	arcpy.Delete_management(mergedZones)
								
								
								
								
								
								



							
							
							
							
							
							
							
# >>>>> Make this a while loop to check for continued conluences in series <<<<<<

# 1. Select all streams that intersect the "impoundedZones" points that fall onto confluences (i.e. zone is too short)
# 2. Create points at the start of these lines using "Feature Vertices to Points" tool
# 3. Select the "impoundedZones" points that intersect these "start points"
# 4. Use this connection, along with the zoneM - FMEAS value to determine how much to add on. 












