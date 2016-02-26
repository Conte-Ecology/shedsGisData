# Outdated corrections that have been incorporated into post processing scripts

# =============
# Define Inputs
# =============
# Parent project directory
baseDirectory = "C:/KPONEIL/HRD/V2"

# List all hydro regions processed
hydroRegions = ['01', '02', '03', '04', '05', '06']

# List buffer distances
bufferDistancesM = ['50', '100', '200']


# ===========
# Directories
# ===========
hydrography_db = baseDirectory + "/products/hydrography.gdb"

riparian_db = baseDirectory + "/products/riparianBuffers.gdb"

# Arc Hydro vectors geodatabase
riparianCorr_db = baseDirectory + "/products/riparianBufferCorrections.gdb"
if not arcpy.Exists(riparianCorr_db): arcpy.CreateFileGDB_management (baseDirectory + "/products", "riparianBufferCorrections", "CURRENT")


# ===========
# Corrections
# ===========
for region in hydroRegions:
	
	# Delete unnecessary fields
	# -------------------------
	catchments = hydrography_db + "/Catchments" + region
	arcpy.DeleteField_management(catchments, 
									"Shape_Leng")
	

	flowlines =  hydrography_db + "/Flowlines" + region
	arcpy.DeleteField_management(flowlines, 
									["Shape_Leng", "SimLnFLag", "InLine_FID", "SmoLnFLag"])	
	
	# Correct the buffer
	for buffer in bufferDistancesM:

		newRip = arcpy.FeatureClassToFeatureClass_conversion(riparian_db + "/riparianBufferDetailed" + buffer + "m_" + region,
																riparianCorr_db, 
																"riparianBufferDetailed" + buffer + "m_" + region,
																"""NOT(FEATUREID_1 = 0)""")

		# Adjust name of FEATUREID field
		arcpy.AddField_management(newRip, 
									"FEATUREID", 
									"DOUBLE")

		arcpy.CalculateField_management(newRip, 
											"FEATUREID", 
											"!FEATUREID_1!", 
											"PYTHON")

		arcpy.DeleteField_management(newRip, 
										"FEATUREID_1")	
	