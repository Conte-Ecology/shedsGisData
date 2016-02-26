

inputRaster = "C:/KPONEIL/sideProjects/deerfield/spatialLayers/pDev"



YourOutputRaster = Divide(Float(ZonalStatistics("YourZoneRaster","Value",Int(Times(inputRaster,1000000)),"ALL","DATA")),100)  
