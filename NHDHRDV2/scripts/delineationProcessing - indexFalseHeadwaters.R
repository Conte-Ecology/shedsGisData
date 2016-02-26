rm(list = ls())

library(foreign)


# =============
# Define Inputs
# =============

# Set the hydro region
regionHUC2 = '01'

# If this is the initial run, set run = 1. If checking results, set run = 2
run <- 1


# ==========
# Intial Run
# ==========

if (run == 1){
  
  lines <- read.dbf(paste0("C:/KPONEIL/HRD/V2/gisFiles/NHDH", regionHUC2, "/arcHydro/Layers/DrainageLine", regionHUC2, ".dbf"))
  
  # Mark the false headwater segments
  lines$remove <- 0
  lines$remove[(lines$Shape_Leng <= 90 & !lines$HydroID %in% lines$NextDownID)] <- 1
  
  lines$RasterVal <- 1
  
  # Export the columns to join back to the "DrainageLine" layer
  linesOut <- lines[,c('HydroID', 'remove', 'RasterVal')]
  write.dbf(linesOut, file = paste0("C:/KPONEIL/HRD/V2/gisFiles/NHDH", regionHUC2, "/arcHydro/Layers/DrainageLine", regionHUC2, "_FalseHeadwaters.dbf"))
}

# =============
# Check Results
# =============
if (run == 2){
  
  lines <- read.dbf(paste0("C:/KPONEIL/HRD/V2/gisFiles/NHDH", regionHUC2, "/arcHydro/Layers/DrainageLineFinal", regionHUC2, ".dbf"))
  
  # Mark the false headwater segments
  lines$remove <- 0
  lines$remove[(lines$Shape_Leng <= 90 & !lines$HydroID %in% lines$NextDownID)] <- 1
  
  lines$RasterVal <- 1
  
  # Export the columns to join back to the "DrainageLine" layer
  linesOut <- lines[,c('HydroID', 'remove', 'RasterVal')]
  
  x <- linesOut[(which(linesOut$remove == 1)),]
  
  print(x)
}