# Buffer script


baseDirectory = "C:/KPONEIL/HRD/V2"

products_db = "C:/KPONEIL/HRD/V2/products/NHDHRDV2.gdb"

workspace_db = baseDirectory + "/workspace.gdb"

# List all hydro regions processed
hydroRegions = ['01', '02', '03', '04', '05', '06']

bufferDistancesM = ['50', '100', '200']


for region in hydroRegions:

	flowlines = products_db + "/smoothedFlowlines" + region

	catchments = products_db + "/Catchments" + region
	
	for buffer in bufferDistancesM:

		streamBuffer = arcpy.Buffer_analysis(flowlines, 
												workspace_db + "/rawBuffer" + buffer + "m_" + region, 
												buffer, 
												"FULL", 
												"ROUND", 
												"NONE")
		
		intersect = arcpy.Intersect_analysis ([streamBuffer, catchments], 
												workspace_db + "/intersectCatBuf" + buffer + "m_" + region, 
												"ALL", 
												"", "")
		
		selection = arcpy.FeatureClassToFeatureClass_conversion(intersect, 
																	workspace_db, 
																	"intersectSelectCatBuf" + buffer + "m_" + region,
																	"""FEATUREID = FEATUREID_1""")
					
		arcpy.Dissolve_management(selection,
									products_db + "/riparianBuffer" + buffer + "m_" + region,
									"FEATUREID", 
									"#",
									"MULTI_PART",
									"DISSOLVE_LINES")