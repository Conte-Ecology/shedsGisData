rm(list=ls())

# Catchment Stats Generator
library(dplyr)
library(reshape2)

# ======
# Inputs 
# ======
inputsFilePath <- "C:/KPONEIL/GitHub/projects/shedsData/basinCharacteristics/zonalStatistics/INPUTS_NHDHRDV2_RIPARIAN.txt"

# There are 3 options for specifying the variables to output:
#   1) "ALL" will include all of the variables present in the folder
#   2) NULL will include the variables from the "rasterList" object in the inputs file
#   3) Manually list the variables to output
outputVariables <- c("ALL")

activateThreshold <- TRUE

missingDataThreshold <- 80

conversionFactorFilePath <- "C:/KPONEIL/GitHub/projects/shedsData/basinCharacteristics/Covariate Data Status - High Res Delineation.csv"

# ========================
# Read user-defined inputs
# ========================
source(inputsFilePath)


# ==================
# Conversion Factors
# ==================
# Read the conversion factors file
conversionFactors <- read.csv(conversionFactorFilePath)[,c("Name", "Conversion.Factor")]

# Rename columns
names(conversionFactors) <- c("variable", "factor")

# ======================
# Group stats for output
# ======================
options(scipen=999)

for (catchmentsFileName in catchmentsFileNames) {

  # Set the directory where the tables are located
  rTablesDirectory <- file.path(baseDirectory, "versions", outputName, "rTables", catchmentsFileName)

  if(is.null(outputVariables)){outputVariables <- c(discreteRasters, continuousRasters)}

  # Local
  # -----
  
  # Create list of variables to compile
  if ( all(outputVariables %in% "ALL" == TRUE) ){
    localStatFiles <- list.files(path = rTablesDirectory, pattern = "local_")  
    
  }else{
    localStatFiles <- c()
    
    for( LF in seq_along(outputVariables) ){
      localStatFiles <- c(localStatFiles, list.files(path = rTablesDirectory, pattern = paste0("local_",outputVariables[LF] ) ) )
    }
  }


  # Loop through files. Pull data and join together for output.
  for ( L in seq_along(localStatFiles) ){
    
    # Print status
    print(L)
    
    # Read in CSV
    localTemp <- read.csv(file.path(rTablesDirectory, localStatFiles[L]) )
    
    # If the percent of the area with data does not meet the threshold, then convert to NA
    if ( "percentAreaWithData" %in% names(localTemp) & activateThreshold ){
      localTemp[which(localTemp$percentAreaWithData < missingDataThreshold), "MEAN"] <- NA
      
      localTemp <- select(localTemp, -percentAreaWithData)
    }
    
    # Get file name
    A <- gsub("*local_", "", localStatFiles[L])
    variableName <- gsub(paste0("*_", statType,".csv"), "", A)
    variableName <- gsub(paste0("*.csv"), "", variableName)
  
    # Rename the columns. Account for the variables without the "percentAreaWithData" metric
    if(ncol(localTemp) == 3) {names(localTemp) <- c(zoneField, variableName, paste0(variableName, "_percentAreaWithData"))} else(names(localTemp) <- c(zoneField, variableName))
    
    # Pull the variable specifc factor
    factor <- filter(conversionFactors, variable == variableName)%>%
                select(factor)
    
    # Account for missing factors  
    if(is.na(as.numeric(factor))) {
      print(paste0("Factor missing for '", variableName, "'. Assigning a default factor of 1."))
      factor <- 1
    }
    
    # Multiply the raw variable value by the conversion factor
    localTemp[,names(localTemp) == variableName] <- localTemp[,names(localTemp) == variableName]*as.numeric(factor)
    
    # Join to main dataframe
    if( L == 1) {LocalStats <- localTemp} else(LocalStats <- left_join(LocalStats, localTemp, by = zoneField) )
  }

  # Upstream
  # --------
  
  # Create list of variables to compile
  if ( all(outputVariables %in% "ALL" == TRUE) ){
    upstreamStatFiles <- list.files(path = rTablesDirectory, pattern = "upstream_")
  }else{
    upstreamStatFiles <- c()
    
    for( UF in seq_along(outputVariables) ){
      upstreamStatFiles <- c(upstreamStatFiles, list.files(path = rTablesDirectory, pattern = paste0("upstream_",outputVariables[UF] ) ) )
    }
  }

  # Loop through files. Pull data and join together for output.
  for ( U in 1:length(upstreamStatFiles) ){
    
    # Print status
    print(U)
    
    # Read in CSV  
    upstreamTemp <- read.csv(file.path(rTablesDirectory, upstreamStatFiles[U]) )
    
    # If the percent of the area with data does not meet the threshold, then convert to NA
    if ( "percentAreaWithData" %in% names(upstreamTemp) & activateThreshold ){
      upstreamTemp[which(upstreamTemp$percentAreaWithData < missingDataThreshold), "MEAN"] <- NA
      
      upstreamTemp <- select(upstreamTemp, -percentAreaWithData)
    }
    
    # Get file name
    A <- gsub("*upstream_", "", upstreamStatFiles[U])
    variableName <- gsub(paste0("*_", statType,".csv"), "", A)
    variableName <- gsub(paste0("*.csv"), "", variableName)
    
    # Rename the columns. Account for the variables without the "percentAreaWithData" metric
    if(ncol(upstreamTemp) == 3) {names(upstreamTemp) <- c(zoneField, variableName, paste0(variableName, "_percentAreaWithData"))}
      else(names(upstreamTemp) <- c(zoneField, variableName))
    
    # Pull the variable specific factor
    factor <- filter(conversionFactors, variable == variableName)%>%
      select(factor)
    
    # Account for missing factors
    if(is.na(as.numeric(factor))) {
      print(paste0("Factor missing for '", variableName, "'. Assigning a default factor of 1."))
      factor <- 1
    }
    
    # Multiply the raw variable value by the conversion factor
    upstreamTemp[,names(upstreamTemp) == variableName] <- upstreamTemp[,names(upstreamTemp) == variableName]*as.numeric(factor)
    
    # Join to main dataframe
    if( U == 1) {UpstreamStats <- upstreamTemp} else(UpstreamStats <- left_join(UpstreamStats, upstreamTemp, by = zoneField) )
  }

  # Format for Database
  # -------------------
  
  locLong <- melt(LocalStats,'FEATUREID')
  locLong$zone <- "local"
  
  upLong <- melt(UpstreamStats,'FEATUREID')
  upLong$zone <- "upstream"
  
  dbStats <- rbind(locLong, upLong)
  
  
  names(dbStats) <- tolower(names(dbStats))
  
  # make sure columns are correctly named and ordered
  stopifnot(all(names(dbStats) == c('featureid', 'variable', 'value', 'zone')))
  
  dbStats$featureid <-format(dbStats$featureid, scientific = FALSE) 
  
  write.csv(dbStats, 
              file = file.path(baseDirectory, "versions", outputName, "completedStats", paste0("zonalStatsForDB_", catchmentsFileName,".csv") ),
              row.names = FALSE)
}



