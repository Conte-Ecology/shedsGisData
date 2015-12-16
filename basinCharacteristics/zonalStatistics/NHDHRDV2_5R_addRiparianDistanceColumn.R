rm(list=ls())

# ======
# Inputs 
# ======

directory <- "C:/KPONEIL/GitHub/projects/basinCharacteristics/zonalStatistics/versions/NHDHRDV2/completedStats"

fileNames <- c("zonalStatsForDB_riparianBufferDetailed50ft_01",
               "zonalStatsForDB_riparianBufferDetailed50ft_02",
               "zonalStatsForDB_riparianBufferDetailed50ft_03",
               "zonalStatsForDB_riparianBufferDetailed50ft_04",
               "zonalStatsForDB_riparianBufferDetailed50ft_05",
               "zonalStatsForDB_riparianBufferDetailed50ft_06")


bufferValue <- 50


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