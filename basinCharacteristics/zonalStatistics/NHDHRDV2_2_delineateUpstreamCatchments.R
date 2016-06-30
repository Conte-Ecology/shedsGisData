# This script delineates the upstream catchments of the arcHydro output shapefile.

rm(list=ls())

# Load libraries
library(tcltk)
library(foreign)

# ==============
# Specify inputs
# ==============
inputsFilePath <- "C:/KPONEIL/GitHub/projects/shedsGISData/basinCharacteristics/zonalStatistics/INPUTS_NHDHRDV2.1.txt"


# ===========
# Delineation
# ===========

# Directory work
# --------------

# Read user-defined inputs
source(inputsFilePath)

# Create output directory
outputFolderPath <- file.path(baseDirectory, 'versions', outputName, "delineatedCatchments")
if( !file.exists( outputFolderPath ) ){
  dir.create(outputFolderPath)
}


# Loop through files
# ------------------
for (catchmentsFileName in catchmentsFileNames){

  # Define the output file
  outputFilePath <- file.path(outputFolderPath, paste0('Delineation_', catchmentsFileName,'.RData') )
  
  
  #Check the existence of the delineated catchments file, stopping the script if it exists.
  if( !file.exists( outputFilePath ) ){
    
    # Read the catchment attributes
    catchmentData <- read.dbf(file.path(baseDirectory, 'gisFiles/vectors/V2.1/', paste0(catchmentsFileName, '.dbf')) )
    
    # --------------------
    # Delineate catchments
    # --------------------
    
    # Select the catchment IDs
    features <- unique(catchmentData[,c(zoneField)])
    
    # Empty list for saving
    delineatedCatchments <- list()
    
    # Set progress bar
    progressBar <- tkProgressBar(title = "progress bar", min = 0, max = length(features), width = 300)
    
    # Loop through all catchments
    for ( i in 1:length(features)){
    
      segments<-c() #list of flowline segments to save
      queue<-c(features[i]) #queue of flowline segments that need to be traced upstream
      
      while (length(queue)>0) {
        
        # Save all of the segments
        segments<-c(segments,queue)
       
        # Which catchments flow into the ones in the current queue
        queue<-c(catchmentData[catchmentData$NextDownID %in% queue, zoneField])
        
        # Eliminate duplicates
        queue<-unique(queue)
        
        # Eliminates queuing flowlines that have already been added to segments
        queue<-queue[!(queue %in% segments)]
      }# end while loop
      
      # Double check duplicates
      delineatedCatchments[[i]] <-unique(segments)
      names(delineatedCatchments)[i] <- features[i]
      
      setTkProgressBar(progressBar, i, label=paste( round(i/length(features)*100, 2), "% done"))
      
    }# end for loop
    
    close(progressBar)
    
    # Save catchments
    save(delineatedCatchments, file = outputFilePath )
  
  }else("Delineated Catchments file already exists. If this is the desired file there is no need to run this script.")

}# End file loop