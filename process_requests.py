#!/usr/bin/env python
import time
import datetime
from app import app, models, db
from sentinel_scripts import processor_1, qgis_generator
import zipfile
import os
import subprocess

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

def send_done_processing(ID, email, link):
    print "Sending e-mail!"
    filename = "send_done_processing_msg.txt"
    f = open(filename,'w')
    to_email = str(email)
    new_msg = (open('sentinel_scripts/templates/email/done_msg.txt','r').read()).format(to_email = to_email, request_id=ID, download_link=link)
    f.write(new_msg)
    f.close()

    command = "ssmtp "+to_email+" < "+filename
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()

if __name__ == '__main__':
    a = 0
    while True:
        req = models.Request.query.filter(models.Request.processed==False).first()
        if(req != None):
            print "Processing!"
            #print (req.crop_type, int(req.season))
            p = processor_1.Processor_1(req.id,req.timestamp, req.body)
            output_folder = p.fetch_data_for_crop_type(req.crop_type, req.season)
            q = qgis_generator.Ggis_gen(output_folder,req.body)
            q.create_qgis_projectfile()
            zipf = zipfile.ZipFile(output_folder+'../'+(output_folder.split('/'))[1]+'.zip', 'w', zipfile.ZIP_DEFLATED, allowZip64 = True)
            zipdir(output_folder, zipf)
            zipf.close()
            cleanup(output_folder)
            link= output_folder[0:-1]+'.zip'
  
            print link
            print "Done zip Compression"
            print "Start updating sqldatabase"
            db.session.query(models.Request).filter(models.Request.id == req.id).update({models.Request.processed: True,models.Request.link:str(link)})
            db.session.commit()
            print "Done Updating sqldatabase"
            print "Sending out info e-mail to user"
            send_done_processing(req.id, str(req.author.email), str(link))
	    print "Done e-mail sending"
            print "Done Processing"
        else:
            a = a%720
            if(a==0):
                print "no new requests"
        a = a+1
        time.sleep(5)
    db.session.close()
