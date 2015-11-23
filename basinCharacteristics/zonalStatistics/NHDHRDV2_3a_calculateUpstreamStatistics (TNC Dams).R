rm(list=ls())

# ==============
# Load libraries
# ==============
library(reshape2)
library(foreign)
library(tcltk)
library(dplyr)
library(lazyeval)

#===============
# Specify Inputs
#===============
inputsFilePath <- "C:/KPONEIL/GitHub/projects/shedsData/basinCharacteristics/zonalStatistics/INPUTS_NHDHRDV2.txt"

barrierStatsFilePath <- 'C:/KPONEIL/GitHub/projects/basinCharacteristics/tncDams/outputTables/barrierStats_NHDHRDV2.dbf'

missingDataFilePath <- 'C:/KPONEIL/GitHub/projects/basinCharacteristics/tncDams/outputTables/barrierStatsNAs_NHDHRDV2.dbf'

# ==========
# Load files
# ==========

# User inputs
# -----------
source(inputsFilePath)

# Barrier statistics
# ------------------
barrierStatsMaster <- read.dbf(barrierStatsFilePath)


# ==================
# Edit Barrier Stats
# ==================

# Remove extra column
barrierStatsMaster <- barrierStatsMaster[,- which(names(barrierStatsMaster) %in% "FREQUENCY")]

# Index zone column
zoneCol <- which(names(barrierStatsMaster) %in% zoneField )

# Rename columns to lowercase
names(barrierStatsMaster)[-zoneCol] <- tolower(names(barrierStatsMaster)[-zoneCol])

# Summ all barrier types
barrierStatsMaster$deg_barr_all <- rowSums (barrierStatsMaster[,-1], na.rm = TRUE, dims = 1)

# Barrier type count
numBarriers <- ncol(barrierStatsMaster) - 1


# Missing Data
# ------------
barrierStatsNAs <- read.dbf(missingDataFilePath)
missingDataZones <- barrierStatsNAs[,zoneField]

barrierStatsMaster[which(barrierStatsMaster[,zoneField] %in% missingDataZones), - zoneCol] <- NA



# Loop through all catchments files
for (catchmentsFileName in catchmentsFileNames) {

  # Load catchments networks
  # ------------------------
  load(file.path(baseDirectory, "versions", outputName, "delineatedCatchments", paste0("Delineation_", catchmentsFileName,".RData")))
  
  # Catchment Areas
  # ---------------
  # Local
  vectorArea <- read.csv(file.path(baseDirectory, "versions", outputName, "rTables", catchmentsFileName, paste0("local_AreaSqKM.csv")))  
  
  # List the zone IDs for splitting dataset
  zoneIDs <- unique(vectorArea[,c(zoneField)])
  
  barrierStats <- barrierStatsMaster[which(barrierStatsMaster[,c(zoneField)] %in% zoneIDs),]
  
    
  # ========================
  # Process local statistics
  # ========================
  # Loop through layers, reading files.
  for (b in 1:numBarriers) {
  
    # Separate individual barrier types
    gisStat <- barrierStats[,c(1, b + 1)]
    
    # Specify the output
    outputTable <- file.path(baseDirectory, "versions", outputName, "rTables", catchmentsFileName, paste0("local_", names(gisStat)[2], ".csv"))
    
    # Save the local stat file
    write.csv(gisStat, file = outputTable, row.names = F)
  }


  # ===========================
  # Process upstream statistics
  # ===========================
  
  # Define storage dataframe
  upstreamStats <- data.frame(matrix(NA, nrow = length(zoneIDs), ncol = numBarriers + 1))
  names(upstreamStats) <- names(barrierStats)


  # Catchments loop
  # ---------------
  progressBar <- tkProgressBar(title = "progress bar", min = 0, max = length(zoneIDs), width = 300)
  for ( m in seq_along(zoneIDs)){  
  
    # Get features in current basin
    features <- delineatedCatchments[[which(names(delineatedCatchments) == zoneIDs[m])]]
    
    # Get individual catchment stats for current basin
    catchStats <- filter_(barrierStats, interp(~col %in% features, col = as.name(zoneField)))
     
    # Sum the weighted stats to get final values
    outStats <- colSums(catchStats, na.rm = T)
   
    # Upstream stats
    upstreamStats[m,1]                     <- zoneIDs[m]
    upstreamStats[m,2:ncol(upstreamStats)] <- outStats[-1]
    
    # Progress bar update
    setTkProgressBar(progressBar, m, label=paste( round(m/length(zoneIDs)*100, 2), "% done"))
  }
  close(progressBar)


  # Output upstream statistics tables
  # ---------------------------------
  
  # Loop through variables writing tables with total number of dams upstream 
  for ( n in 2:(ncol(upstreamStats))){
    
    # Name
    colName <- names(upstreamStats)[n]
    
    # Output dataframe
    upStat <- upstreamStats[,c(zoneField, colName)]
  
    # Write out file
    write.csv(upStat, 
              file = file.path(baseDirectory, "versions", outputName, "rTables", catchmentsFileName, paste0("upstream_", colName, ".csv")),
              row.names = F)
  }
  
} # End catchments file loop