import arcpy

# ==============
# Specify Inputs
# ==============

# Directory to write to
baseDirectory = "C:/KPONEIL/SHEDS/impoundments"

# NHDHRDV2 hydrologic regions
hydroRegions = ["01", "02", "03", "04", "05", "06"]

# Length downstream from impoundments to identify (in meters)
zoneDistM = 50

# Maximum distance (in meters) to snap dams to streams. Dams should already be snapped, this ensures they fall on the line.
snapDistanceM = 5

# Full path to the impoundments layer
sourceImpoundments = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/connectivity/tnc/TNC Dams - High Resolution Flowlines/Dams_ALL_highres.shp"



# ======================
# Network Pre-processing
# ======================

# Create version geodatabase
workingDirectory = baseDirectory + "/processing" + str(zoneDistM) + "m.gdb"
if not arcpy.Exists(workingDirectory): arcpy.CreateFileGDB_management (baseDirectory, "processing" + str(zoneDistM) + "m", "CURRENT")

# Create version geodatabase
networkDirectory = baseDirectory + "/network" + str(zoneDistM) + "m.gdb"
if not arcpy.Exists(networkDirectory): arcpy.CreateFileGDB_management (baseDirectory, "network" + str(zoneDistM) + "m", "CURRENT")


arcpy.MakeFeatureLayer_management(sourceImpoundments, "impoundments_lyr")

damsToMerge = []
linesToMerge = []

for region in hydroRegions:

	# Define layers and directories
	detailedFlowlines = "//IGSAGBEBWS-MJO7/projects/dataIn/environmental/streamStructure/NHDHRDV2/products/hydrography.gdb/detailedFlowlines" + region

	# Select impoundments to use
	# --------------------------
	# Within range of flowlines
	arcpy.SelectLayerByLocation_management ("impoundments_lyr",
												"WITHIN_A_DISTANCE",
												detailedFlowlines,
												str(snapDistanceM) + " Meters", 
												"NEW_SELECTION")											
												
	# Limit to "Use = 1" cases (see source documentation)									
	selectImpoundments = arcpy.FeatureClassToFeatureClass_conversion("impoundments_lyr", 
																		networkDirectory, 
																		"impoundments_" + region,
																		""""Use" = 1""")																																				
	
	# Re-snap dams to fix cases of altered lines	
	snappedImpoundments = arcpy.Snap_edit(selectImpoundments,
											[[detailedFlowlines, "EDGE", str(snapDistanceM) + " Meters"]])
		
	damsToMerge.append(networkDirectory + "/impoundments_" + region)		
	
	
	# Select flowlines near dams
	# --------------------------
	arcpy.MakeFeatureLayer_management(detailedFlowlines, "detailedFlowlines_lyr")											
												
	arcpy.SelectLayerByLocation_management ("detailedFlowlines_lyr",
												"WITHIN_A_DISTANCE",
												snappedImpoundments,
												str(zoneDistM*1.5) + " Meters", 
												"NEW_SELECTION")	
		
	selectFlowlines = arcpy.FeatureClassToFeatureClass_conversion("detailedFlowlines_lyr", 
																	networkDirectory, 
																	"selectFlowlines_" + region)		
			
	linesToMerge.append(networkDirectory + "/selectFlowlines_" + region)	

	arcpy.Delete_management("detailedFlowlines_lyr")



arcpy.Delete_management("impoundments_lyr")


# Create full-range layers																		
mergedDams = arcpy.Merge_management(damsToMerge, 
										networkDirectory + "/impoundments")	

mergedLines = arcpy.Merge_management(linesToMerge, 
										networkDirectory + "/flowlines")	
	
	
	
# Segment lines into reaches
# --------------------------
dissolveLines = arcpy.Dissolve_management(mergedLines,
												networkDirectory + "/flowlines_dissolved",
												"#", "#",
												"MULTI_PART",
												"UNSPLIT_LINES")
			
