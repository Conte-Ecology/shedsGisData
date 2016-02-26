# SHEDS Data
============

This repo documents the steps used to generate the supporting data used on SHEDS.


### NHDHRDV2 Desctiption 
Version 2 of the National Hydrography Dataset High Resolution Delineation (NHDHRDV2) is a series of GIS layers representing hydrologic catchments and flowlines spanning the Northeast region of the United States. The catchments are similar to existing products such as the well-known NHD Plus dataset. Catchments are based on the National Hydrography Dataset (NHD) and contain fields to indicate routing paths which can be used to establish the network structure. Some basic information about the layers is also included in the attribute tables. Layers representing riparian buffer zones in each catchment are developed as well.

The NHDHRDV2 seeks to address specific aspects of existing hydrography products that have proven to restrict their usefulness. Specifically, improved spatial resolution and consistency are the focus of the development of these products. Catchment delineation is based on the high resolution NHD flowlines. Currently, there are no known large scale catchment products derived from this more detailed dataset. The purpose of this product is to capture small headwater streams omitted by existing products such as the medium resolution catchments in NHDPlus Version 2. Representing these streams can be critical to understanding key ecological interests. Figure 1 shows the added catchment detail from the high resolution streams in the Westbrook stream in Whately, MA.

![Figure 1](https://cloud.githubusercontent.com/assets/6216239/13364134/22316bc8-dc9b-11e5-93f9-3d1d0db73fb0.png)

Figure 1 

Resolution consistency is addressed in the creation of the high resolution catchments. The NHD Plus Version 2 catchments, derived from the medium resolution NHD flowlines, are unnaturally inconsistent in area. The inconsistency is evidenced in Figure 2, which shows a regional view of the catchments. The unnatural catchment area differential shows up as a straight line between lighter and darker shades, indicating lesser and greater density of catchments respectively. These inconsistencies permeate the entire dataset and are a result of the varying resolution of existing hydrography data in the region. The areal inconsistency presents a problem for models relying on drainage area as a driver as well as for visual representation of data layers. 

![Figure 2](https://cloud.githubusercontent.com/assets/6216239/13364586/9ddedc0e-dc9d-11e5-8f8c-7b7126654b8a.png)

Figure 2

The issue shown above in the medium resolution layers also exists in the high resolution flowlines. It is evident from examining the flowline layers that the dataset has been processed in a gridded format at differing resolutions. A methodology for improving areal consistency of the catchments has been developed. The hydrography layers created by this method are derived a 30m resolution digital elevation model and the NHD high resolution flowlines. The high resolution flowlines edited by the Designing Sustainable Landscapes (DSL) Project to eliminate network gaps, correct flow direction, and remove coastline form the majority of the flowline layer used. Raw NHD flowlines were edited in general accordance with the DSL Project methodolgoy to produce whole watersheds that are not artificially split along poltical boundaries. (ADD IMAGE)


* 6 Hydrologic regions

The final products adhere to an established areal consistency while managing to include higher resolution streams than the medium resolution products. 


All citations are in the "NHDHRDV2 Documentation.doc" file.

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