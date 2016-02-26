# SHEDS Data
============

This repo documents the steps used to generate the supporting data used on SHEDS.


### NHDHRDV2 Desctiption 
Is this where we want to store the documentation for this product?



### Daymet Climate Record
This section takes advantage of the gridded daily surface weather and 
climatological summaries known as [Daymet](https://daymet.ornl.gov/). 
A daily timeseries is assigned to all catchments in the NHDHRDV2 for 
all climate variables over the entire record (1980-2014). The 
[Daymet repository](https://github.com/Conte-Ecology/shedsData/tree/master/daymet) 
documents the process for assigning the climate records to each hydrologic 
catchment in the NHDHRDV2. 


### Basin Characteristics
This section assigns a variety of attributes from different sources to the 
hydrologic catchments in the NHDHRDV2. The basin characteristics are spatially 
attributed to the zonal catchment layers through a series of ArcPy and R scripts. 
Varying source data structures are processed to create uniformly structured 
value raster layers that are attributed to the individual catchments and 
aggregated to larger basins based on the network structure of the delineation
product. The [Basin Characteristics repository](https://github.com/Conte-Ecology/shedsData/tree/master/basinCharacteristics) 
provides an in depth description of the processing steps and the different 
characteristics assigned. 


### Tidal Influence Layer
The tidal influence layer represents all water bodies within the SHEDS spatial 
range that experience some form of tidal effect. Spatial layers from the 
[U.S. Fish & Wildlife Service - National Wetlands Inventory](http://www.fws.gov/wetlands/Data/Mapper.html) 
are processed to generate a spatial polygon layer of all of the tidal zones. 
The processing documentation exists in the [Tidal Layer repo](https://github.com/Conte-Ecology/shedsData/tree/master/tidalLayer). 
This layer is primarily used to flag observed stream temperature sites that may 
be influenced by tides.


### Impoundment Influence Layer
The impoundment influence layer is developed to represent the stream sections 
within the SHEDS hydrologic network that are impacted by impoundments. The 
impoundment location dataset comes from the DSL Project. The locations from 
The Nature Conservancy's dam inventory were snapped to the NHD high resolution 
flowlines. This source layer is not public and the resulting layer is only used 
within the SHEDS group. The processing documentation exists in the 
[Impoundments repo](https://github.com/Conte-Ecology/shedsData/tree/master/impoundments). 

## Contact Info
Kyle O'Neil
koneil@usgs.gov