from flask import render_template, flash, redirect, send_from_directory
from app import app, models, db
from .forms import CropSelectorForm, CurrentDataForm
import datetime
import json
import os
from HTMLParser import HTMLParser

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError, e:
    return False
  return True

def valid_email(string):
    email_p = string.split('@')
    domain = email_p[-1].split('.')
    if(len(email_p)>1 and len(domain)>1 and (domain[-1]=='dk' or domain[-1]=='com')):
        return True
    else:
        return False

def valid_field(myjson):
    json_object = json.loads(myjson)
    lon_min = 7.5
    lon_max = 12.85
    lat_min = 54.5
    lat_max = 57.85
    lat_diff = 1
    lon_diff = 1
    min_diff = 0.001

    try:
        if(len(json_object["features"]) == 1):
            point_list = ((((json_object["features"])[0])["geometry"])["coordinates"])[0]
            t_lon_min = 361.0
            t_lon_max = -1.0
            t_lat_min = 361.0
            t_lat_max = -1.0
            for i in range(0,len(point_list)):
                if(float((point_list[i])[0]) > t_lon_max):
                    t_lon_max = float((point_list[i])[0])
                if(float((point_list[i])[0]) < t_lon_min):
                    t_lon_min = float((point_list[i])[0])
                if(float((point_list[i])[1]) > t_lat_max):
                    t_lat_max = float((point_list[i])[1])
                if(float((point_list[i])[1]) < t_lat_min):
                    t_lat_min = float((point_list[i])[1])

            if(t_lon_min > lon_min and t_lon_max < lon_max and t_lat_min > lat_min and t_lat_max < lat_max and ((t_lon_max-t_lon_min) <= lon_diff) and ((t_lat_max-t_lat_min) <= lat_diff) and ((t_lon_max-t_lon_min) > min_diff) and ((t_lat_max-t_lat_min) > min_diff)):
                #print "SUCEES!!!!"
                return True
            else:
                #print "problem"
                return False
        else:
            return False
    except KeyError, e:
        return False

@app.route('/sentinel_output/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return send_from_directory(directory='/nfs/radar_test/fieldbabel/'+'sentinel_output/', filename=filename)

@app.route('/', methods=['GET', 'POST'])
#@app.route('/index')
def index():
    date_seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).date()
    current_form = CurrentDataForm()
    crop_form = CropSelectorForm()
    if current_form.validate_on_submit():
        print "processing!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        if(valid_email(current_form.email.data) and is_json(current_form.fieldpoly.data)):
            if(valid_field(current_form.fieldpoly.data)):

                if(models.User.query.filter(models.User.email==current_form.email.data).first() == None):
                    u = models.User(timestamp=datetime.datetime.utcnow(), email=current_form.email.data)
                    db.session.add(u)
                else:
                    u = models.User.query.filter(models.User.email==current_form.email.data).first()
                rq = models.Request(body=current_form.fieldpoly.data, timestamp=datetime.datetime.utcnow(), crop_type='None', season = 'Now!', processed=False, author=u, request_queued=False) #crop_type="Winterwheat"
                db.session.add(rq)
                db.session.commit()

                flash('Data is going to be send to: %s' % crop_form.email.data)
                #flash('GOT="%s", email=%s' % (form.fieldpoly.data, crop_form.email.data))
            else:
                flash("Not a valid JSON polygon!!! Either the area is to large/small or you have multiple areas")
        else:
            if(is_json(crop_form.fieldpoly.data)):
                flash('Not a valid email:%s' % crop_form.email.data)
            else:
                flash('BROKEN JSON SYNTAX! Did you copy it correctly')
        return redirect('/')

    if crop_form.validate_on_submit():
        #flash("validate_on_submit()")
        if(valid_email(crop_form.email.data) and is_json(crop_form.fieldpoly.data)):
            if(valid_field(crop_form.fieldpoly.data)):

                if(models.User.query.filter(models.User.email==crop_form.email.data).first() == None):
                    u = models.User(timestamp=datetime.datetime.utcnow(), email=crop_form.email.data)
                    db.session.add(u)
                else:
                    u = models.User.query.filter(models.User.email==crop_form.email.data).first()
                rq = models.Request(body=crop_form.fieldpoly.data, timestamp=datetime.datetime.utcnow(), crop_type=crop_form.crop_type.data, season = crop_crop_form.season.data, processed=False, author=u, request_queued=False) #crop_type="Winterwheat"
                db.session.add(rq)
                db.session.commit()

                flash('Data is going to be send to: %s' % crop_form.email.data)
                #flash('GOT="%s", email=%s' % (form.fieldpoly.data, crop_form.email.data))
            else:
                flash("Not a valid JSON polygon!!! Either the area is to large/small or you have multiple areas")
        else:
            if(is_json(crop_form.fieldpoly.data)):
                flash('Not a valid email:%s' % crop_form.email.data)
            else:
                flash('BROKEN JSON SYNTAX! Did you copy it correctly')
        return redirect('/')

    return render_template('login.html',
                           title='Fieldbabel service for sentinel data',
                           current_form=current_form,
                           crop_form=crop_form,
                           requests = models.Request.query.filter(models.Request.processed == False).order_by(models.Request.id).all(),
                           peformed = models.Request.query.filter(models.Request.processed == True, models.Request.timestamp >= date_seven_days_ago).order_by(models.Request.id).all(),
                           html = HTMLParser())
