rm(list=ls())

# ==============
# Load libraries
# ==============
library(reshape2)
library(foreign)
library(tcltk)
library(dplyr)
library(lazyeval)


# ==============
# Specify inputs
# ==============
inputsFilePath <- "C:/KPONEIL/GitHub/projects/shedsData/basinCharacteristics/zonalStatistics/INPUTS_NHDHRDV2.txt"

# ==========
# Load files
# ==========

# User inputs
# -----------
source(inputsFilePath)

rasterList <- c(discreteRasters, continuousRasters)

# If one of the raster lists is empty, remove the NA
if ("NA" %in% rasterList) {
  rasterList <- rasterList[-which(rasterList == "NA")]
}


# Loop through catchment shapefiles (by hydrologic region)
for (catchmentsFileName in catchmentsFileNames) {
  

  # Create output directory
  # -----------------------
  outputFolderPath <- file.path(baseDirectory, "versions", outputName, "rTables", catchmentsFileName)
  if( !file.exists( outputFolderPath ) ){
    dir.create(outputFolderPath)
  }
  
  
  # Load Catchment networks
  # -----------------------
  load(file.path(baseDirectory, "versions", outputName, "delineatedCatchments", paste0("Delineation_", catchmentsFileName, ".RData")))
  
  
  # ==============
  # Drainage Areas
  # ==============
  # The areas based on the vectors are saved as the areas, though the raster areas are used to define the percentage of area with data. 
  #   These areas match up with the data layers which
  
  # Vector
  # ------
  # Input file
  vectorFile <- file.path(baseDirectory, 'gisFiles/vectors', paste0(catchmentsFileName, '.dbf'))
  
  # Output filepath (local)
  areaFileLocal <- file.path(outputFolderPath, paste0("local_AreaSqKM.csv"))
  
  # If the area file doesn't exist, write it. Else load it.
  if (!file.exists(areaFileLocal)) {
    
    # Read the catchment attributes
    vectorArea <- read.dbf(vectorFile)[,c(zoneField, "AreaSqKM")]
    
    # Save file
    write.csv(vectorArea, file = areaFileLocal, row.names = F)
  } else {vectorArea <- read.csv(areaFileLocal)}
  
  
  # Raster
  # ------
  rasterArea <- read.dbf(file.path(baseDirectory,"versions", outputName, "gisTables", catchmentsFileName, "catRasterAreas.dbf"))[,c(zoneField, "AreaSqKM")]
  #names(rasterArea)[2] <- "AreaSqKM"
  
  
  # ========================
  # Process local statistics
  # ========================
  # Loop through layers, reading files.
  for (j in 1:length(rasterList)) {
  
    # File path to table
    tableFilePath <- file.path(baseDirectory,"versions", outputName, "gisTables", catchmentsFileName, paste0(rasterList[j], ".dbf"))
    
    # Open table
    dbfTable <-read.dbf(tableFilePath)[,c(zoneField, statType, "AREA")]
    dbfTable$AREA <- dbfTable$AREA*0.000001 # convert to square kilometers
    dbfTable[which(dbfTable[,statType] == -9999), statType] <- NA # Replace all "-9999" values with "NA"
    
    # Output filepath
    outputTable <- file.path(outputFolderPath, paste0("local_", rasterList[j], ".csv"))
    
    if (!file.exists(outputTable)){
    
      # Calculate the % of the catchment area with data and include in the output
      gisStat <- left_join(dbfTable, rasterArea, by = zoneField) %>%
                    mutate(percentAreaWithData = AREA/AreaSqKM*100)%>%
                    select(-c(AREA, AreaSqKM))
      
   
      # save this as a file
      write.csv(gisStat, file = outputTable, row.names = F)
    }
    
    # Prep dataframes for upstream averaging
    # --------------------------------------
    # Data
    dat <- dbfTable[,c(zoneField, statType)]
    names(dat)[2] <- rasterList[j]
    if (j == 1) {
      zonalData <- dat
    } else (zonalData <- left_join(zonalData, dat, by = zoneField))
  
    # Areas
    wt <- dbfTable[,c(zoneField, "AREA")]
    names(wt)[2] <- rasterList[j]
    if (j == 1) { 
      zonalAreas <- wt 
    } else (zonalAreas <- left_join(zonalAreas, wt, by = zoneField))
  }
  
  
  
  
  # ===========================
  # Process upstream statistics
  # ===========================
  
  # Define features to compute
  featureList <- zonalData[,zoneField]
  
  # Define storage dataframes
  # -------------------------
  
  # Upstream stats
  upstreamStats <- data.frame(matrix(NA, nrow = length(featureList), ncol = length(rasterList) + 1))
  names(upstreamStats) <- c(zoneField, rasterList)
  
  # Areas with data
  pcntUpstreamWithData <- data.frame(matrix(NA, nrow = length(featureList), ncol = length(rasterList) + 1))
  names(pcntUpstreamWithData) <- c(zoneField, rasterList)
  
  # Upstream area (from vector)
  areaFileUpstream <- file.path(outputFolderPath, paste0("upstream_AreaSqKM.csv"))
  
  # If Upstream area file doesn't exist, calculate it based on the vectors
  if (!file.exists(areaFileUpstream)) {
    upstreamArea <- data.frame(matrix(NA, nrow = length(featureList), ncol = 2))
    names(upstreamArea) <- c(zoneField, "AreaSqKM")
  }
  
  
  # Catchments loop
  # ---------------
  progressBar <- tkProgressBar(title = "progress bar", min = 0, max = length(featureList), width = 300)
  for (m in seq_along(featureList)) {  
  
    # Get features in current basin
    features <- delineatedCatchments[[which(names(delineatedCatchments) == featureList[m])]]
    
    # Sum the areas of the individual catchments in the basin (raster version)
    TotDASqKM <- sum(filter_(rasterArea, interp(~col %in% features, col = as.name(zoneField)))$AreaSqKM)
    
    # Get individual catchment stats for current basin
    catchStats <- filter_(zonalData, interp(~col %in% features, col = as.name(zoneField)))#%>%
    
    # Get individual catchment areas with data for current basin
    catchAreas <- filter_(zonalAreas, interp(~col %in% features, col = as.name(zoneField)))#%>%
  
    # Calculate the weights of each element in the dataframe (creates a matching dataframe)
    weights <- sweep(catchAreas, 2, colSums(catchAreas), `/`)
    
    # Weight the values by area
    weightedStats <- catchStats*weights
      
    # Sum the weighted stats to get final values. (Account for the case where all values are NA, preventing it from returning a 0)
    outStats <- colSums(weightedStats, na.rm=TRUE) + ifelse(colSums(is.na(weightedStats)) == nrow(weightedStats), NA, 0)
  
    # Get the percentage of catchment area with data
    outAreas <- colSums(catchAreas)/TotDASqKM
    
    # Account for the rare case of catchments area = 0 (product of rasterizing catchments polygons)
    if (TotDASqKM == 0) {
      outStats[2:length(outStats)] <- NA
      outAreas[2:length(outAreas)] <- 0
    }
    
    # Upstream stats
    upstreamStats[m,1]                     <- featureList[m]
    upstreamStats[m,2:ncol(upstreamStats)] <- outStats[-1]
    
    # Area with data
    pcntUpstreamWithData[m,1]                     <- featureList[m]
    pcntUpstreamWithData[m,2:ncol(upstreamStats)] <- outAreas[-1]
    
    
    # Total drainage area
    # -------------------
    # This is calculated based on the vector file
    if (!file.exists(areaFileUpstream)) {
      upstreamArea[m,1] <- featureList[m]
      upstreamArea[m,2] <- sum(filter_(vectorArea, interp(~col %in% features, col = as.name(zoneField)))$AreaSqKM, na.rm = T)
    }
    
    # Progress bar update
    setTkProgressBar(progressBar, m, label=paste( round(m/length(featureList)*100, 2), "% done"))
  }
  close(progressBar)
  
  # Output upstream statistics tables
  # ---------------------------------
  
  # Loop through variables writing tables with upstream data and the percent of the area with data
  for (n in 2:(ncol(upstreamStats))) {
    
    # Name
    colName <- names(upstreamStats)[n]
    
    # Output dataframe
    upStat <- upstreamStats[,c(zoneField, colName)]
    names(upStat)[2] <- statType
    
    upPcnt <- pcntUpstreamWithData[,c(zoneField, colName)]
    upPcnt[,2] <- upPcnt[,2]*100
    names(upPcnt)[2] <- "percentAreaWithData" 
    
    up <- left_join(upStat, upPcnt, by = zoneField)
  
    outputUpstream  <- file.path(outputFolderPath, paste0("upstream_", colName, ".csv"))
    write.csv(up, file = outputUpstream,  row.names = F)
  }
  
  # Save area file
  if (!file.exists(areaFileUpstream)) {
    write.csv(upstreamArea, file = areaFileUpstream, row.names = F)
  }

} # End catchments file loop