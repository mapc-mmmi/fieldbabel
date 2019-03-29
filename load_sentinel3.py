#!/usr/bin/env python
import time
import sys
import datetime
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt, SentinelAPIError

start_date = '20160101' # hardcoded value
current_date = '20171231' # hardcoded value
#current_date = datetime.date.today().strftime("%Y%m%d")

server_link = 'https://scihub.copernicus.eu/s3'

api = SentinelAPI('s3guest', 's3guest', server_link)
footprint = geojson_to_wkt(read_geojson('map.geojson'))
SAE = False
while(True):
    print 'connecting to:' + server_link
    try:
        products = api.query(footprint, date=(start_date, current_date), platformname = 'Sentinel-3', producttype='SL_2_LST___')
        api.download_all(products)
        SAE = False
    except SentinelAPIError as error:
        if(not SAE):
            print error.msg
        SAE = True
        time.sleep(600) # sleep for 600 seconds (10 min)
    except Exception as e:
        print "Connection to scihub faild!!!"
        print sys.exc_info()[0]

