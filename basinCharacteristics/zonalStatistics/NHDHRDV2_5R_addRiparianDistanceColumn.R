rm(list=ls())

# ======
# Inputs 
# ======

directory <- "C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics/versions/NHDHRDV2/completedStats"

fileNames <- c("zonalStatsForDB_Catchments01",
               "zonalStatsForDB_Catchments02",
               "zonalStatsForDB_Catchments03",
               "zonalStatsForDB_Catchments04",
               "zonalStatsForDB_Catchments05",
               "zonalStatsForDB_Catchments06")


bufferValue <- NA


# ============
# Update Files
# ============

for (file in fileNames){
  
  currentFile <- read.csv(file.path(directory, paste0(file, ".csv")))
  
  currentFile$riparian_distance_ft <- bufferValue
  
  write.csv(currentFile, 
            file = file.path(directory, paste0(file, ".csv")),
            row.names = FALSE)
}