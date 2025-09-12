#!/usr/bin/env python
# coding: utf-8

# # DGI/KyFromAbove Workshop
# #### Getting Started
# 
# September 23, 2025
# Kentucky GIS Conference
# Fun Exploration of KyFromAbove with Python and other Tools
# 
# Let's get started using a notebook.  If you are using MyBinder to run this notebook, the environment is mostly set up already.  You may need to install some packages using `%pip install <module>`

# ## Some basic code
# 
# Import python modules/packages/libraries . .  whatever.  Let's make sure our code works.

# In[ ]:


import os
from leafmap import Map                # interactive mapping in Python
import geopandas as gpd                # working with geospatial data in Python
from pystac_client import Client       # STAC API clientimport
import pdal                            # lidar processing in Python
import json
import rasterio                        # raster processing in Python  
from rasterstats import zonal_stats    # zonal statistics
import trimesh                         # 3D mesh processing in Python


# Let's get ready to build a map.  First, we are going to visit [The Commonwealth Map](https://kygeonet.ky.gov/tcm) to use the coordinate widget to grab center coordinates.
# 
# <p align="center">
#     <img src="assets/coordinate_widget.png" width="450" height="auto" />
#     <figcaption><strong>Figure:</strong> Coordinate widget in the lower left corner of the the Commonwealth Basemap app.</figcaption>
# </p>
# 
# I was able to copy: -84.886 37.917 Degrees.  We can use this to center our map.  
# 
# Notice the values pasted are in the order of long/lat.  When we go to add the values for the map, make sure to reverse the order so that it is lat/long
# 
# ```juypter
# m = Map(center=(lat, long, zoom=4, width= , height=))
# ```
# 
# Fill the values for `center`, `zoom`, and `size`.

# In[ ]:


# let's create a map
m = Map(
    center=(37.917, -84.886), 
    zoom=4
    )
# display the map
m


# Familiarize yourself with the map and the default widgets on the left.  Take a moment to test drive the ones on the left.  
# 
# - zoom
# - fullscreen
# - polyline
# - polygon
# - rectangle
# - circle
# - marker
# - edit
# - delete
# 
# When you are done, go to the previous cell and make adjustments to zoom, height, width, or coordinates.  Try to make Kentucky centered and be in fill the screen.

# Now take a moment to open the toolbox in the top right.  Scroll over each thumbnail to see what's available.  Try them out.  We'll comeback to this later. 

# While we're working on the map.  Let's add a *WMSLayer* of The Commonwealth Basemap.

# In[ ]:


m.add_tile_layer(
    url="https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_TCM_Base_WGS84WM/MapServer/tile/{z}/{y}/{x}",
    name="TCM",
    attribution="DGI",
)
m


# ___
# ## Get Building Heights

# Building heights are an important attribute in many contexts: urban studies, environmental studies, emergency management, economics, and of course, geospatial and remote sensing.
# 
# Although using LiDAR to extract building footprints is a fun exercise, many excellent resources already exist.  I like [Overture Maps's](https://docs.overturemaps.org/guides/buildings/#14/32.58453/-117.05154/0/60) (OM) building datasets. 
# 
# Fortunately, DGI has already processed a recent release of OM's buildings.  We will use that dataset from DGI's Open Data Portal along with KyFromAbove LiDAR Pointcloud data to extract building heights.
# 
# These are the steps we are going to take.
# 
# 1. Find an area of interest
# 2. Get building footprint data
# 3. Search STAC for pointcloud data
# 4. Create a Height Above Ground Model (HAG)\*
# 5. Perform zonal statistics on buildings
# 6. Write buildings with height attributes to file
# 
# 
# \*Using the Height Above Ground model is much more efficient and accurate than using math and dsm/dtm.

# ### Find an AOI
# 
# To find our area of interest, let's overlay the Phase 3 Pointcloud Tile Grid on the map.
# 
# - Go to [KyFromAbove Stac-Browser](https://kygeonet.ky.gov/stac)
# - Click on the *Point Cloud Phase 3 (COPC)* collection.
# - Find the tile index geopackage under *Asssets*
# - Click *Copy URL*\*
# - Paste it to your local text file or in your notebook with comments (#)<br><p><img src="assets/tileindexlink.png" width="600" height="auto" /></p>
# - Add to map
# 
# 
# \*FYI, I have pre-saved some links in the repo root directory in [pasted_values.txt](../pasted_values.txt).

