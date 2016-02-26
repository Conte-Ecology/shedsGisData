import arcpy

inputDirectory = "C:/KPONEIL/HRD/V2/products/hydrography.gdb"

outputDirectory = "C:/KPONEIL/HRD/V2/report/tables"


# List all hydro regions processed
hydroRegions = ['01', '02', '03', '04', '05', '06']


for region in hydroRegions:

	arcpy.TableToTable_conversion(inputDirectory + "/Catchments" + region,
									outputDirectory,
									"Catchments" +  region + ".dbf")
	
	arcpy.TableToTable_conversion(inputDirectory + "/Flowlines" + region,
									outputDirectory,
									"Flowlines" + region + ".dbf")