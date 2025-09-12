#!/usr/bin/env python
# coding: utf-8

# # DGI/KyFromAbove Workshop
# #### Getting Started
# 
# September 22, 2025
# Kentucky GIS Conference
# Fun Exploration of KyFromAbove with Python and other Tools
# 
# Let's get started using a notebook.  If you are using MyBinder to run this notebook, the environment is mostly set up already.

# ## Some basic code
# 
# Install python modules/packages/libraries . .  whatever.  Let's make sure our code works.
# 
# *\* For future tutorials, I may use [obstore](https://developmentseed.org/obstore/) to replace the botocore libraries.*

# In[1]:


import os
from leafmap import Map                # interactive mapping in Python
import geopandas as gpd                # working with geospatial data in Python
from pystac_client import Client       # STAC API clientimport
import pdal                            # lidar processing in Python
import json


# Let's get ready to build a map.  First, we are going to visit [The Commonwealth Map](https://kygeonet.ky.gov/tcm) to use the coordinate widget to grab center coordinates.
# 
# <p align="center">
#     <img src="assets/coordinate_widget.png" width="450" height="auto" />
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

# In[2]:


# let's create a map
m = Map(
    center=(37, -85.5), 
    zoom=7,
    # width=500, 
    # height=300
    )
# display the map by using m or display(m)
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
# When you are done, go to the previous cell and make adjustments to zoom, height, width, or coordinates.  

# Now take a moment to open the toolbox in the top right.  Scroll over each thumbnail to see what's available.  Try them out.  We'll comeback to this later. 

# While we're working on the map.  Let's add a *WMSLayer* of The Commonwealth Basemap.

# In[3]:


m.add_tile_layer(
    url="https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_TCM_Base_WGS84WM/MapServer/tile/{z}/{y}/{x}",
    name="TCM",
    attribution="DGI",
)
m


# ___
# ## Get Building Heights

# Building heights are an important attribute in a lot of contexts: urban studies, environmental studies, emergency management, economics, and of course, geospatial and remote sensing.
# 
# Though, using LiDAR to extract building footprints is a fun exercise, many excellent resources already exist.  I like [Overture Maps](https://docs.overturemaps.org/guides/buildings/#14/32.58453/-117.05154/0/60) building datasets. 
# 
# We are going to use overture maps dataset and KyFromAbove LiDAR Pointcloud data to extract building heights.
# 
# These are the steps we are going to take.
# 
# 1. Find an area of interest
# 2. Get building footprint data
# 3. Search STAC for pointcloud data.
# 4. Create a Height Above Ground Model\*
# 5. Perform zonal statistics on buildings
# 
# 
# \* Using the Height Above Ground model is much more efficient and accurate than using math and dsm/dtm.

# ### Find an AOI
# 
# To find our area of interest, let's overlay the Phase 3 Pointcloud Tile Grid on the map.
# 
# - Go to [KyFromAbove Stac-Browser](https://kygeonet.ky.gov/stac)
# - Click on the *Point Cloud Phase 3 (COPC)* collection.
# - Find the tile index geopackage in under *Asssets*
# - Click *Copy URL*
# - Paste it to your local text file or in your notebook with comments (#)<br><p><img src="assets/tileindexlink.png" width="600" height="auto" /></p>
# - Add to map

# In[4]:


# add tile index to map
tile_index = "https://kyfromabove.s3-us-west-2.amazonaws.com/elevation/PointCloud/TileGrids/kyfromabove_phase3_pointcloud_5k_grid.gpkg"
# read with geopandas
gdf = gpd.read_file(tile_index)
# add to map
m.add_gdf(gdf, layer_name="Phase 3 Tile Index")
m


# 

# In[5]:


# get AWS URL
aws_url = input("Paste the AWS S3 URL for the KyFromAbove data: ")
print(aws_url)


# #### Get extent values
# 
# Now that we know the tile and have it's name.  Let's go to the STAC API to grab to extent details. 
# 
# 1. Extract the STAC Item ID from the file path

# In[6]:


# get the item_id
tile_basename = os.path.basename(aws_url)    # Separate the path and get the file name
item_id = tile_basename.replace(".laz", "")  # Remove the file extension to get the
item_id


