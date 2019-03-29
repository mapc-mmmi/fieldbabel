#!/usr/bin/env python
import time
import datetime
from app import app, models, db
from sentinel_scripts import processor_1, qgis_generator
import zipfile
import os

def cleanup(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

    os.rmdir(path)

def zipdir(path, ziph):
    # ziph is zipfile handle
    cwd = os.getcwd()
    os.chdir(path)
    for root, dirs, files in os.walk('.'):
        for file in files:
            ziph.write(os.path.join(root, file))
    os.chdir(cwd)

if __name__ == '__main__':

    body = open("sentinel_grd_raw/map_test.geojson",'r').read()
    #print body

    p = processor_1.Processor_1(101,datetime.date.today(), body)
    #p = processor_1.Processor_1(101,req.timestamp, req.body)
    #output_folder = p.fetch_data_for_crop_type("All", 2017)
    #output_folder = p.fetch_data_for_crop_type("Winterwheat", 2017)
    output_folder = p.fetch_data_for_crop_type("Springbarley", 2017)

    q = qgis_generator.Ggis_gen(output_folder,body)
    q.create_qgis_projectfile()
