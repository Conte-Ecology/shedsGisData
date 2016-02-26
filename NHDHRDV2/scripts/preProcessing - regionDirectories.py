# =============
# Define Inputs
# =============
# Parent project directory
baseDirectory = "C:/KPONEIL/HRD/V2"

# Hydrologic region being processed
regionHUC2 = "01"


# ==================
# Create Directories
# ==================

# Parent Folders
# --------------
# GIS files directory
gis_directory = baseDirectory + "/gisFiles"
if not arcpy.Exists(gis_directory): arcpy.CreateFolder_management(baseDirectory, "gisFiles")

# Product files directory
product_directory = baseDirectory + "/products"
if not arcpy.Exists(product_directory): arcpy.CreateFolder_management(baseDirectory, "products")


# Delineation Processing
# ----------------------
# Hydro region directory
region_directory = baseDirectory + "/gisFiles/NHDH" + regionHUC2
if not arcpy.Exists(region_directory): arcpy.CreateFolder_management(baseDirectory + "/gisFiles", "NHDH" + regionHUC2)

# Arc hydro processing directory
arcHydro_directory = region_directory + "/arcHydro"
if not arcpy.Exists(arcHydro_directory): arcpy.CreateFolder_management(region_directory, "arcHydro")

# Arc Hydro vectors geodatabase
vectors_db = arcHydro_directory + "/vectors.gdb"
if not arcpy.Exists(vectors_db): arcpy.CreateFileGDB_management (arcHydro_directory, "vectors", "CURRENT")

# Processing files geodatabase
processing_db = region_directory + "/processing.gdb"
if not arcpy.Exists(processing_db): arcpy.CreateFileGDB_management (region_directory, "processing", "CURRENT")

# Boundary file geodatabase
boundaries_db = region_directory + "/boundaries.gdb"
if not arcpy.Exists(boundaries_db): arcpy.CreateFileGDB_management (region_directory, "boundaries", "CURRENT")

# Arc Hydro input geodatabase
arcHydroInput_db = region_directory + "/arcHydroInput.gdb"
if not arcpy.Exists(arcHydroInput_db): arcpy.CreateFileGDB_management (region_directory, "arcHydroInput", "CURRENT")

# Post-delineation processing geodatabase
postProcessing_db = region_directory + "/postProcessing.gdb"
if not arcpy.Exists(postProcessing_db): arcpy.CreateFileGDB_management (region_directory, "postProcessing", "CURRENT")


# Post Processing Directories
# ---------------------------
# Main post-processing directory
postProcessing_directory = gis_directory + "/postProcessing"
if not arcpy.Exists(postProcessing_directory): arcpy.CreateFolder_management(gis_directory + "/postProcessing")

# Post-processing Edits geodatabase
edits_db = postProcessing_directory + "/Edits.gdb"
if not arcpy.Exists(edits_db): arcpy.CreateFileGDB_management (postProcessing_directory, "Edits", "CURRENT")


# Product Directories
# -------------------
# Product geodatabase
products_db = product_directory + "/hydrography.gdb"
if not arcpy.Exists(products_db): arcpy.CreateFileGDB_management (product_directory, "NHDHRDV2", "CURRENT")