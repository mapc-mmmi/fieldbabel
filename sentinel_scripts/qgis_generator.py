import utm
import os
import json
import time
from pathlib import Path

class Ggis_gen:
    def __init__(self, output_folder,geo_json_data):
        self.own_path = 'sentinel_scripts/'
    	self.template_path = self.own_path + 'templates/'
        self.output_folder = output_folder
        self.output_folder_geotifs = 'geotifs/'
        self.output_folder_fielddata = 'field_data/'
        self.geo_json_data = geo_json_data


    def create_qgis_projectfile(self):
        js_dic = json.loads(self.geo_json_data)

        P0 = (((((js_dic["features"])[0])["geometry"])["coordinates"])[0])[0]
        P2 = (((((js_dic["features"])[0])["geometry"])["coordinates"])[0])[2]
        M0 = utm.from_latlon(float(P0[1]), float(P0[0]))
        M2 = utm.from_latlon(float(P2[1]), float(P2[0]))

        filenames = next(os.walk(self.output_folder+self.output_folder_geotifs))[2]
        filenames.sort()

        f = open(self.output_folder + (self.output_folder.split('/'))[1]+".qgs",'w')
        i = open(self.template_path+"qgis/head_qgis.xml",'r')

        p = Path(self.output_folder+self.output_folder_fielddata)
        print p
        print p.exists()
        time_now = (time.strftime("%Y%m%d%H%M%S"))
        if(p.exists()):
            shapefile_names = next(os.walk(self.output_folder+self.output_folder_fielddata))[2]
            for shape_name in shapefile_names:
                if((shape_name)[-4:] == '.shp'):
                    shapefile_name = (shape_name)[0:-4]
                    print shape_name
                    name = shapefile_name

                    layer_id = name+time_now

                    tree_layer = (open(self.template_path+"qgis/layer_tree_layer.xml",'r').read()).format(
                                    layer_id = "\""+layer_id+"\"",
                                    layer_name = "\""+name+"\"")
        else:
            layer_id = ""
            tree_layer = ""

        tree_layer2 = ""
        for string in filenames:
            if ".tif" == string[-4:]:
                tree_layer2 = tree_layer2+(open(self.template_path+"qgis/layer_tree_layer.xml",'r').read()).format(
                                layer_id = "\""+string[:-4]+"\"",
                                layer_name = "\""+string[:-4]+"\"")



        #data = (i.read()).format(qgis_title=time_now+"_SENTINEL1_"+crop_dk_name+"_"+start_date+"_"+end_date,
        #                        tree_layers=tree_layer+tree_layer2)
        data = (i.read()).format(qgis_title=time_now+"_SENTINEL1_"+'Winterwheat',
                                tree_layers=tree_layer+tree_layer2)

        f.write(data)


        i = open(self.template_path+"qgis/mapcanvas.xml",'r')
        data = (i.read()).format(lon_1=M0[0],lat_1=M0[1],lon_2=M2[0],lat_2=M2[1])
        f.write(data)

        f.write("<projectlayers layercount=\""+ str(1+len(filenames))+"\">\n")

        crop_field_render = (open(self.template_path+"qgis/crop_field_render.xml",'r').read())

        if(p.exists()):
            for shape_name in shapefile_names:
                if((shape_name)[-4:] == '.shp'):
                    data = (open(self.template_path+"qgis/maplayer.xml",'r').read()).format(
                                render_type = "\"vector\"",
                                render_config = """ simplifyDrawingHints="1" minLabelScale="0" maxLabelScale="1e+08" simplifyDrawingTol="1" geometry="Polygon" simplifyMaxScale="1" simplifyLocal="1" scaleBasedLabelVisibilityFlag="0" """,
                                layer_id = layer_id,
                                layer_name = name,
                                layer_datasource = self.output_folder_fielddata+shape_name,
                                maplayer_configuration = crop_field_render)

                    f.write(data)

        geotif_config = (open(self.template_path+"qgis/geotif_config.xml",'r').read())


        for string in filenames:
            if ".tif" == string[-4:]:
                print "adding geotif :: "+ string
                data = (open(self.template_path+"qgis/maplayer.xml",'r').read()).format(
                            render_type = "\"raster\"",
                            render_config = "",
                            layer_id = string[:-4],
                            layer_name = string[:-4],
                            layer_datasource = self.output_folder_geotifs+string,
                            maplayer_configuration = geotif_config)

                f.write(data)

        f.write("</projectlayers>\n")

        i = open(self.template_path+"qgis/tail_qgis.xml",'r')
        data = i.read()
        f.write(data)
        f.close()
