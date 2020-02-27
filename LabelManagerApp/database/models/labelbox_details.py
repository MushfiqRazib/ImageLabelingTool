# file: image.py
# author: Muhammad Mushfiqur Rahman <mushfiq.rahman@tum.de>
# date: 07-10-2019
# This is a labelbox model file.


import sys, os
import uuid
from database.dbutility import time_iso8601

class Labelbox_Details(object):
    def __init__(self):
        #All object parameters have the same name as on the database        
        self.Dataset_Id = ""
        self.Project_Id = None
        self.LB_Project_Id = ""
        self.Dataset_Name = ""
        self.UInterface_ID = ""
        self.UInterface_Name = ""
        self.Date_Labelbox = time_iso8601()