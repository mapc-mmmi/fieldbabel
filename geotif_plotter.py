#!/usr/bin/env python
import time
import datetime
import os
import sys
import subprocess
from osgeo import gdal
import utm
import numpy
import shapefile
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates
from shapely.geometry import Point, Polygon, MultiPolygon
from descartes.patch import PolygonPatch
import json

COLOR = {
    True:  '#6699cc',
    False: '#ff3333'
    }

BLUE =   '#6699cc'
YELLOW = '#ffcc33'
GREEN =  '#339933'
RED =  '#FF0000'
GRAY =   '#999999'

def v_color(ob):
    return COLOR[ob.is_valid]

def plot_coords(ax, ob):
    x, y = ob.xy
    ax.plot(x, y, 'o', color=GRAY, zorder=1)

def plot_zone(ax, ob):
    x, y = ob.xy
    ax.plot(x, y, '--', color=BLUE, zorder=1)

def pnpoly(vertx, verty, testx, testy):
    c = False
    j = len(vertx)-1
    for i in range(0,len(vertx)):
        if( ((verty[i]>testy) != (verty[j]>testy)) and (testx < (vertx[j]-vertx[i]) * (testy-verty[i]) / (verty[j]-verty[i]) + vertx[i]) ):
            c = (not c)
        j=i
    return c

def readgeotifbandvalues(rasterfn,utm_x,utm_y):
    raster = gdal.Open(rasterfn)
    geotransform = raster.GetGeoTransform()
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    p_x = int((utm_x-originX)/pixelWidth)
    p_y = int((utm_y-originY)/pixelHeight)
    databands = []
    for i in range(1,4):
        try:
            srcband = raster.GetRasterBand(i)
        except RuntimeError, e:
            print 'No band %i found' % i
            print e
            sys.exit(1)
        dataraster = srcband.ReadAsArray(p_x,p_y,1,1).astype(numpy.float)
        databands.append((dataraster[0])[0])

    return databands

