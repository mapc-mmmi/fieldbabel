#!/usr/bin/env python
import shapefile
import json
import geojson
import os
import sys
import csv
import utm
import datetime
import subprocess
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt

def pnpoly(vertx, verty, testx, testy):
    c = False
    j = len(vertx)-1
    for i in range(0,len(vertx)):
        if( ((verty[i]>testy) != (verty[j]>testy)) and (testx < (vertx[j]-vertx[i]) * (testy-verty[i]) / (verty[j]-verty[i]) + vertx[i]) ):
            c = (not c)
        j=i
    return c

def extract_polygon(geo_json_data):
    js_dic = json.loads(geo_json_data)

    geo_poly = (((((js_dic['features'])[0])['geometry'])['coordinates'])[0])

    X_poly = []
    Y_poly = []
    for i in range(0,5):
        M = utm.from_latlon(float((geo_poly[i])[1]), float((geo_poly[i])[0]))
        X_poly.append(M[0])
        Y_poly.append(M[1])

    return [X_poly, Y_poly]

class Processor_1:
    def __init__(self,id,time,geo_json_data):
    	self.geo_json_data = geo_json_data
    	self.output_main = 'sentinel_output/'
    	self.output_folder = self.output_main+time.strftime("%Y%m%d%H%M%S")+'_' +str(id)+'/'
        self.own_path = 'sentinel_scripts/'
    	self.template_path = 'sentinel_scripts/templates/'
    	self.preprocessed_path = 'sentinel_preprocessed_data/'
    	self.ending = "_preproces_1.dim"
    	self.harvestyear = 2017
    	self.shapefile_name = ''

    	self.processed_grd_data = next(os.walk(self.preprocessed_path))[2]

        self.crop_info = []
        self.crops = []
        with open(os.path.join(sys.path[0], 'app/crop_type.csv'), 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                self.crops.append(str(row[1])[2:-1])
                c_info = ((str(row[1])[2:-1]),(str(row[2])[2:-1]),int(row[3]),(str(row[4])[2:-1]),int(row[5]),(str(row[6])[2:-1]))
                self.crop_info.append(c_info)

    	if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            os.makedirs(self.output_folder+'geotifs/')

    def create_sentinel_xml(self):
        f = open("sentinel_scripts/autoGraph.xml",'w')
        parsing_xml = (open(self.template_path+"/snap/output_1.xml",'r').read()).format(polygon_string = str(geojson_to_wkt(geojson.loads(self.geo_json_data))))
        f.write(parsing_xml)

    def fetch_sentinel_data(self,start_date, end_date):
    	api = SentinelAPI('mpc', 'q11g33h99', 'https://scihub.copernicus.eu/dhus')

    	footprint = geojson_to_wkt(geojson.loads(self.geo_json_data))

        print (start_date, end_date)
        print footprint

    	products = api.query(footprint, date=(start_date, end_date), platformname = 'Sentinel-1', producttype='GRD') #, orbitdirection='ASCENDING'
    	for i, (product_id, props) in enumerate(products.items()):
            file_name = props['title']+self.ending

            if any(file_name in s for s in self.processed_grd_data):
                print file_name
                outputfilename = file_name[17:32]+"_"+file_name[0:16]+'.tif'
                filepath_out = self.output_folder+'geotifs/'
                command = "LD_LIBRARY_PATH=. ~/snap/bin/gpt sentinel_scripts/autoGraph.xml -Pinputfile=\""+self.preprocessed_path+file_name+"\"" +" -Poutputfile=\""+filepath_out+outputfilename+"\""
                p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
                (output, err) = p.communicate()


    def extract_crop_fields(self, crop_dk_name):


        Pos_poly = extract_polygon(self.geo_json_data)
        myshp = open(self.template_path+"Marker"+str(self.harvestyear)+"oShape/"+"Marker"+str(self.harvestyear)+"oShape.shp", "rb")
        mydbf = open(self.template_path+"Marker"+str(self.harvestyear)+"oShape/"+"Marker"+str(self.harvestyear)+"oShape.dbf", "rb")
        sf = shapefile.Reader(shp=myshp, dbf=mydbf)

        w = shapefile.Writer()
        #pprint(vars(sf))
        w.fields = sf.fields

        fields = 0

        print crop_dk_name
        for shaperec in sf.iterShapeRecords():
            field_type = shaperec.record[4]
            if((crop_dk_name in field_type) or (crop_dk_name.lower() in field_type) or crop_dk_name == "All"):
                if(pnpoly(Pos_poly[0],Pos_poly[1],shaperec.shape.bbox[0],shaperec.shape.bbox[1]) and pnpoly(Pos_poly[0],Pos_poly[1],shaperec.shape.bbox[2],shaperec.shape.bbox[3])):
                    w.records.append(shaperec.record)
                    w._shapes.append(shaperec.shape)
                    fields = fields + 1

        self.shapefile_name = 'sub_field_map_'+crop_dk_name
        if(fields>0): # is there any fields pressent in the area,
            # else do not save empty polygon file
            w.save(self.output_folder+'field_data/'+self.shapefile_name)

    def fetch_data_for_crop_type(self, crop_type, harvestyear):
        if(harvestyear.isdigit()):
            self.harvestyear = int(harvestyear)
        else:
            self.harvestyear = int(datetime.date.today().year)
    	start_date = '20170101'
    	end_date = '20170101'
    	crop_dk_name = ""
        self.create_sentinel_xml()

        crop_found = False
        for i in range(0,len(self.crops)):
            if(crop_type == self.crops[i]):
                crop_dk_name = (self.crop_info[i])[1]
                start_date = str(self.harvestyear+(self.crop_info[i])[2]) + str((self.crop_info[i])[3])
                end_date = str(self.harvestyear+(self.crop_info[i])[4]) + str((self.crop_info[i])[5])
                crop_found = True

    	if(crop_dk_name != "" and crop_found == True):
    		print "process sentinel data"
    		self.fetch_sentinel_data(str(start_date), str(end_date))
    		print "shapfile extraction"
    		self.extract_crop_fields(crop_dk_name)
        elif(crop_type == 'None' and crop_found == False):
            start_date = (datetime.datetime.now() - datetime.timedelta(days=14)).strftime("%Y%m%d")
            end_date = datetime.datetime.now().strftime("%Y%m%d")
            print "process sentinel data"
            self.fetch_sentinel_data(str(start_date), str(end_date))

        return self.output_folder
