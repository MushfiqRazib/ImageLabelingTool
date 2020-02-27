# file: image.py
# author: Muhammad Mushfiqur Rahman <mushfiq.rahman@tum.de>
# date: 05-21-2019
# This is a image model file.


import sys, os
import uuid
from database.dbutility import time_iso8601
from database.models.project import Project

class Image(object):
    def __init__(self):
        #All object parameters have the same name as on the database  
        #self.project = Project()              
        self.Image_Id = uuid.uuid4().hex
        self.Ext_Image = ""
        self.Dir_Image = ""
        self.Web_Url = ""
        self.Project_Id = ""
        self.Labeled = 0
        self.Critical = 0
        self.Labeling_Running = False
        self.Quality_Labeling = 0
        self.Is_Deleted = False
        self.Date_Image = time_iso8601()
        self.Orig_Image_Name = ""

    