if __name__ == '__main__':

    filepath_field_data = "sentinel_output/test_farm/field_data/"
    filepath_geotifs = "sentinel_output/test_farm/geotifs/"
    plot_folder = "temp_plot/"
    journal_num = "17-0015889"
    minimum_geo_size = 8
    geostep = 10
    sample_gap = 10
    methods = 2

    f = open(plot_folder + "farm_report.tex",'w')
    i = open("template/report_header.tex",'r')
    data = (i.read())
    f.write((data%journal_num))
    f.flush()

    field_data_files = next(os.walk(filepath_field_data))[2]
    field_data_files.sort()
    field_shp = ''
    field_dbf = ''

    for field_data in field_data_files:
        #print field_data[-4:]
        if(field_data[-4:]=='.shp'):
            field_shp = field_data
        if(field_data[-4:]=='.dbf'):
            field_dbf = field_data

    myshp = open(filepath_field_data+field_shp, "rb")
    mydbf = open(filepath_field_data+field_dbf, "rb")
    sf = shapefile.Reader(shp=myshp, dbf=mydbf)

    filenames = next(os.walk(filepath_geotifs))[2]
    filenames.sort()

    Time_plot = []
    for j in range (0,2):
        for i in range (1,13):
            y = 2016+j
            m = i
            time = mdates.date2num(datetime.strptime(str(y)+"%02d"%m+'15','%Y%m%d'))
            Time_plot.append(time)

    fig = plt.figure(123, figsize=(16,9),dpi=150)
    plt.clf()
    ax = fig.add_subplot(111)
    m = 1
    f.write("\\clearpage\n")
    f.write("\section{Introduction}\n\n")

    f.write("       \subsection{Field overview}\n\n")
    i = open("template/norm_figure.tex",'r')
    image_name = journal_num+'_fields'  + '.png'
    data = (i.read()) % (image_name,image_name[:-4])
    for shaperec in sf.iterShapeRecords():
        if(shaperec.record[0]  == journal_num):

            shape = shaperec.shape

            field_num = shaperec.record[1]
            polygon = Polygon(shape.points)
            plot_zone(ax, polygon.exterior)
            x_field_l = [i[0] for i in shape.points[:]]
            y_field_l = [i[1] for i in shape.points[:]]
            centroid = (sum(x_field_l) / len(x_field_l), sum(y_field_l) / len(x_field_l))
            try:
                rep_point = polygon.representative_point()
            except ValueError:
                rep_point = Point([centroid[0], centroid[1]])
                rep_point_calc = False
            if(int((shaperec.record[2]).partition(',')[0]) > minimum_geo_size):
                m = m + 1
                patch1 = PolygonPatch(polygon, fc=GRAY, ec=GRAY, alpha=0.5, zorder=2)
                ax.add_patch(patch1)
                ax.text(rep_point.x, rep_point.y,m,color='b')
                print field_num
            else:
                patch2 = PolygonPatch(polygon, fc=RED, ec=RED, alpha=0.5, zorder=2)
                ax.add_patch(patch2)


    ax.legend([patch1,patch2],['Analyzed field areas','field areas<'+ str(minimum_geo_size)+ 'ha'],loc=2)
    ax.set_xlabel('UTM meter - Easting')
    ax.set_ylabel('UTM meter - Northing')
    ax.set_title("Fields overview: "+journal_num)
    fig.tight_layout()
    plt.savefig(plot_folder+image_name)
    f.write(data)


    for shaperec in sf.iterShapeRecords():
        if(shaperec.record[0]  == journal_num and int((shaperec.record[2]).partition(',')[0]) > minimum_geo_size):
            field_num = shaperec.record[1]
            geo_size = int((shaperec.record[2]).partition(',')[0])
            crop_type = shaperec.record[4]
            crop_ko = shaperec.record[5]
            shape = shaperec.shape
            print crop_type.decode('utf-8', 'ignore')
            f.write("\n")
            f.write("\\newpage")
            f.write("\n")
            #print"   \section{"+str(field_num).decode('ascii', 'ignore')+"_"+ crop_type.decode('ascii', 'ignore')+"}\n"
            f.write("   \section{"+str(field_num).decode('ascii', 'ignore')+" "+ crop_type.decode('ascii', 'ignore')+"}\n")
            f.write("\n")
            f.write("   \subsection{Field Info}\n")
            f.write("\n")
            f.flush()
            R = []
            G = []
            B = []

            R_g = []
            G_g = []
            B_g = []

            Time = []
            time = 0
            count = 0
            count_val = 0
            x_field_l = [i[0] for i in shape.points[:]]
            y_field_l = [i[1] for i in shape.points[:]]
            centroid = (sum(x_field_l) / len(x_field_l), sum(y_field_l) / len(x_field_l))

            polygon = Polygon(shape.points)
            sample_poly = polygon.buffer(-2*geostep)
            if sample_poly.type == 'Polygon':
                sample_list = list(sample_poly.exterior.coords)
            else:
                sample_list = shape.points
            x_sample_l = [i[0] for i in sample_list[:]]
            y_sample_l = [i[1] for i in sample_list[:]]

            rep_point_calc = True
            try:
                rep_point = polygon.representative_point()
            except ValueError:
                rep_point = Point([sample_x, sample_y])
                rep_point_calc = False
            sample_x = rep_point.x
            sample_y = rep_point.y


            sample = True
            sat_pass = []
            sat_miss = []
            for string in filenames:
                 if ".tif" == string[-4:]:
                    time = time +1
                    #print filepath_out + string
                    count = 0
                    #print string[:-4]+'.json'
                    with open(filepath_geotifs + string[0:-4]+'.json', "r") as jsonfile:
                        json_data = json.loads(jsonfile.read())
                    jsonfile.close()



                    #time = mdates.date2num(datetime.strptime(string[0:15],'%Y%m%dT%H%M%S'))
                    time = mdates.date2num(datetime.strptime(string[17:32],'%Y%m%dT%H%M%S'))


                    if(not pnpoly(x_field_l, y_field_l, sample_x,sample_y)):
                        sample_x = centroid[0]
                        sample_y = centroid[1]

                    [r, g, b]= readgeotifbandvalues(filepath_geotifs + string,sample_x,sample_y)
                    if(r != 0 and g != 0):
                        sat_pass.append((json_data['PASS'])[0])
                        sat_miss.append((json_data['MISSION'][10]))
                        R.append(r)
                        G.append(g)
                        B.append(b)
                        Time.append(time)
                        count = count+1
                        if(methods>1):
                            R_temp = []
                            G_temp = []
                            B_temp = []
                            for x_sp in xrange(int(shape.bbox[0]+geostep),int(shape.bbox[2]-geostep),sample_gap*geostep):
                                for y_sp in xrange(int(shape.bbox[1]+geostep),int(shape.bbox[3]-geostep),sample_gap*geostep):
                                    if(pnpoly(x_sample_l, y_sample_l, x_sp,y_sp)):
                                        [r, g, b]= readgeotifbandvalues(filepath_geotifs + string,x_sp,y_sp)
                                        if(r != 0 and g != 0):
                                            R_temp.append(r)
                                            G_temp.append(g)
                                            B_temp.append(b)
                            R_g.append(R_temp[:])
                            G_g.append(G_temp[:])
                            B_g.append(B_temp[:])

            f.write("\\clearpage\n")
            f.write("       \subsection{Sampling Methods}\n\n")
            i = open("template/norm_figure.tex",'r')
            image_name = journal_num+"_"+field_num+"_"+crop_ko+'_sampling_m1'+'.png'
            data = (i.read()) % (image_name,image_name[:-4])

            fig = plt.figure(101, figsize=(16,8),dpi=150)
            #figsize=(20,10)
            plt.clf()
            ax = fig.add_subplot(111)
            plot_coords(ax, polygon.exterior)
            patch = PolygonPatch(polygon, fc=GRAY, ec=GRAY, alpha=0.5, zorder=2)
            ax.add_patch(patch)
            ax.set_title(field_num+' - ' +crop_type.decode('utf-8', 'ignore')+ ' - sample method1: spot' )
            sample_pl, = ax.plot(centroid[0],centroid[1],'ko')
            if(rep_point_calc):
                rep_pl, = ax.plot(rep_point.x,rep_point.y,'o',color=BLUE)
            circle2 = plt.Circle((sample_x,sample_y), 1.4*geostep, color=GREEN, fill=False)
            ax.add_artist(circle2)
            if(rep_point_calc):
                ax.legend([patch,sample_pl,rep_pl,circle2],['field area','centroid point','representative point','selected sample point'],loc=2)
            else:
                ax.legend([patch,sample_pl,circle2],['field area','centroid point','selected sample point'],loc=2)
            plt.axis('equal')
            ax.set_xlabel('UTM meter - Easting')
            ax.set_ylabel('UTM meter - Northing')
            fig.tight_layout()
            plt.savefig(plot_folder+image_name)
            f.write(data)

            if(methods>1):
                i = open("template/norm_figure.tex",'r')
                image_name = journal_num+"_"+field_num+"_"+crop_ko+'_sampling_m2'+'.png'
                data = (i.read()) % (image_name,image_name[:-4])
                fig = plt.figure(102, figsize=(16,8),dpi=150)
                #figsize=(20,10)
                plt.clf()
                ax = fig.add_subplot(111)
                plot_coords(ax, polygon.exterior)
                patch1 = PolygonPatch(polygon, fc=GRAY, ec=GRAY, alpha=0.5, zorder=2)
                ax.add_patch(patch1)
                for x_sp in xrange(int(shape.bbox[0]),int(shape.bbox[2]),sample_gap*geostep):
                    for y_sp in xrange(int(shape.bbox[1]),int(shape.bbox[3]),sample_gap*geostep):
                        if(pnpoly(x_sample_l, y_sample_l, x_sp,y_sp)):
                            rep_pl, = ax.plot(x_sp,y_sp,'o',color=BLUE)
                plt.axis('equal')
                ax.set_xlabel('UTM meter - Easting')
                ax.set_ylabel('UTM meter - Northing')
                ax.legend([patch1,rep_pl],['field area','sample points'],loc=2)
                ax.set_title(field_num+' - ' +crop_type.decode('utf-8', 'ignore')+ ' - sample method2:  '+str(sample_gap*geostep)+'m grid')
                fig.tight_layout()
                plt.savefig(plot_folder+image_name)
                f.write(data)

            if(methods>3):
                fig = plt.figure(103, figsize=(16,8),dpi=150)
                #figsize=(20,10)
                plt.clf()
                ax = fig.add_subplot(111)
                plot_coords(ax, polygon.exterior)
                patch1 = PolygonPatch(polygon, fc=GRAY, ec=GRAY, alpha=0.5, zorder=2)
                ax.add_patch(patch1)

                patch2 = PolygonPatch(sample_poly, fc=BLUE, ec=BLUE, alpha=0.5, zorder=2)
                ax.add_patch(patch2)
                ax.legend([patch1,patch2],['field area','sample area'],loc=2)
                ax.set_title(field_num+' - ' +crop_type.decode('utf-8', 'ignore')+ ' - sample method3: region')
                plt.axis('equal')
                fig.tight_layout()
                plt.savefig(plot_folder+journal_num+"_"+field_num+"_"+crop_ko+'_sampling_m3'+'.png')

            R_a = []
            R_d = []
            R_g_m = []
            R_g_a_m_a = []
            R_g_d_m_a = []
            R_g_a_m_b = []
            R_g_d_m_b = []
            G_a = []
            G_d = []
            G_g_m = []
            G_g_a_m_a = []
            G_g_d_m_a = []
            G_g_a_m_b = []
            G_g_d_m_b = []
            B_a = []
            B_d = []
            B_g_m = []
            B_g_a_m_a = []
            B_g_d_m_a = []
            B_g_a_m_b = []
            B_g_d_m_b = []

            Time_a = []
            Time_d = []
            Time_a_a = []
            Time_d_a = []
            Time_a_b = []
            Time_d_b = []

            for variants in range(0,len(R)):
                if(sat_pass[variants]=='A'):
                    R_a.append(R[variants])
                    G_a.append(G[variants])
                    B_a.append(B[variants])
                    if(sat_miss[variants]=='A'):
                        R_g_a_m_a.append(numpy.mean(R_g[variants]))
                        G_g_a_m_a.append(numpy.mean(G_g[variants]))
                        B_g_a_m_a.append(numpy.mean(B_g[variants]))
                        Time_a_a.append(Time[variants])
                    elif(sat_miss[variants]=='B'):
                        R_g_a_m_b.append(numpy.mean(R_g[variants]))
                        G_g_a_m_b.append(numpy.mean(G_g[variants]))
                        B_g_a_m_b.append(numpy.mean(B_g[variants]))
                        Time_a_b.append(Time[variants])
                    Time_a.append(Time[variants])
                if(sat_pass[variants]=='D'):
                    R_d.append(R[variants])
                    G_d.append(G[variants])
                    B_d.append(B[variants])
                    if(sat_miss[variants]=='A'):
                        R_g_d_m_a.append(numpy.mean(R_g[variants]))
                        G_g_d_m_a.append(numpy.mean(G_g[variants]))
                        B_g_d_m_a.append(numpy.mean(B_g[variants]))
                        Time_d_a.append(Time[variants])
                    elif(sat_miss[variants]=='B'):
                        R_g_d_m_b.append(numpy.mean(R_g[variants]))
                        G_g_d_m_b.append(numpy.mean(G_g[variants]))
                        B_g_d_m_b.append(numpy.mean(B_g[variants]))
                        Time_d_b.append(Time[variants])
                    Time_d.append(Time[variants])

            for i in range(1,methods+1):

                if(i==1):
                    sample_type = 'spot'
                elif(i==2):
                    sample_type = 'grid'
                elif(i==3):
                    sample_type = 'region'
                #print sample_type

                f.write("\\clearpage\n")
                f.write("       \subsection{Sampling type: " +sample_type +"}\n\n")
                i = open("template/norm_figure.tex",'r')
                image_name = journal_num+"_"+field_num+"_"+crop_ko+'_variable1_'+sample_type+'.png'
                data = (i.read()) % (image_name,image_name[:-4])

                fig = plt.figure(1, figsize=(16,8),dpi=300)
                plt.clf()
                ax = fig.add_subplot(111)
                ax.set_title(field_num+' - ' +crop_type.decode('utf-8', 'ignore')+ ' - variable1'+' - sample method: ' + sample_type)

                plt.plot(Time,R,'ro')
                if(sample_type == 'grid'):
                    plt.boxplot(R_g, positions=Time)


                ax.set_xticks(Time_plot) # Tickmark + label at every plotted point
                ax.grid(True)
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                # Format the x-axis for dates (label formatting, rotation)
                fig.autofmt_xdate(rotation=45)
                fig.tight_layout()
                plt.savefig(plot_folder+image_name)
                f.write(data)

                i = open("template/norm_figure.tex",'r')
                image_name = journal_num+"_"+field_num+"_"+crop_ko+'_variable2_'+sample_type+'.png'
                data = (i.read()) % (image_name,image_name[:-4])
                fig = plt.figure(2, figsize=(16,8),dpi=300)
                #image_name = plot_folder+journal_num+"_"+field_num+"_"+crop_ko+'_variable2_'+sample_type+'.png'
                plt.clf()
                ax = fig.add_subplot(111)
                ax.set_title(field_num+' - ' +crop_type.decode('utf-8', 'ignore')+ ' - variable2'+' - sample method: ' + sample_type)
                plt.plot(Time,G,'go')
                if(sample_type == 'grid'):
                    plt.boxplot(G_g, positions=Time)


                ax.set_xticks(Time_plot) # Tickmark + label at every plotted point
                ax.grid(True)
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

                # Format the x-axis for dates (label formatting, rotation)
                fig.autofmt_xdate(rotation=45)
                fig.tight_layout()
                plt.savefig(plot_folder+image_name)
                f.write(data)

                i = open("template/norm_figure.tex",'r')
                image_name = journal_num+"_"+field_num+"_"+crop_ko+'_variable3_'+sample_type+'.png'
                data = (i.read()) % (image_name,image_name[:-4])
                fig = plt.figure(3, figsize=(16,8),dpi=300)
                plt.clf()
                ax = fig.add_subplot(111)
                ax.set_title(field_num+' - ' +crop_type.decode('utf-8', 'ignore')+ ' - variable3'+' - sample method: ' + sample_type)
                plt.plot(Time,B,'bo')
                if(sample_type == 'grid'):
                    plt.boxplot(B_g, positions=Time)

                ax.set_xticks(Time_plot) # Tickmark + label at every plotted point
                ax.grid(True)
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                # Format the x-axis for dates (label formatting, rotation)
                fig.autofmt_xdate(rotation=45)
                fig.tight_layout()
                plt.savefig(plot_folder+image_name)
                f.write(data)

                if(sample_type == 'grid'):
                    f.write("\\clearpage\n")
                    f.write("       \subsection{"+sample_type + " sorted by recoding type}\n\n")
                    i = open("template/norm_figure.tex",'r')
                    image_name = journal_num+"_"+field_num+"_"+crop_ko+'_variable1_sorted_'+sample_type+'.png'
                    data = (i.read()) % (image_name,image_name[:-4])

                    fig = plt.figure(4, figsize=(16,8),dpi=300)
                    plt.clf()
                    ax = fig.add_subplot(111)
                    ax.set_title(field_num+' - ' +crop_type.decode('utf-8', 'ignore')+ ' - variable1'+' - sample method: ' + sample_type)

                    s1_a_a, = plt.plot(Time_a_a,R_g_a_m_a,'r-o')
                    s1_a_d, = plt.plot(Time_d_a,R_g_d_m_a,'b-x')
                    s1_b_a, = plt.plot(Time_a_b,R_g_a_m_b,'g--')
                    s1_b_d, = plt.plot(Time_d_b,R_g_d_m_b,'y-x')
                    ax.set_xticks(Time_plot) # Tickmark + label at every plotted point
                    ax.grid(True)
                    ax.legend([s1_a_a,s1_a_d,s1_b_a,s1_b_d],['Sentinel-1a ascending','Sentinel-1a decending','Sentinel-1b ascending','Sentinel-1b decending'],loc=2)

                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                    # Format the x-axis for dates (label formatting, rotation)
                    fig.autofmt_xdate(rotation=45)
                    fig.tight_layout()
                    plt.savefig(plot_folder+image_name)
                    f.write(data)

                    i = open("template/norm_figure.tex",'r')
                    image_name = journal_num+"_"+field_num+"_"+crop_ko+'_variable2_sorted_'+sample_type+'.png'
                    data = (i.read()) % (image_name,image_name[:-4])

                    fig = plt.figure(5, figsize=(16,8),dpi=300)
                    plt.clf()
                    ax = fig.add_subplot(111)
                    ax.set_title(field_num+' - ' +crop_type.decode('utf-8', 'ignore')+ ' - variable2'+' - sample method: ' + sample_type)

                    s1_a_a, = plt.plot(Time_a_a,G_g_a_m_a,'r-p')
                    s1_a_d, = plt.plot(Time_d_a,G_g_d_m_a,'b-x')
                    s1_b_a, = plt.plot(Time_a_b,G_g_a_m_b,'g--')
                    s1_b_d, = plt.plot(Time_d_b,G_g_d_m_b,'y-x')
                    ax.set_xticks(Time_plot) # Tickmark + label at every plotted point
                    ax.grid(True)
                    ax.legend([s1_a_a,s1_a_d,s1_b_a,s1_b_d],['Sentinel-1a ascending','Sentinel-1a decending','Sentinel-1b ascending','Sentinel-1b decending'],loc=2)

                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                    # Format the x-axis for dates (label formatting, rotation)
                    fig.autofmt_xdate(rotation=45)
                    fig.tight_layout()
                    plt.savefig(plot_folder+image_name)
                    f.write(data)

                    i = open("template/norm_figure.tex",'r')
                    image_name = journal_num+"_"+field_num+"_"+crop_ko+'_variable3_sorted_'+sample_type+'.png'
                    data = (i.read()) % (image_name,image_name[:-4])

                    fig = plt.figure(6, figsize=(16,8),dpi=300)
                    plt.clf()
                    ax = fig.add_subplot(111)
                    ax.set_title(field_num+' - ' +crop_type.decode('utf-8', 'ignore')+ ' - variable3'+' - sample method: ' + sample_type)

                    s1_a_a, = plt.plot(Time_a_a,B_g_a_m_a,'r-o')
                    s1_a_d, = plt.plot(Time_d_a,B_g_d_m_a,'b-x')
                    s1_b_a, = plt.plot(Time_a_b,B_g_a_m_b,'g--')
                    s1_b_d, = plt.plot(Time_d_b,B_g_d_m_b,'y-x')
                    ax.set_xticks(Time_plot) # Tickmark + label at every plotted point
                    ax.grid(True)
                    ax.legend([s1_a_a,s1_a_d,s1_b_a,s1_b_d],['Sentinel-1a ascending','Sentinel-1a decending','Sentinel-1b ascending','Sentinel-1b decending'],loc=2)
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                    # Format the x-axis for dates (label formatting, rotation)
                    fig.autofmt_xdate(rotation=45)
                    fig.tight_layout()
                    plt.savefig(plot_folder+image_name)
                    f.write(data)

    f.write("\end{document}\n")
    f.close()
    sys.exit(0)
