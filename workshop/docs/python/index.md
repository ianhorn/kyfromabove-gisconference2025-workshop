# Python

___
## Extract Building Heights

Launch the notebook [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ianhorn/kyfromabove-gisconference2025-workshop/main?labpath=notebooks/workshop-exercise.ipynb) 

<p align="center">
    <img src="assets/extrudedbuildings.png" width="100%" height="auto" />
    <figcaption><strong>Figure: </strong>Extruded Buildings from notebook output.</figcaption>
</p>

___

## Gists

Simple STAC Search

```python
from pystac_client import Client

api_url = 'https://spved5ihrl.execute-api.us-west-2.amazonaws.com/'
catalog = Client.open(api_url)

mysearch = catalog.search(
    max_items=20,
    bbox=[-88.45770480,36.91939541,-88.12757292,37.07265632]
)

# Convert results to a list of items
items = list(mysearch.get_items())

# Print each item ID
for item in items:
    print(item.id, item.bbox)
```

Create a mosaicjson

```python
from maap.maap import MAAP
maap = MAAP(maap_host='api.maap-project.org')
username = maap.profile.account_info()["username"]

local_path = "/local/path/to/files/"

files = glob.glob(os.path.join(dps_output, "*.tif"), recursive=False)

def local_to_s3(url):
    ''' A Function to convert local paths to s3 urls'''
    if url.startswith("my-private-bucket"):
        return url.replace("my-private-bucket", f"s3://maap-ops-workspace/{username}")

    if url.startswith("my-public-bucket"):
        return url.replace("my-public-bucket", f"s3://maap-ops-workspace/shared/{username}")

    if url.startswith("shared-buckets"):
        return url.replace("shared-buckets", "s3://maap-ops-workspace/shared")

tiles = [local_to_s3(file) for file in files]

mosaicdata = MosaicJSON.from_urls(tiles, minzoom=9, maxzoom=16)
```


