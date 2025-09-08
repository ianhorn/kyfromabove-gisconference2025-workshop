# STAC

## What is a SpatioTemporal Asset Catlog?

Why STAC?

Here are some highlights from the [STAC Spec](https://stacspec.org) landing page.
>>When a user wants to search for all the imagery in their area and time of interest they can’t make just one search — they have to use different tools and connect to API’s that are similar but all slightly different. STAC aims to make that much easier, by providing common metadata to expose geospatial assets.

Space, and Time?

Yes, you can simultaneously query by geography and dates for an area of interest.

But How?

Because STAC is a way to serve earth observation data via its metadata.
>STAC aims to make that much easier, by providing common metadata to expose geospatial assets.

What makes a STAC?

The basic component of a stac are the following:

1. Item
    - data + metadata
    - file location
    - date collected
    - relevant links
        - thumbnails
        - world files
        - viewers

2. Catalog
    - structure or heirarchy
    - groups of child catalogs
    - list of stac items

3. Collection
    - extension of a catalog
    - more metadata
        - date ranges
        - equipment
        - providers
        - more metadata
4. **STAC API**
    - enables the search component
        - [OpenAPI specification](https://swagger.io/specification/)
        - Open Geospatial Consortium [(OGC) WFS3](https://ubuntu.qgis.org/qgisdata/QGIS-Documentation/live/html/en/docs/server_manual/services/ogcapif.html)

## TL;DR

1. The STAC Specification is the common structure that describes and catalogs spatiotemporal Assets.  
2. Items is the basic unit of a catalog
3. Catalogs provide structure
4. Collections are an extension of the catalog that help describe the data or subset of data in a similar manner.  