# In[ ]:


# add tile index to map
tile_index = "https://kyfromabove.s3-us-west-2.amazonaws.com/elevation/PointCloud/TileGrids/kyfromabove_phase3_pointcloud_5k_grid.gpkg"
# read with geopandas
gdf = gpd.read_file(tile_index)
# add to map
m.add_gdf(gdf, layer_name="Phase 3 Tile Index")
m


# Zoom to an area around Florence, Kentucky.  As you scroll over the tiles, the info box will show feature id, key, and aws_url.  We need to grab a url to add to the next cell. 

# In[ ]:


# get AWS URL
aws_url = 'https://kyfromabove.s3.us-west-2.amazonaws.com/elevation/PointCloud/Phase3/N023E293_LAS_Phase3.copc.laz'  # input("Paste the AWS S3 URL for the KyFromAbove data: ")
print(aws_url)


# #### Get extent values
# 
# Now that we know the tile and have it's name.  Let's go to the STAC API to grab to extent details. 
# 
# 1. Extract the STAC Item ID from the file path

# In[ ]:


# get the item_id
tile_basename = os.path.basename(aws_url)    # Separate the path and get the file name
item_id = tile_basename.replace(".laz", "")  # Remove the file extension to get the name
item_id                                      # ID to search for


# 2. Use [PySTAC](https://pystac.readthedocs.io/en/stable/) to get info on the Item
# 
#     - connect to the API *https://spved5ihrl.execute-api.us-west-2.amazonaws.com/*
#     - get item
#     - get item info

# In[ ]:


# stac api url
stac_api_url = "https://spved5ihrl.execute-api.us-west-2.amazonaws.com"
# open the stac client
client = Client.open(stac_api_url)

stac_item = item_id

# search fo the item
results = client.search(ids=[stac_item])
results.get_all_items()


# In[ ]:


# parse the results to get item bbox
for item in results.get_items():
    bbox = item.bbox

geometry = bbox[0], bbox[1], bbox[2], bbox[3]
geometry = str(geometry).replace("(", "").replace(")", "").replace(" ", "")
print(geometry)


# We will use these bbox values to help us filter buildings.

# ___
# ### Get Building Footprints
# 
# 1. Visit the Kentucky [Open Data Portal](https://opengisdata.ky.gov) and search for buildings.  
# 2. Click on *Kentucky Building Footprints - Overture Maps Foundation*.
# 3. At the bottom of the left sidebar, click *I want to use this*.
# 4. Toggle open *View API Resources*.
# 5. Click on *View* for the GeoService\*.<br><p><img src="assets/api_resources.png" width="400" height="auto" /></p>
# 
# *Refer to the Rest API [Query](https://developers.arcgis.com/rest/services-reference/enterprise/query-feature-service/) Documentation for the next step.

# #### Set up a query
# 
# From step five above, we should now be on the rest service endpoint for the buildings layer.
# 
# 1. Grab the bbox from the code cell above without the brackets *[]*.
# 2. Paste it into the *Input Geometry* on the service end point.
# 3. Use `4326` as the *Input Spatial Reference*.
# 4. Enter the number `6` for *Geometry Precision*.
# 5. Click *Query (GET)*.  Leave as HMTL to see if it works
# 6. Switch format to `GeoJSON`.
# 7. Click Get
# 8. Copy the URL and paste to your text file for use in the next cell.

# In[ ]:


