# file: labeldal.py
# author: Muhammad Mushfiqur Rahman <mushfiq.rahman@tum.de>
# date: 05-21-2019
'''
# This is a Label Data Access Layer Class file.
# From this layer, DBManager's raw CRUD operations will be called. It will be acted as a wrapper class 
# which in turn call the underlying CRUD operations through the api methods that implemented here. 
'''

import sys, os
import json
import uuid
from database.dbmanager import DBManager
from database.models.label import Label
import database.dbutility as dbutil
from utility.loggingfile import Log

logger = Log().logging.getLogger(__name__)

class LabelDAL(object):
    def __init__(self):
        self.db = DBManager()
        self.db_table_name = 'Label_Details'
        self.order = self.get_label_order()

    def get_label_order(self):
        order = {}
        order['1'] = 'Label_Id'
        order['2'] = 'Image_Id'
        order['3'] = 'Is_Deleted'
        order['4'] = 'Label_Details'
        order['5'] = 'Date_Label'

        return order

    def insert_label_row(self, label = Label()):
        """
        Processing insert query

        @input: label object with the new values

        """
        record = []
        insert_sql= """INSERT INTO "Label_Details" ("Image_Id", "Is_Deleted", "Date_Label", "Label_Details")
                    VALUES(%s, %s, %s, %s) RETURNING "Label_Id";"""

        record = [label.Image_Id,label.Is_Deleted,label.Date_Label,json.dumps(label.Label_Details)]

        row_id = self.db.db_insert_row(insert_sql, record)
        label.Label_Id = row_id
        logger.info(f'Database insert: {self.db_table_name}: {dbutil.dict_to_cs_str(label,self.order)}.')

        return row_id

    def update_label_row(self, label = Label()):
        """
        Processing update query for all parameters except Label_Id and Image_Id

        @input: label object with the new values

        """
        record = []
        update_sql = """UPDATE "Label_Details"
                        SET "Date_Label" = %s,
                            "Label_Details" = %s
                        WHERE "Image_Id" = %s"""
        for key, value in vars(label).items():
            if key != "Label_Id" and key != "Image_Id" and key != "IsDeleted":
                record.append(value)
        record.append(label.Image_Id)
        self.db.db_update_row(update_sql, record)
        logger.info(f'Database update: {self.db_table_name}: {dbutil.dict_to_cs_str(label,self.order)}.')


    def soft_delete_label_row(self, label = Label()):
        """
        Processing soft delete query

        @input: uuid of the Image obj's labeling we want to delete

        """
        soft_delete_sql = """ UPDATE "Label_Details"
                        SET "Is_Deleted" = TRUE
                        WHERE "Image_Id" = %s;"""
        record = (label.Image_Id,)
        self.db.db_delete_row(soft_delete_sql, record)
        logger.info(f'Database soft delete: {self.db_table_name}: {dbutil.dict_to_cs_str(label,self.order)}.')


    def hard_delete_label_row(self, label = Label()):
        """
        Processing hard delete query for junk data

        @input: uuid of the Image obj's labeling we want to delete

        """
        hard_delete_sql = """ DELETE FROM "Label_Details"
                        WHERE "Image_Id" = %s;"""
        record = (label.Image_Id,)
        self.db.db_delete_row(hard_delete_sql, record)
        logger.info(f'Database hard delete: {self.db_table_name}: {dbutil.dict_to_cs_str(label,self.order)}.')


    def get_label_by_uuid(self, image_uuid):
        """
        get one label using the uuid attribute
        """

        sql_query = """SELECT "Label_Details"."Label_Id",
                              "Label_Details"."Image_Id",
                              "Label_Details"."Is_Deleted",
                              "Label_Details"."Date_Label",
                              "Label_Details"."Label_Details"
                        FROM "Label_Details" 
                        WHERE "Image_Id" = %s AND "Is_Deleted" = 'f';"""

        record = (image_uuid,)
        rows = self.db.get_rows_by_condition(sql_query, record)
        labels = []
        for row in rows:
            lbl = Label()
            
            lbl.Label_Id = row[row._index['Label_Id']]
            lbl.Image_Id = uuid.UUID(row[row._index['Image_Id']]).hex
            lbl.Is_Deleted = row[row._index['Is_Deleted']]
            lbl.Date = row[row._index['Date_Label']]
            lbl.Label_Details = row[row._index['Label_Details']]

            labels.append(lbl)

        return labels