segmentedLines = arcpy.FeatureToLine_management(dissolveLines,
													   networkDirectory + "/flowlines_segmented",
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

#mergedDams = networkDirectory + "/impoundments"
#segmentedLines = networkDirectory + "/flowlines_segmented"


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
locations = arcpy.LocateFeaturesAlongRoutes_lr(mergedDams,
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




# A) zoneM is the end point of the route event calculation. For the confluence affected zones,
#		this is incremental and either equals the total length of the segment or the length 
#		that will get the total zone length (totalZoneM) to the specified value.
# B) totalZoneM is the total length of the zone through the current iteration
# C) FMEAS is the start point along the segment of the next zone (calculated as 0 for any segments
#		downstream of a confluence



# =====================
# Non-confluence points
# =====================
# Locations that do not have a confluence in the downstream impacted zone

arcpy.SelectLayerByAttribute_management ("locations_tbl", 
												"NEW_SELECTION", 
												"FMEAS + " + str(zoneDistM) + " <= routeLengthM")

# zoneM is simply calculated as the start point plus the defined zone distance
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

toMerge = [workingDirectory + "/nonConfluenceZone"]			

										
# =================
# Confluence points
# =================
# Locations that have 1 or more confluence in the downstream impacted zone

arcpy.SelectLayerByAttribute_management ("locations_tbl", 
												"SWITCH_SELECTION")

# Calculate the route length as the end of the segment
arcpy.CalculateField_management ("locations_tbl", 
										"zoneM", 
										"!routeLengthM!", 
										"PYTHON_9.3")
		
confluenceTable = arcpy.TableToTable_conversion ("locations_tbl", 
													workingDirectory, 
													"confluence")
		
arcpy.Delete_management ("locations_tbl")
		
# Field for keeping track of zone length through confluences
arcpy.AddField_management(confluenceTable, "totalZoneM", "DOUBLE")
arcpy.CalculateField_management (confluenceTable, "totalZoneM", 0,	"PYTHON_9.3")
													
													
# Start with all of the points near confluences
arcpy.MakeTableView_management("confluence", "confluence_tbl")


count = 0





# Iterate through confluences
while int(arcpy.GetCount_management("confluence_tbl").getOutput(0)) > 0:

	# Keep track of iterations for layer naming
	count = count + 1
		
	# Make events of downstream zone points
	confluenceZones = arcpy.MakeRouteEventLayer_lr (routes, 
														"routeID", 
														"confluence_tbl", 
														"routeID LINE FMEAS zoneM", 
														"confluenceZones" + "_" + str(count), 
														"#", 
														"NO_ERROR_FIELD", 
														"NO_ANGLE_FIELD")

	# Save zone layer
	currentZone = arcpy.FeatureClassToFeatureClass_conversion(confluenceZones, 
																workingDirectory, 
																"confluenceZone" + "_" + str(count))
	arcpy.Delete_management(confluenceZones)

	# Add the layer to the list to merge
	toMerge.append(workingDirectory + "/confluenceZone" + "_" + str(count))
	
	
	# Delete old location table
	arcpy.Delete_management("confluence_tbl")
	
	# Prepare next iteration
	# ----------------------

	# Select the next segment below the confluence by the following steps:
	#	1) Add up the total length of the impacted zone through this iteration
	# 	2) Select incomplete zones for continued processing
	#	3) Create points at the end of the incomplete zones
	#	4) Select the flow routes that intersect with the incomplete zone end points
	#	5) Create points at the upstream end of these selected flow routes
	#	6) Select next iteration of routes (via spatial join between incomplete zone end points and flow route start points)


	# Calculate the total length of the zone through confluences (FMEAS = start, zoneM = end)
	arcpy.CalculateField_management (currentZone,
										"totalZoneM",
										"!totalZoneM! + (!zoneM! - !FMEAS!)",
										"PYTHON_9.3")

	incompleteZones = arcpy.FeatureClassToFeatureClass_conversion(currentZone, 
																	workingDirectory, 
																	"incompleteZones" + "_" + str(count),
																	""" "totalZoneM" < """ + str(zoneDistM))
	
	# Create points at end of zones for marking against confluence locations	
	zoneEndPoint = arcpy.FeatureVerticesToPoints_management(incompleteZones,
																workingDirectory + "/zoneEndPoint" + "_" + str(count), 
																"END")
		
	# Calculate the length of the zone to mark (zone distance - current running total)
	arcpy.CalculateField_management (zoneEndPoint, 
										"zoneM", 
										str(zoneDistM) + " - !totalZoneM!", "PYTHON_9.3")

	# New FMEAS	starts from the confluence (start of the line, FMEAS = 0)
	arcpy.CalculateField_management (zoneEndPoint, "FMEAS", 0, "PYTHON_9.3")



	# Select the next downstream segment
	# ----------------------------------
	
	# Delete old fields
	arcpy.DeleteField_management(zoneEndPoint, 
									 ["RouteLengthM", "routeID"])
		
	# Select routes intersecting confluence point
	arcpy.SelectLayerByLocation_management ("flowRoutes",
												"INTERSECT",
												zoneEndPoint,
												"", 
												"NEW_SELECTION")

	# Create points based on start of intersecting routes
	confluencePoints = arcpy.FeatureVerticesToPoints_management("flowRoutes",
																	workingDirectory + "/confluencePoints" + "_" + str(count), 
																	"START")	

	arcpy.SelectLayerByAttribute_management ("flowRoutes", "CLEAR_SELECTION")												

	
	# Join downstream route info to the incomplete zone based on overlapping confluence points
	nextSegments = arcpy.SpatialJoin_analysis(zoneEndPoint, 
													confluencePoints, 
													workingDirectory + "/nextSegments" + "_" + str(count),
													"JOIN_ONE_TO_MANY")


	nextSegmentsTable = arcpy.TableToTable_conversion(nextSegments, 
															workingDirectory, 
															"nextSegmentsTable" + "_" + str(count))

	with arcpy.da.UpdateCursor(nextSegmentsTable, ["zoneM", "routeLengthM"]) as cursor:
		for row in cursor:
			if row[0] >= row[1]:
				row[0] = row[1]
			cursor.updateRow(row)	

	
	# Create new location table for next iteration	
	arcpy.MakeTableView_management(nextSegmentsTable, "confluence_tbl")										




# ================
# Merge zone tiers
# ================

mergedZones = arcpy.Merge_management(toMerge, 
										workingDirectory + "/allZones")

finalZones = arcpy.Dissolve_management(mergedZones, 
										baseDirectory + "/impoundedZones" + str(zoneDistM) + "m.shp",
										"", "", 
										"MULTI_PART", 
										"DISSOLVE_LINES")

finalZones = arcpy.Dissolve_management(mergedZones, 
										workingDirectory + "/impoundedZones" + str(zoneDistM) + "m",
										"", "", 
										"MULTI_PART", 
										"DISSOLVE_LINES")
										
										


# Join all connected areas













										
#arcpy.AddField_management(finalZones, "LengthM", "DOUBLE")
#arcpy.CalculateField_management (finalZones, "LengthM", "!shape.length@meters!", "PYTHON_9.3")












# >>>>> Make this a while loop to check for continued conluences in series <<<<<<

# 1. Select all streams that intersect the "impoundedZones" points that fall onto confluences (i.e. zone is too short)
# 2. Create points at the start of these lines using "Feature Vertices to Points" tool
# 3. Select the "impoundedZones" points that intersect these "start points"
# 4. Use this connection, along with the zoneM - FMEAS value to determine how much to add on. 