# get Overture Maps Bulding Footprints
buildings_geojson = 'https://services3.arcgis.com/ghsX9CKghMvyYjBU/arcgis/rest/services/Ky_OvertureMaps_Buildings_WM_gdb/FeatureServer/0/query?where=1%3D1&objectIds=&geometry=-84.628911%2C38.975701%2C-84.611113%2C38.989593&geometryType=esriGeometryEnvelope&inSR=4326&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&relationParam=&returnGeodetic=false&outFields=*&returnGeometry=true&returnCentroid=false&returnEnvelope=false&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=4326&defaultSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&collation=&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&returnZ=false&returnM=false&returnTrueCurves=false&returnExceededLimitFeatures=true&quantizationParameters=&sqlFormat=none&f=pgeojson&token='  # input("Paste the URL for the Overture Maps Building Footprints: ")


# Add it to the map

# In[ ]:


m.add_geojson(buildings_geojson, layer_name="Building Footprints",
              style={"fillColor": "yellow", "color": "orange", "weight": 1, "fillOpacity": 0.5})
m


# #### Clean up the map
# 
# The map has a few too many layers from trial and error.  Let's clean that up.

# In[ ]:


# Insert values for map cen
m_clean = Map(
    center=(37.5, 86.5),
    zoom=8)

m_clean.add_tile_layer(
    url="https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_TCM_Base_WGS84WM/MapServer/tile/{z}/{y}/{x}",
    name="TCM",
    attribution="DGI",)
m_clean.add_geojson(buildings_geojson, layer_name="Building Footprints",
              style={"fillColor": "yellow", "color": "orange", "weight": 1, "fillOpacity": 0.5}) 


# In[ ]:


# display the map
m_clean


# ### Review
# 
# What have we done up to now?
# 
# 1. Created an Interactive Map
# 2. Added The Commonwealth Basemap
# 3. Added Phase3 Pointcloud Tiles
# 4. Added Buildings for AOI

# ___
# ### Get Building Heights
# 
# In order to GET our building heights, we need to process our laz file so that we can add height values to the building footprints.
# 
# This next step is a redundancy.  We're just doing it to set our variable in one spot.

# In[ ]:


# retreive variables for reproducibility
buildings = buildings_geojson
tile_url = aws_url


# [PDAL](https://pdal.io/en/2.8.4/)\* - *Point Data Abstraction Data Library*
# 
# >PDAL is C++ libary to translate and manipulate point cloud data.
# 
# It also provides [Python](https://pdal.io/en/2.8.4/python.html) support.  For the purposes of this exercise, all the information we need is in the *Concepts* (we don't need to know about Java).
# 
# <p><img src="assets/pdal_concepts.png" width="300" height="auto" /><p>  
# 
# Take a moment to briefly review tthe concepts
# 
# \*For this exercise, I am using PDAL v2.8.4

# #### Surface Models and stuff
# 
# To streamline processing, we are going to set up a pipeline using the concepts reviewed above.
# 
# <p align="center">
#     <img src="assets/pipeline.png" width="400" height="auto" />
#     <figcaption><strong>Figure:</strong> Representation of a PDAL Pipeline.</figcaption>
# </p>
# 
# In order to get building heights, we need to get surface heights.  Traditionally, people will create a bare earth Digital Terrain Model (DEM/DTM), a Digital Surface Model (DSM), and then perform some raster math to get the *normalized Digital Surface Model* (nDSM)
# $$
# \text{nDSM} = \text{DTM} - \text{DSM}
# $$
# 
# This would mean we would have to create a new file for the DEM/DTM, a new file for the DSM, then perform some raster math create a file for the nDSM.  That's a lot of filters, files, processing, etc.  And frankly, I don't want to do that.  
# 
# Instead, I like to create one pipeline, read one file, pass it through a series of filters, and export a file with surface height values.  This is call the *Height Above Ground*, or HAG for short.

