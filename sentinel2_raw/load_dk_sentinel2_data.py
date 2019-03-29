#!/usr/bin/env python
import time
import datetime
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt

start_date = '20160101' # hardcoded value
current_date = datetime.date.today().strftime("%Y%m%d")
#current_date = datetime.date.today().strftime("%Y%m%d")

print "loading!"
api = SentinelAPI('mpc', 'q11g33h99', 'https://scihub.copernicus.eu/dhus')
footprint = geojson_to_wkt(read_geojson('map.geojson'))

products = api.query(footprint, date=(start_date, current_date), platformname = 'Sentinel-2', producttype='S2MSI1C', cloudcoverpercentage = (0, 15))

api.download_all(products)

print "DONE!!!"
