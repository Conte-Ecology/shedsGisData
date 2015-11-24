Raster Preparation
==================

## Description

This repo houses all of the scripts used to process raw spatial data layers as they are received from the source. These layers are converted to value rasters for assigning attributes to zonal polygons. Each sub-folder contains stand-alone scripts and spatial data sources used to create layers for a user-defined spatial range. The layers created in each sub-repo are defined by the scripting process and not necessarily the data source or the layer definition. For example, multiple sub-repos exist that access the same source layers from SSURGO because the scripting process differs significantly enough to warrant separation. On the other hand, all of the NLCD Land Cover layers come from the same script and thus exist in the same repo.