# 
# #### Build a Pipeline
# 
# Before we run our pipeline, I'm going to walk you through what we're going to do with PDAL.
# 
# 1. Read the Point Cloud File - Remember, it's a COPC  
# 2. Filter to points for first return 
# 3. Use the HAG filter
# 4. It's not enough to just create the HAG filter, we need to carry the values with us.
# 5.  Save the HAG to file with the *maximum* value.
# 
# ```python
#     {
#         "type":"readers.copc",
#         "filename":'f'tile_url'
#     },
#     {
#         "type":"filters.expression",
#         "expression":"ReturnNumber == 1 || ReturnNumber == 1"        
#     },
#     {
#         "type":"filters.hag_delaunay",
#         "allow_extrapolation":True
#     },
#     {
#         "type":"filters.ferry",
#         "dimensions":"HeightAboveGround=>Z"
#     },
#     {
#         "type":"writers.gdal",
#         "filename":"hag.tif",
#         "resolution":2,
#         "output_type":"max",
#         "gdalopts":[
#             "COMPRESS=LZW",
#             "TILED=YES",
#             "BLOCKYSIZE=256",
#             "BLOCKYSIZE=256
#         ]
#     }
# ```
# 
# The result is one pipeline, one input, and one output.  Feel free to paste values into the next cell.

# In[ ]:


# create a pdal pipeline
# paste the above values between the brackets
pipeline_json = []
print(json.dumps(pipeline_json, indent=2))


# In[ ]:


# Process the pipeline
pipeline = pdal.Pipeline(json.dumps(pipeline_json))
count = pipeline.execute()
arrays = pipeline.arrays
print(f"Processed {count} points.")

# create variable to the hag file
hag_file = "output/hag.tif"


# In[ ]:


# Check it in a map
m_clean.add_raster(hag_file, layer_name="Height Above Ground (Feet)", colormap="terrain")
m_clean


# #### Zonal Statistics
# 
# We've successfully created HAG model file.  Now we can use zonal statistics to create the building height attributes.  For this, you can refer to the [rasterstats](https://pythonhosted.org/rasterstats/index.html) documentation.

# ##### Housekeeping
# If you recall, we've pulled building footprints using WGS84 and the HAG file is projected in its original Kentucky Single Zone: *EPSG:3089*.  This won't work for processing.  We will have to get the CRS value of one, and assign it to the other.  Since our tif is in EPSG:3089 and we are concerned with Kentucky values, we'll assign single zone to the buildings.

# In[ ]:


# Use python to get the hag file crs.  
# This way, we know that CRSs are the same. 
# Rasterio is a good tool for this.
with rasterio.open(hag_file) as src:
    src_crs = src.crs

src_crs


# In[ ]:


# read building file with Geopandas
buildings = gpd.read_file(buildings_geojson)
buildings = buildings.to_crs(src_crs)

# assign values to to buildings
stats = zonal_stats(buildings, hag_file, stats="min max mean median std")
stats


# This looks good.  We have the values for building heights.  Time to save it to file.
# 
# - add height attributes to the buildings geodataframe.
# - save to your preferred vector format

# In[ ]:


# assign stat fields to buildings
buildings["hag_min"] = [s["min"] for s in stats]
buildings["hag_max"] = [s["max"] for s in stats]
buildings["hag_mean"] = [s["mean"] for s in stats]
buildings["hag_median"] = [s["median"] for s in stats]
buildings["hag_std"] = [s["std"] for s in stats]

# Save updated GeoJSON or GPKG
buildings.to_file("output/buildings_with_hag.gpkg", driver="GPKG")
buildings.to_file("output/buildings_with_hag.json", driver="GeoJSON")


# # Congratulations!
# 
# You have completed this exercise.  We have taken building footprints, a pointcloud file in the cloud, and ran it through a few processes to add height attributes to builings.  
# 
# Logically, the next step would be to create a 3D Builing layer from our 2D buildings with heights, but I'd rather focus the rest of the time helping you with any questions you have.

# ### Bonus
# 
# Convert to 3d

# In[ ]:


# read buildings from last output
gdf = gpd.read_file("output/buildings_with_hag.gpkg")

# extrude
meshes = []
for _, row in gdf.iterrows():
    h = row["hag_max"]
    footprint = row.geometry

    # Convert polygon exterior to 3D (Z=0)
    base_coords = [(x, y, 0) for x, y in footprint.exterior.coords]
    roof_coords = [(x, y, h) for x, y in footprint.exterior.coords]

    # Stack base and roof into a prism
    prism = trimesh.creation.extrude_polygon(footprint, h)
    meshes.append(prism)

scene = trimesh.Scene(meshes)
scene.show()

