# file: project.py
# author: Muhammad Mushfiqur Rahman <mushfiq.rahman@tum.de>
# date: 01-07-2019
# This is a image model file.


import sys, os
import uuid
from database.dbutility import time_iso8601


class Project(object):
    def __init__(self):
        #All object parameters have the same name as on the database
        self.Project_Id = None
        self.Project_Name = ""
        self.Date_Project = time_iso8601()
        self.Parent_Project_Id = 0