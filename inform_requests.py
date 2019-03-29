#!/usr/bin/env python
import time
import os
import subprocess
from app import app, models, db

if __name__ == '__main__':
    a = 0
    while True:
        a = a+1
        req = models.Request.query.filter(models.Request.request_queued==False).first()
        if(req != None):
            print req.id

            f = open('new_request_msg.txt','w')
            to_email = str(req.author.email)
            new_request_msg = (open('sentinel_scripts/templates/email/info_msg.txt','r').read()).format(to_email = to_email, request_id=req.id)
            f.write(new_request_msg)
            f.close()
            time.sleep(1)
            command = "ssmtp "+to_email+" < new_request_msg.txt"
            print command
            p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
            (output, err) = p.communicate()

            db.session.query(models.Request).filter(models.Request.id == req.id).update({models.Request.request_queued: True})
            db.session.commit()
        else:
            a = a%720
            if(a==0):
                print "no req data"
        time.sleep(5)
    db.session.close()
