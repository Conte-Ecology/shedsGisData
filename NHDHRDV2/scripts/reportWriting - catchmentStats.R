rm(list = ls())

library(foreign)
library(dplyr)

# =============
# Define Inputs
# =============

baseDirectory <- "C:/KPONEIL/HRD/V2"

hydroRegions <- c("01", "02", "03", "04", "05", "06")


# ===============
# Calculate Stats
# ===============

stats <- as.data.frame(matrix(NA, ncol = 7, nrow = 6))

names(stats) <- c("Hydrologic Region",
                  "Number of Catchments", 
                  "Mean Catchment Area", 
                  "Median Catchment Area",
                  "Number of Flowlines",
                  "Mean Flowline Length",
                  "Median Flowline Length")


# Loop through all hydrologic regions
for ( R in seq_along(hydroRegions) ){
  
  # Load attributes tables
  cats <-    read.dbf(paste0(baseDirectory, "/report/tables/Catchments", hydroRegions[R], ".dbf"))
  streams <- read.dbf(paste0(baseDirectory, "/report/tables/Flowlines",  hydroRegions[R], ".dbf"))

  stats[R, 1] <- hydroRegions[R] 
  stats[R, 2] <- nrow(cats)
  stats[R, 3] <- round(mean(cats$AreaSqKM), digits = 2)
  stats[R, 4] <- round(median(cats$AreaSqKM), digits = 2)
  
  stats[R, 5] <- nrow(streams)
  stats[R, 6] <- round(mean(streams$LengthKM), digits = 2)
  stats[R, 7] <- round(median(streams$LengthKM), digits = 2)
}


write.csv(stats, 
          file = paste0(baseDirectory, "/report/layerStats.csv"),
          row.names = F)





