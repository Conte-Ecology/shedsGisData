rm(list = ls())

library(foreign)
library(dplyr)

# =============
# Define Inputs
# =============

baseDirectory <- "C:/KPONEIL/HRD/V2"

hydroRegions <- c("01")
#hydroRegions <- c("01", "02", "03", "04", "05", "06")

run <- 1

# ===============
# Quality Control
# ===============

allCats <- NULL
allStreams <- NULL

# Loop through all hydrologic regions
for ( R in seq_along(hydroRegions) ){
  
  if ( run == 1 ){
    # Load attributes tables
    cats <- read.dbf(paste0(baseDirectory, "/gisFiles/NHDH", hydroRegions[R], "/allCatchments", hydroRegions[R], ".dbf"))
    streams <- read.dbf(paste0(baseDirectory, "/gisFiles/NHDH", hydroRegions[R], "/allFlowlines", hydroRegions[R], ".dbf"))
  }
  
  
  if ( run == 2 ){
    # Load attributes tables
    cats <-    read.dbf(paste0(baseDirectory, "/products/shapefiles/Catchments", hydroRegions[R], ".dbf"))
    streams <- read.dbf(paste0(baseDirectory, "/products/shapefiles/Flowlines",  hydroRegions[R], ".dbf"))
  }
  
  errors <- data.frame(paste0(X = character(0)), 
                        stringsAsFactors = FALSE)
  colnames(errors) <- paste0("Errors for Hydrologic Region ", hydroRegions[R])

  
  # Check for duplicate FEATUREIDs
  # ------------------------------
  if ( nrow(cats)    != length(unique(cats$FEATUREID   )) ) { errors[nrow(errors) + 1,] <- c("Duplicate catchments exist.")}
  if ( nrow(streams) != length(unique(streams$FEATUREID)) ) { errors[nrow(errors) + 1,] <- c("Duplicate streams exist."   )}
  
  ?data.frame
  
  # Ensure all streams have a catchment
  # -----------------------------------
  if ( !all(streams$FEATUREID %in% cats$FEATUREID) ) { errors[nrow(errors) + 1,] <- c("Some streams do not have an associated catchment.")}
  
  
  # Ensure all NextDownIDs are existing features
  # --------------------------------------------
  # Catchments
  x <- cats$NextDownID[which(cats$NextDownID != -1)] 
  if( !all(x %in% cats$FEATUREID) ) { errors[nrow(errors) + 1,] <- c("In the catchments layer, some NextDownIDs do not exist as catchments.")}
  
  # Flowlines
  y <- streams$NextDownID[which(streams$NextDownID != -1)]
  if( !all(y %in% streams$FEATUREID) ) { errors[nrow(errors) + 1,] <- c("In the streams layer, some NextDownIDs do not exist as stream segments.")}
  
  
  # Make sure NextDownIDs didn't get altered incorrectly
  # ----------------------------------------------------
  a <- length(cats$NextDownID == -1)
  b <- length(streams$NextDownID == -1)
  
  d <- length(which(cats$Source == "Coastal Fill"))
  
  
  if (a != b + d) { errors[nrow(errors) + 1,] <- c("The number of headwaters are mismatched.")}

  # Join all tables together
  # ------------------------
  if( is.null(allCats)){
    allCats <- cats}
  else ( allCats <- rbind(allCats, cats))
  
  if( is.null(allStreams)){
    allStreams <- streams}
  else ( allStreams <- rbind(allStreams, streams))
  
  
  if ( nrow(errors) == 0 ){ errors[1,] <- c("No errors found!")}
  
  print(errors)
}


if(length(hydroRegions) > 1){

  # Check if duplicates exist between hydrologic regions
  if ( length(unique(allCats$FEATUREID)) != nrow(allCats) ) { print( "Duplicate FEATUREIDs exist in the catchments layer.")}
  if ( length(unique(allStreams$FEATUREID)) != nrow(allStreams) ) { print( "Duplicate FEATUREIDs exist in the streams layer.")}

}