# 2. Use [PySTAC](https://pystac.readthedocs.io/en/stable/) to get info on the Item
# 
#     - connect to the API *https://spved5ihrl.execute-api.us-west-2.amazonaws.com*
#     - get item
#     - get item info

# In[7]:


# stac api url
stac_api_url = "https://spved5ihrl.execute-api.us-west-2.amazonaws.com"
client = Client.open(stac_api_url)

stac_item = item_id
results = client.search(ids=[stac_item])
results.get_all_items()


# In[8]:


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

# In[9]:


# get Overture Maps Bulding Footprints
buildings_geojson = input("Paste the URL for the Overture Maps Building Footprints: ")


# Add it to the map

# In[10]:


m.add_geojson(buildings_geojson, layer_name="Building Footprints",
              style={"fillColor": "yellow", "color": "orange", "weight": 1, "fillOpacity": 0.5})
m


# #### Clean up the map
# 
# The map has a few too many layers from trial and error.  Let's clean that up.

# In[11]:


m_clean = Map(
    center=(37.5, -85.5),
    zoom=7)

m_clean.add_tile_layer(
    url="https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_TCM_Base_WGS84WM/MapServer/tile/{z}/{y}/{x}",
    name="TCM",
    attribution="DGI",)
m_clean.add_geojson(buildings_geojson, layer_name="Building Footprints",
              style={"fillColor": "yellow", "color": "orange", "weight": 1, "fillOpacity": 0.5}) 


# In[12]:


m_clean


# ### Review
# 
# What have we done up to now?
# 
# 1. Created an Interactive Map
# 2. Added The Commonwealth Basemap
# 3. Added Phase Tiles
# 4. Added Buildings for AOI

# ___
# ### Get Building Heights
# 
# In order to GET our building heights, we need to process our laz file so that we can add height values to the building footprints.
# 
# This next step is a redundancy.  We're just doing it to set our variable in one spot.

# In[13]:


# retreive variables for reproducibility
buildings_geojson = buildings_geojson
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
# \*For this exercise, I am using verion 2.8.4

# #### Surface Models and stuff
# 
# To streamline processing, we are going to set up a pipeline using the concepts reviewed above.
# 
# In order to get building heights, we need to get surface heights.  Traditionally, people will create a bare earth Digital Terrain Model (DEM/DTM), a Digital Surface Model (DSM), and then perform some raster math to get the *normalized Digital Surface Model* (nDSM)
# $$
# \text{nDSM} = \text{DTM} - \text{DSM}
# $$
# 
# This would mean we would have to create a new file for the DEM/DTM, a new file for the DSM, then perform some raster math create a file for the nDSM.  That's a lot of filters, files, processing, etc.  And frankly, I don't want to do that.  
# 
# Instead, I like to create one pipeline, read one file, filter it, and export a file surface height values.  This is call the *Height Above Ground*, or HAG for short.

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
# ```python
#     {
#         "type":"readers.copc",
#         "filename":aws_url
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
# 
# The result is one pipeline, one input, and one output.  Feel free to paste values into the next cell.

# In[14]:


# create a pdal pipeline
# paste the above values between the brackets
pipeline_json = [
    {
        "type":"readers.copc",
        "filename":f'{aws_url}'
    },
    {
        "type":"filters.expression",
        "expression":"ReturnNumber == 1 || ReturnNumber == 1"        
    },
    {
        "type":"filters.hag_delaunay",
        "allow_extrapolation":True
    },
    {
        "type":"filters.ferry",
        "dimensions":"HeightAboveGround=>Z"
    },
    {
        "type":"writers.gdal",
        "filename":"hag.tif",
        "resolution":2,
        "output_type":"max",
        "gdalopts":[
            "COMPRESS=LZW",
            "TILED=YES",
            "BLOCKYSIZE=256",
            "BLOCKYSIZE=256"
        ]
    }
]
print(json.dumps(pipeline_json, indent=2))


# In[15]:


# Process the pipeline
pipeline = pdal.Pipeline(json.dumps(pipeline_json))
count = pipeline.execute()
arrays = pipeline.arrays
print(f"Processed {count} points.")


# In[16]:


# Check it in a map
m_clean.add_raster("hag.tif", layer_name="Height Above Ground (m)", colormap="terrain")
m_clean

