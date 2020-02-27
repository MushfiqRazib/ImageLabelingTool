# file: image.py
# author: Muhammad Mushfiqur Rahman <mushfiq.rahman@tum.de>
# date: 05-21-2019
# This is a image model file.

import sys, os
import uuid
from database.dbutility import time_iso8601
# this is a label model file.


class Label(object):
    def __init__(self):
        #All attributes have the same name as on the database
        self.Label_Id = None
        self.Image_Id = None
        self.Is_Deleted = False
        self.Date_Label = time_iso8601()
        self.Label_Details = ""