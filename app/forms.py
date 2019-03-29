#!/usr/bin/python
from wtforms import StringField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import Form
import csv
import os
import sys

class CurrentDataForm(Form):
    submit_current = SubmitField('submit')
    fieldpoly = StringField('fieldpoly', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])

class CropSelectorForm(Form):
    crops_submit = SubmitField('submit')
    crops = []
    with open(os.path.join(sys.path[0], 'app/crop_type.csv'), 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            crops.append(((str(row[1])[2:-1]),row[0]))

    fieldpoly = StringField('fieldpoly', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    crop_type = SelectField('Crop Types', choices=crops)
    season = SelectField('Season', choices=[('2016', '2016'), ('2017', '2017'), ('2018', '2018')]) #('2016', '2016'),


class FarmInfoForm(Form):


    email = StringField('email', validators=[DataRequired()])
    season = SelectField('Season', choices=[('2017', '2017'), ('2018', '2018')]) #('2016', '2016'),
