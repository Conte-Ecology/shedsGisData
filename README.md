SHEDS Data
==========

This repo contains scripts used to generate the supporting data used on SHEDS. 
A list of the 




## Daymet

### Repo
`shedsData\daymet`


### Description
The Daymet data are daily time series of climate variables as distributed through 
the [ORNL DAAC](https://daymet.ornl.gov/). The 1km x 1km gridded data from 
1980 - present are spatially assigned to the catchment polygons displayed on SHEDS.
The scripts in this repo do this spatial assignment by using the custom 
[zonalDaymet package](https://github.com/Conte-Ecology/zonalDaymet).




## Basin Characteristics

### Repo
`basinCharacteristics\daymet`

### Description
The basin characteristics are spatially attributed to the zonal catchments through 
series of ArcPy and R scripts. Varying data sources are processed to create uniformly
structured value raster layers that are spatially assigned to the catchments and 
aggregated to larger basins based on the network structure of the delineation
product.



## Tidal Influence

### Repo
`tidalLayer\daymet`

### Description
The tidal influence layer represents all water bodies within the SHEDS spatial 
range that experience some form of tidal effect. The output is spatial polygon 
layer of all of the tidal zones.



## Impoundment Influence

### Repo
`impoundments\daymet`

### Description
The impoundment influence layer is developed to represent the stream sections 
within the SHEDS hydrologic network that are impacted by impoundments. This 
layer is dependent upon a user-specified value representing length downstream 
from an impoundment to be measured. The result is a spatial polyline layer 
representing the segments within the specified length downstream from 
all known impoundments.




