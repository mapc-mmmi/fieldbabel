#!/usr/bin/env python
import time
import threading
import datetime
import os
import sys
import subprocess
from sentinelsat import SentinelAPI, SentinelAPIError, read_geojson, geojson_to_wkt

class myThread (threading.Thread):
   def __init__(self, threadID, command, counter):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.command = command
      self.counter = counter
   def run(self):
       print str(self.threadID)+"---"+str(self.counter)
       p = subprocess.Popen(self.command, stdout=subprocess.PIPE, shell=True)
       (output, err) = p.communicate()
       print "DONE Processing!!!"

if __name__ == '__main__':

    start_date = '20160101' # hardcoded value
    current_date = datetime.date.today().strftime("%Y%m%d")

    api = SentinelAPI('mpc', 'q11g33h99', 'https://scihub.copernicus.eu/dhus')
    footprint = geojson_to_wkt(read_geojson('map.geojson'))

    filepath = "."
    filepath_out = "../sentinel_preprocessed_data/"
    ending = "_preproces_"

    SAE = False
    while True:
        print "Download new GRD data!!!"
        current_date = datetime.date.today().strftime("%Y%m%d") #update to current date
        try:
            print current_date
            products = api.query(footprint, date=(start_date, current_date), platformname = 'Sentinel-1', producttype='GRD', polarisationmode='VV VH') #, orbitdirection='ASCENDING'
            api.download_all(products)
            print "Done downloading!"
        except SentinelAPIError as error:
            if(not SAE): # is this the first time we get an error from the sentinel homepage
                print error.msg
            SAE = True
            time.sleep(600) # sleep for 600 seconds (10 min)
        except Exception as e:
            print "Connection to scihub faild!!!"
            print sys.exc_info()[0]

        filenames = next(os.walk(filepath))[2]
        filenames.sort()
        string = ""
        file_name = ""
        processed = next(os.walk(filepath_out))[2]

        processing_count = 0

        thread1 = myThread(1, "ls", 0) #dummy system call to start the thread (NOP)
        thread1.start()
        thread2 = myThread(2, "ls", 0) #dummy system call to start the thread (NOP)
        thread2.start()

        print "Start processing stage..."

        for string in (filenames[::-1]):
            print string
            if (".zip" == string[-4:] and "IW" == string[4:6]):
                for j in range(1,3):
                    outputfilename = string[0:-4]+ending+str(j)+".dim"
                    print outputfilename
                    file_name = string
                    if any(outputfilename in s for s in processed):
                        print "Processed!!!"
                    else:
                        print "Processing: " + file_name
                        processing_count = processing_count+1
                        command = "~/snap/bin/gpt preprocessor_"+str(j)+".xml -Pinputfile=\""+file_name+"\"" +" -Poutputfile=\""+filepath_out+outputfilename+"\""
                        while(thread1.isAlive() and thread2.isAlive()): # wait until free thread
                             time.sleep(10) # sleep for 10 seconds
                        if(not thread1.isAlive()):
                            thread1 = myThread(1, command, processing_count)
                            thread1.start()
                        elif(not thread2.isAlive()):
                            thread2 = myThread(2, command, processing_count)
                            thread2.start()

                print "Exiting Prossing Threads"
        time.sleep(120) # sleep for 120 seconds
