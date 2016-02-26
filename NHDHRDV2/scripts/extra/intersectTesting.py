
streamBuffer = "C:/KPONEIL/HRD/V2/test.gdb/bufferLayer"
catchments = "C:/KPONEIL/HRD/V2/test.gdb/cats"


intersect = arcpy.Intersect_analysis ([streamBuffer, catchments], 
										"C:/KPONEIL/HRD/V2/test.gdb/intersect4", 
										"ALL", 
										"", "")