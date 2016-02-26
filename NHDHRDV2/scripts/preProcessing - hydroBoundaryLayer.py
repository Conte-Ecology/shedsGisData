# =============
# Define Inputs
# =============

# Parent project directory
baseDirectory = "C:/KPONEIL/HRD/V2"

# Hydrologic region being processed
regionHUC2 = "01"

# Layer defining the projection to use
projectionDefinitionFile = "F:/KPONEIL/SourceData/topography/umass/dem"

# Directory containing the high resolution NHD folders
nhdDirectory = "F:/KPONEIL/SourceData/NHDplus/NHDHighres"


# =================================
# Establish Directories & Workspace
# =================================
sourceFolder = nhdDirectory + "/NHDH" + regionHUC2

boundaries_db = baseDirectory + "/gisFiles/NHDH" + regionHUC2 + "/boundaries.gdb"
processing_db = baseDirectory + "/gisFiles/NHDH" + regionHUC2 + "/processing.gdb"

arcpy.env.workspace = sourceFolder
workspaces = arcpy.ListWorkspaces("*", "FileGDB")

# ===============
# Hydro Boundary
# ===============

# Loop through all HUC4 geodatabases
# ----------------------------------
toMergeHUC4 = []
for j in range(len(workspaces)):

	# Get HUC4 ID
	split1 = workspaces[j].split("\\NHDH")[1]
	huc4 = split1.split(".gdb")[0]
	
	# Select HUC4s that fall in the hydrologic region of interest
	arcpy.FeatureClassToFeatureClass_conversion (workspaces[j] + "/WBD/WBDHU4", 
													processing_db, 
													"hydroBounds_" + huc4, 
													"""	HUC4 LIKE '""" + regionHUC2 + """%' """)
	
	toMergeHUC4.append(str(processing_db + "/hydroBounds_" + huc4))

# Merge and dissolve into one layer
# ---------------------------------
mergeHUCs = arcpy.Merge_management(toMergeHUC4, 
									processing_db + "/mergedHUC4s")
								
rawDissolve = arcpy.Dissolve_management(mergeHUCs, 
											processing_db + "/rawHydroBoundary" + regionHUC2,
											"", "", 
											"MULTI_PART", 
											"")

hydroBoundary =  arcpy.Project_management(rawDissolve, 
											boundaries_db + "/hydroBoundary" + regionHUC2, 
											projectionDefinitionFile)				
																		
# Delete layers
# -------------				
arcpy.Delete_management(mergeHUCs)	
arcpy.Delete_management(rawDissolve)

for i in range(len(toMergeHUC4)):
	arcpy.Delete_management(toMergeHUC4[i])		
