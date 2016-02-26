# Buffer script

# =============
# Define Inputs
# =============

baseDirectory = "C:/KPONEIL/HRD/V2"

# List all hydro regions processed
#hydroRegions = ['01', '02']
hydroRegions = ['03', '04', '05', '06']


bufferDistancesM = ['50']#, '100', '200']

# ============
# Set up paths
# ============

products_db = baseDirectory + "/products/NHDHRDV2.gdb"

riparianProducts_db = baseDirectory + "/products/NHDHRDV2_RiparianBufferProcessing.gdb"

workspace_db = baseDirectory + "/workspace.gdb"

# Arc Hydro vectors geodatabase
riparian_db = baseDirectory + "/gisFiles/riparianBuffers.gdb"
if not arcpy.Exists(riparian_db): arcpy.CreateFileGDB_management (baseDirectory + "/gisFiles", "riparianBuffers", "CURRENT")


for region in hydroRegions:

	catchments = arcpy.FeatureClassToFeatureClass_conversion(products_db + "/Catchments" + region, 
																riparian_db, 
																"Catchments" + region)
	
	flowlines = workspace_db + "/intersect" + region
	
	#flowlines = arcpy.FeatureClassToFeatureClass_conversion(workspace_db + "/intersect" + region, 
	#															riparian_db, 
	#															"intersect" + region)
	
	for buffer in bufferDistancesM:

		dissolveByCat = arcpy.Dissolve_management(workspace_db + "/intersect" + region,
													riparian_db + "/dissolveByCat" + region,
													"FEATUREID", 
													"#",
													"MULTI_PART",
													"#")
	
		streamBuffer = arcpy.Buffer_analysis(dissolveByCat, 
												riparian_db + "/dissolveByCatBuffer" + buffer + "m_" + region, 
												buffer, 
												"FULL", 
												"ROUND", 
												"NONE")
												
		# Repair geometry to prevent errors in Union/Intersect tools										
		arcpy.RepairGeometry_management (streamBuffer)										
		arcpy.RepairGeometry_management (catchments)											
												
						
		union = arcpy.Union_analysis([streamBuffer, catchments], 
										riparian_db + "/bufCatUnion" + region,
										"ALL",
										"#",
										"GAPS")
							
		unionSelect = arcpy.FeatureClassToFeatureClass_conversion(union, 
														riparian_db, 
														"unionSelect" + region,
														"""NOT(FEATUREID = 0)""" )

		arcpy.Dissolve_management(unionSelect,
									riparianProducts_db + "/riparianBufferDetailed" + buffer + "m_" + region,
									"FEATUREID_1",
									"#",
									"MULTI_PART",
									"#")

		
		
		
		
		#arcpy.Union_analysis(in_features="C:/KPONEIL/HRD/V2/test.gdb/bufferLayer #;C:/KPONEIL/HRD/V2/test.gdb/cats #",
		#out_feature_class="C:/Users/koneil/Documents/ArcGIS/Default.gdb/bufferLayer_Union",join_attributes="ALL",cluster_tolerance="#",gaps="GAPS")										
												

				
		# works up until this point. Intersect crashes fairly reliably...
				

		
				
		#intersect = arcpy.Intersect_analysis ([streamBuffer2, catchments2], 
		#										workspace_db + "/intersectCatDetailBuf" + buffer + "m_" + region, 
		#										"ALL", 
		#										"", "")		
		
		
		#arcpy.Dissolve_management(selection,
		#							products_db + "/riparianDetailBuffer" + buffer + "m_" + region,
		#							"FEATUREID_1", 
		#							"#",
		#							"MULTI_PART",
		#							"DISSOLVE_LINES")












for region in hydroRegions:

	#flowlines = products_db + "/smoothedFlowlines" + region

	catchments = products_db + "/Catchments" + region
	
	flowlines = workspace_db + "/intersect" + region
	
	
	for buffer in bufferDistancesM:

		dissolveByCat = arcpy.Dissolve_management(workspace_db + "/intersect" + region,
													workspace_db + "/dissolveByCat" + region,
													"FEATUREID", 
													"#",
													"MULTI_PART",
													"#")
	
		streamBuffer = arcpy.Buffer_analysis(dissolveByCat, 
												workspace_db + "/dissolveByCatBuffer" + buffer + "m_" + region, 
												buffer, 
												"FULL", 
												"ROUND", 
												"NONE")
												
		# intersect throws an error in first try
		intersect = arcpy.Intersect_analysis ([streamBuffer, catchments], 
												workspace_db + "/intersectCatDetailBuf" + buffer + "m_" + region, 
												"ALL", 
												"", "")		
		
		
		intersect = arcpy.Intersect_analysis ([streamBuffer, catchments], 
												workspace_db + "/intersectCatDetailBuf" + buffer + "m_" + region, 
												"ALL", 
												"", "")
		
		selection = arcpy.FeatureClassToFeatureClass_conversion(intersect, 
																	workspace_db, 
																	"intersectSelectCatDetailBuf" + buffer + "m_" + region,
																	"""FEATUREID = FEATUREID_1""")
					
		arcpy.Dissolve_management(selection,
									products_db + "/riparianDetailBuffer" + buffer + "m_" + region,
									"FEATUREID", 
									"#",
									"MULTI_PART",
									"DISSOLVE_LINES")