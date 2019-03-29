#!/usr/bin/env python
import time
import datetime
import shapefile
import zipfile
import os
import subprocess

if __name__ == '__main__':

    harvestyear = 2017
    template_path = ''
    shapefile_name = 'test'+str(harvestyear)
    myshp = open(template_path+"Marker"+str(harvestyear)+"oShape/"+"Marker"+str(harvestyear)+"oShape.shp", "rb")
    mydbf = open(template_path+"Marker"+str(harvestyear)+"oShape/"+"Marker"+str(harvestyear)+"oShape.dbf", "rb")
    sf = shapefile.Reader(shp=myshp, dbf=mydbf)

    #w = shapefile.Writer()

    fields = sf.fields

    print sf.fields

    count = 0
    for shaperec in sf.iterShapeRecords():
        count = count +1
        if(count < 2):
            record = shaperec.record
            print shaperec.record
            print shaperec.shape
            break;

    #w.save('field_data/'+shapefile_name)
    print "d"
    harvestyear = 2016
    template_path = ''
    shapefile_name = 'test'+str(harvestyear)
    myshp = open(template_path+"Marker"+str(harvestyear)+"oShape/"+"Marker"+str(harvestyear)+"oShape.shp", "rb")
    mydbf = open(template_path+"Marker"+str(harvestyear)+"oShape/"+"Marker"+str(harvestyear)+"oShape.dbf", "rb")
    sf = shapefile.Reader(shp=myshp, dbf=mydbf)

    w = shapefile.Writer()
    w.fields = fields

    print sf.fields
    print w.fields
    count = 0
    for shaperec in sf.iterShapeRecords():
        record[0] = str(shaperec.record[2])
        record[1] = str(shaperec.record[3])
        record[2] = (str(shaperec.record[1])).replace('.',',')
        record[3] = '1' if float(shaperec.record[0]) > 0.0 else '0'
        record[4] = str(shaperec.record[5])
        record[5] = str(shaperec.record[4])
        w.records.append(list(record))
        w._shapes.append(shaperec.shape)

    w.save('field_data/Marker'+str(harvestyear)+"oShape.shp")
