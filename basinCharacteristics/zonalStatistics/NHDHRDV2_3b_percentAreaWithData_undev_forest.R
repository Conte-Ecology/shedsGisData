rm(list=ls())

# ==============
# Load libraries
# ==============
library(dplyr)


#===============
# Specify Inputs
#===============
inputsFilePath <- "C:/KPONEIL/GitHub/projects/shedsData/basinCharacteristics/zonalStatistics/INPUTS_NHDHRDV2.txt"


# ==========
# Load files
# ==========
source(inputsFilePath)


# ===================================
# Replace percentAreaWithData columns
# ===================================


for (catchmentsFileName in catchmentsFileNames) {

  # Source table folder
  rTablesFilePath <- file.path(baseDirectory, "versions", outputName, "rTables", catchmentsFileName)
  
  
  # Local files
  # -----------
  indLocal <- read.csv(file.path(rTablesFilePath, paste0("local_forest.csv")))[,c(zoneField, "percentAreaWithData")]
  
  depLocal <- read.csv(file.path(rTablesFilePath, paste0("local_undev_forest.csv")))
  
  depLocalOut <- select(depLocal, -percentAreaWithData)%>%
                  left_join(indLocal, by = zoneField)
  
  write.csv(depLocalOut, 
              file = file.path(rTablesFilePath, paste0("local_undev_forest.csv")),
              row.names = F)
  
  
  # Upstream Files
  # --------------
  indUpstream <- read.csv(file.path(rTablesFilePath, paste0("upstream_forest.csv")))[,c(zoneField, "percentAreaWithData")]
  
  depUpstream <- read.csv(file.path(rTablesFilePath, paste0("upstream_undev_forest.csv")))
  
  depUpstreamOut <- select(depUpstream, -percentAreaWithData)%>%
                      left_join(indUpstream, by = zoneField)
  
  write.csv(depUpstreamOut, 
              file = file.path(rTablesFilePath, paste0("upstream_undev_forest.csv")),
              row.names = F)
  
}# End catchments file loop