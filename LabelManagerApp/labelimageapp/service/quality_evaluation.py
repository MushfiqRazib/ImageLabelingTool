# file: labelbox.py
# author: Muhammad Mushfiqur Rahman <mushfiq.rahman>
# date: 05-21-2019


import os
import uuid

from database.models.image import Image
from database.dal.imagedal import ImageDAL
from database.models.project import Project
from database.dal.projectdal import ProjectDAL
from database.models.label import Label
from database.dal.labeldal import LabelDAL
from database.dbmanager import DBManager
from utility.loggingfile import Log

logger = Log().logging.getLogger(__name__)



class QualityEvaluation():
    def __init__(self):
        self.label_access_obj = LabelDAL()

    def quality_criteria(self, img=Image()):
        image_id = uuid.UUID(img.Image_Id).hex
        fname = image_id + '.' + img.Ext_Image
        if img.Labeled >= 1:
            logger.debug(f'Image: {fname} fullfills quality criteria.')
            labels = self.label_access_obj.get_label_by_uuid(image_id)
            img.Quality_Labeling = labels[0].Label_Id
            return img, True
        else:
            logger.debug(f'Image: {fname} does not fullfill quality criteria.')
            return img, False








