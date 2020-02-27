# file: imagedal.py
# author: Muhammad Mushfiqur Rahman <mushfiq.rahman@tum.de>
# date: 05-21-2019
'''
# This is a Image Data Access Layer Class file.
# From this layer, DBManager's raw CRUD operations will be called. It will be acted as a wrapper class
# which in turn call the underlying CRUD operations through the api methods that implemented here.
'''

import sys, os
import uuid

from database.dbmanager import DBManager
from database.models.image import Image
import database.dbutility as dbutil
from utility.loggingfile import Log

logger = Log().logging.getLogger(__name__)

class ImageDAL(object):
    def __init__(self):
        self.db = DBManager()
        self.db_table_name = 'Image_Details'
        self.order = self.get_img_order()

    def get_img_order(self):
        order = {}
        order['1'] = 'Image_Id'
        order['2'] = 'Orig_Image_Name'
        order['3'] = 'Ext_Image'
        order['4'] = 'Dir_Image'
        order['5'] = 'Web_Url'
        order['6'] = 'Project_Id'
        order['7'] = 'Labeled'
        order['8'] = 'Critical'
        order['9'] = 'Labeling_Running'
        order['10'] = 'Quality_Labeling'
        order['11'] = 'Is_Deleted'
        order['12'] = 'Date_Image'

        return order

    def insert_image_row(self, img = Image()):
        """
        Processing insert query

        @input: image object with the new values

        """
        record = []
        insert_sql = """INSERT INTO "Image_Details"("Image_Id",
                                                    "Ext_Image",
                                                    "Dir_Image",
                                                    "Web_Url",
                                                    "Project_Id",
                                                    "Labeled",
                                                    "Critical",
                                                    "Labeling_Running",
                                                    "Quality_Labeling",
                                                    "Is_Deleted",
                                                    "Date_Image",
                                                    "Orig_ImageName")
                                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING "Image_Id";"""
        for key, value in vars(img).items():
            record.append(value)

        image_id = self.db.db_insert_row(insert_sql, record)
        logger.info(f'Database insert: {self.db_table_name}: {dbutil.dict_to_cs_str(img,self.order)}.')

        return image_id

    def update_image_row(self, img = Image()):
        """
        Processing update query for all parameters except IsDeleted

        @input: image object with the new values

        """
        record = []
        update_sql = """UPDATE "Image_Details"
                        SET "Ext_Image" = %s,
                            "Dir_Image" = %s,
                            "Web_Url" = %s,
                            "Project_Id" = %s,
                            "Labeled" = %s,
                            "Critical" = %s,
                            "Labeling_Running" = %s,
                            "Quality_Labeling" = %s,
                            "Is_Deleted" = %s,
                            "Date_Image" = %s,
                            "Orig_ImageName" = %s
                        WHERE "Image_Id" = %s;"""

        for key, value in vars(img).items():
            if key != 'Image_Id' and key != 'Project_Name':
                record.append(value)
        record.append(img.Image_Id)
        self.db.db_update_row(update_sql, record)
        logger.info(f'Database update: {self.db_table_name}: {dbutil.dict_to_cs_str(img,self.order)}.')


    def soft_delete_image_row(self, img = Image()):
        """
        Processing soft delete query

        @input: image object with the new values

        """
        soft_delete_sql = """ UPDATE "Image_Details"
                        SET "Is_Deleted" = TRUE
                        WHERE "Image_Id" = %s;"""
        record = (img.Image_Id,)
        self.db.db_delete_row(soft_delete_sql, record)
        logger.info(f'Database soft delete: {self.db_table_name}: {dbutil.dict_to_cs_str(img,self.order)}.')


    def hard_delete_image_row(self, img = Image()):
        """
        Processing hard delete query for junk data

        @input: image object with the new values

        """
        hard_delete_sql = """ DELETE FROM "Image_Details"
                        WHERE "Image_Id" = %s;"""
        record = (img.Image_Id,)
        self.db.db_delete_row(hard_delete_sql, record)
        logger.info(f'Database hard delete: {self.db_table_name}: {dbutil.dict_to_cs_str(img,self.order)}.')

    def get_all_images(self):
        """
        get all the images

        """
        sql_query = """SELECT * FROM "Image_Details" """
        rows = self.db.get_all_rows(sql_query)
        image_obj_list = []
        for row in rows:
            img = Image()

            img.Image_Id = uuid.UUID(row[row._index['Image_Id']]).hex            
            img.Ext_Image = row['Ext_Image']
            img.Dir_Image = row['Dir_Image']
            img.Web_Url = row['Web_Url']
            img.Project_Id = row['Project_Id']
            img.Labeled = row['Labeled']
            img.Critical = row['Critical']
            img.Labeling_Running = row['Labeling_Running']
            img.Quality_Labeling = row['Quality_Labeling']
            img.Is_Deleted = row['Is_Deleted']
            img.Date_Image = row['Date_Image']
            img.Orig_Image_Name = row['Orig_ImageName']
            image_obj_list.append(img)

        return image_obj_list

    def get_images_for_uploading(self):
        """
        get images for uploading
        """

        sql_query = """SELECT "Image_Details"."Image_Id",
                              "Image_Details"."Ext_Image",
                              "Image_Details"."Dir_Image",
                              "Image_Details"."Web_Url",
                              "Image_Details"."Project_Id",
                              "Image_Details"."Labeled",
                              "Image_Details"."Critical",
                              "Image_Details"."Labeling_Running",
                              "Image_Details"."Quality_Labeling",
                              "Image_Details"."Is_Deleted",
                              "Image_Details"."Date_Image",
                              "Image_Details"."Orig_ImageName",
                              "Project_Details"."Project_Name"
                        FROM "Image_Details"
                        INNER JOIN "Project_Details" ON "Project_Details"."Project_Id" = "Image_Details"."Project_Id"
                        WHERE "Labeling_Running" = %s AND "Is_Deleted" = %s AND "Quality_Labeling" = %s;"""

        Labeling_Running = 'f'
        Is_Deleted = 'f'
        Quality_Labeling = 0
        record = (Labeling_Running, Is_Deleted, Quality_Labeling)
        rows = self.db.get_rows_by_condition(sql_query, record)

        image_obj_list = []
        for row in rows:
            img = Image()

            img.Image_Id = uuid.UUID(row[row._index['Image_Id']]).hex            
            img.Ext_Image = row['Ext_Image']
            img.Dir_Image = row['Dir_Image']
            img.Web_Url = row['Web_Url']
            img.Project_Id = row['Project_Id']
            img.Labeled = row['Labeled']
            img.Critical = row['Critical']
            img.Labeling_Running = row['Labeling_Running']
            img.Quality_Labeling = row['Quality_Labeling']
            img.Is_Deleted = row['Is_Deleted']
            img.Date_Image = row['Date_Image']
            img.Orig_Image_Name = row['Orig_ImageName']
            img.Project_Name = row['Project_Name']

            image_obj_list.append(img)

        return image_obj_list

    def get_image_by_uuid(self, image_id):
        """
        get one image using the uuid attribute
        """

        sql_query = """SELECT "Image_Details"."Image_Id",
                              "Image_Details"."Ext_Image",
                              "Image_Details"."Dir_Image",
                              "Image_Details"."Web_Url",
                              "Image_Details"."Project_Id",
                              "Image_Details"."Labeled",
                              "Image_Details"."Critical",
                              "Image_Details"."Labeling_Running",
                              "Image_Details"."Quality_Labeling",
                              "Image_Details"."Is_Deleted",
                              "Image_Details"."Date_Image",
                              "Image_Details"."Orig_ImageName"
                        FROM "Image_Details"
                        WHERE "Image_Id" = %s;"""

        record = (image_id,)
        row = self.db.get_rows_by_condition(sql_query, record)[0]
        img = Image()

        img.Image_Id = uuid.UUID(row[row._index['Image_Id']]).hex        
        img.Ext_Image = row['Ext_Image']
        img.Dir_Image = row['Dir_Image']
        img.Web_Url = row['Web_Url']
        img.Project_Id = row['Project_Id']
        img.Labeled = row['Labeled']
        img.Critical = row['Critical']
        img.Labeling_Running = row["Labeling_Running"]
        img.Quality_Labeling = row['Quality_Labeling']
        img.Is_Deleted = row['Is_Deleted']
        img.Date_Image = row['Date_Image']       
        img.Orig_Image_Name = row['Orig_ImageName']
        return img

    def get_images_by_projectid(self, project_id):
        """
        get all images using the project_id attribute
        """

        sql_query = """SELECT "Image_Details"."Image_Id",
                              "Image_Details"."Ext_Image",
                              "Image_Details"."Dir_Image",
                              "Image_Details"."Web_Url",
                              "Image_Details"."Project_Id",
                              "Image_Details"."Labeled",
                              "Image_Details"."Critical",
                              "Image_Details"."Labeling_Running",
                              "Image_Details"."Quality_Labeling",
                              "Image_Details"."Is_Deleted",
                              "Image_Details"."Date_Image",
                              "Image_Details"."Orig_ImageName"
                        FROM "Image_Details"
                        WHERE "Project_Id" = %s;"""

        record = (project_id,)
        logger.info(f'project_id: {record}.')
        rows = self.db.get_rows_by_condition(sql_query, record)

        logger.info(f'Database: {rows[0]} records get_labelbox_rows_by_project_id successfully.')

        image_obj_list = []
        for row in rows:
            img = Image()
            img.Image_Id = uuid.UUID(row[row._index['Image_Id']]).hex            
            img.Ext_Image = row['Ext_Image']
            img.Dir_Image = row['Dir_Image']
            img.Web_Url = row['Web_Url']
            img.Project_Id = row['Project_Id']
            img.Labeled = row['Labeled']
            img.Critical = row['Critical']
            img.Labeling_Running = row["Labeling_Running"]
            img.Quality_Labeling = row['Quality_Labeling']
            img.Is_Deleted = row['Is_Deleted']
            img.Date_Image = row['Date_Image']
            img.Orig_Image_Name = row['Orig_ImageName']         

            image_obj_list.append(img)

        return image_obj_list

    def get_image_with_quality_label(self, project_id):
        '''
        get all images with a given project ID, where quality labeling is set to 1
        '''

        sql_query = """SELECT "Image_Details"."Image_Id",
                              "Image_Details"."Ext_Image",
                              "Image_Details"."Dir_Image",
                              "Image_Details"."Web_Url",
                              "Image_Details"."Project_Id",
                              "Image_Details"."Labeled",
                              "Image_Details"."Critical",
                              "Image_Details"."Labeling_Running",
                              "Image_Details"."Quality_Labeling",
                              "Image_Details"."Is_Deleted",
                              "Image_Details"."Date_Image",
                              "Image_Details"."Orig_ImageName"
                        FROM "Image_Details"
                        WHERE "Quality_Labeling" = %s AND "Project_Id" = %s;"""

        quality_labeled_value = 1
        record = (quality_labeled_value, project_id)

        rows = self.db.get_rows_by_condition(sql_query, record)

        image_obj_list = []
        for row in rows:
            img = Image()
            img.Image_Id = uuid.UUID(row[row._index['Image_Id']]).hex            
            img.Ext_Image = row['Ext_Image']
            img.Dir_Image = row['Dir_Image']
            img.Web_Url = row['Web_Url']
            img.Project_Id = row['Project_Id']
            img.Labeled = row['Labeled']
            img.Critical = row['Critical']
            img.Labeling_Running = row["Labeling_Running"]
            img.Quality_Labeling = row['Quality_Labeling']
            img.Is_Deleted = row['Is_Deleted']
            img.Date_Image = row['Date_Image']           
            img.Orig_Image_Name = row['Orig_ImageName']
            image_obj_list.append(img)

        return image_obj_list

    def get_images_by_threshold_critical_value(self, critical_value):
        """
        get all images which have threshold critical value
        """

        sql_query = """SELECT "Image_Details"."Image_Id",
                              "Image_Details"."Ext_Image",
                              "Image_Details"."Dir_Image",
                              "Image_Details"."Web_Url",
                              "Image_Details"."Project_Id",
                              "Image_Details"."Labeled",
                              "Image_Details"."Critical",
                              "Image_Details"."Labeling_Running",
                              "Image_Details"."Quality_Labeling",
                              "Image_Details"."Is_Deleted",
                              "Image_Details"."Date_Image",
                              "Image_Details"."Orig_ImageName"
                        FROM "Image_Details"
                        WHERE "Labeling_Running" = %s AND "Is_Deleted" = %s AND "Critical" >= %s;"""

        Labeling_Running = 'f'
        Is_Deleted = 'f'
        record = (Labeling_Running, Is_Deleted, critical_value)
        rows = self.db.get_rows_by_condition(sql_query, record)

        image_obj_list = []
        for row in rows:
            img = Image()
            img.Image_Id = uuid.UUID(row[row._index['Image_Id']]).hex
            img.Ext_Image = row['Ext_Image']
            img.Dir_Image = row['Dir_Image']
            img.Web_Url = row['Web_Url']
            img.Project_Id = row['Project_Id']
            img.Labeled = row['Labeled']
            img.Critical = row['Critical']
            img.Labeling_Running = row["Labeling_Running"]
            img.Quality_Labeling = row['Quality_Labeling']
            img.Is_Deleted = row['Is_Deleted']
            img.Date_Image = row['Date_Image']            
            img.Orig_Image_Name = row['Orig_ImageName']
            image_obj_list.append(img)

        return image_obj_list





