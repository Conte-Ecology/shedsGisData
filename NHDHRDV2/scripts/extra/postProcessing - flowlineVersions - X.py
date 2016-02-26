import arcpy
from arcpy import env
import arcpy.cartography as CA

# =============
# Define Inputs
# =============
# Parent project directory
baseDirectory = "C:/KPONEIL/HRD/V2"

# List all hydro regions processed
hydroRegions = ['01', '02', '03', '04', '05', '06']


# =================
# Setup directories
# =================
# Arc Hydro vectors geodatabase
workspace_db = baseDirectory + "/workspace.gdb"
if not arcpy.Exists(workspace_db): arcpy.CreateFileGDB_management (baseDirectory, "workspace", "CURRENT")

product_db = baseDirectory + "/products/NHDHRDV2.gdb"


# =================
# Process Flowlines
# =================
for region in hydroRegions:

	# Existing Layers
	# ===============
	flowlines = product_db + "/Flowlines" + region

	highResLines = baseDirectory + "/gisFiles/NHDH" + region + "/arcHydroInput.gdb/delineationStreams" + region
	
	catchments = product_db + "/Catchments" + region
	
	# Truncated Lines
	# ===============
	simplifedLine = CA.SimplifyLine(flowlines, 
										workspace_db + "/simplifyFlowlines" + region, 
										"BEND_SIMPLIFY", 
										"60 Meters",
										"FLAG_ERRORS",
										"KEEP_COLLAPSED_POINTS",
										"CHECK")

	arcpy.SmoothLine_cartography(simplifedLine,
									baseDirectory + "/products/NHDHRDv2.gdb/smoothedFlowlines" + region,
									"PAEK",
									"60 Meters",
									"FIXED_CLOSED_ENDPOINT",
									"FLAG_ERRORS")
	
	arcpy.CalculateField_management(product_db + "/smoothedFlowlines" + region, 
										"LengthKM", 
										"!SHAPE.LENGTH@KILOMETERS!", 
										"PYTHON")




	# The next section is computationally intensive and may throw an error if the system requirements are not sufficient.

	# Detailed Lines
	# ==============
	# Creates one feature per reach
	dissolveLines = arcpy.Dissolve_management(highResLines,
												workspace_db + "/dissolve" + region,
												"#", "#",
												"MULTI_PART",
												"UNSPLIT_LINES")
												
	# Establish link between flowlines and catchments
	intersect = arcpy.Intersect_analysis([dissolveLines, catchments],
											workspace_db + "/intersect" + region,
											"ALL",
											"#",
											"INPUT")

	detail = arcpy.Dissolve_management(intersect,
										product_db + "/DetailedFlowlines" + region,
										"FEATUREID", 
										"#",
										"MULTI_PART",
										"#")											

	arcpy.AddField_management(detail, 
								"LengthKM", 
								"DOUBLE")
										
	arcpy.CalculateField_management(detail, 
										"LengthKM", 
										"!SHAPE.LENGTH@KILOMETERS!", 
										"PYTHON")