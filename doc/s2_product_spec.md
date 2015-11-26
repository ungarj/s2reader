## Sentinel Product Specification

To get more information on the data format, please be refered to the official
Sentinel 2 [Product Specification](https://www.google.at/url?sa=t&rct=j&q=&esrc=s&source=web&cd=2&cad=rja&uact=8&sqi=2&ved=0CCQQFjABahUKEwjB_5i834rIAhWDwxQKHRtVDdI&url=https%3A%2F%2Fsentinel.esa.int%2Fdocuments%2F247904%2F349490%2FS2_MSI_Product_Specification.pdf&usg=AFQjCNEI-gxDbhIpFaDPXq1e1NEZNRHoSQ&sig2=aUy9lsNqJlgCF3PLrA1vbQ&bvm=bv.103073922,d.bGQ). Also, have a look at the [tiling
scheme](https://github.com/ungarj/mapdocs/blob/master/geojson/sentinel_tiles.geojson) used by Sentinel 2.

The following sections shall give a short overview on selected terms. Parts of the text are from the aforementioned [Product Specification](https://www.google.at/url?sa=t&rct=j&q=&esrc=s&source=web&cd=2&cad=rja&uact=8&sqi=2&ved=0CCQQFjABahUKEwjB_5i834rIAhWDwxQKHRtVDdI&url=https%3A%2F%2Fsentinel.esa.int%2Fdocuments%2F247904%2F349490%2FS2_MSI_Product_Specification.pdf&usg=AFQjCNEI-gxDbhIpFaDPXq1e1NEZNRHoSQ&sig2=aUy9lsNqJlgCF3PLrA1vbQ&bvm=bv.103073922,d.bGQ).

### User Product

A **User Product** is a collection of **Product Data Items (PDI)**. The **User Product** is delivered according to a user defined Area Of Interest (AOI) and a defined selection of User Product Components. It is packaged as a **SAFE** (Standard Archive Format for Europe) product.

### Product Data Item (PDI)

A PDI can be the actual *image* as well as *ancillary* or *auxilliary* data and respective *metadata*. It is the minimum indivisible partition of one S2 User Product. It is *self standing*, *atomic*, includes all *processing-related data* and can be *univocally identified*.

PDI elements can be:
* image data
* image metadata
* image quality reports including quality data indicators and quality checks
* auxiliary data
* satellite ancillary data
* preview image data

### Granule/Tile

Depending on the AOI, the User Product is composed by **Granules** (or Tiles for L1C). A Granule is the minimum indivisible (geographical) partition of a User Product. It also includes all possible spectral bands.

As we are focusing on L1C data, the terms "**Granule**" and "**Tile**" describe the same.

All Tiles intersecting or touching the AOI of the user are provided into the final User Product. Tiles have a fixed size of 100x100 km.
