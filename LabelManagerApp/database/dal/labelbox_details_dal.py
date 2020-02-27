# file: labelbox.py
# author: Muhammad Mushfiqur Rahman <mushfiq.rahman@tum.de>
# date: 07-10-2019
'''
# This is a Labelbox Data Access Layer Class file.
# From this layer, DBManager's raw CRUD operations will be called. It will be acted as a wrapper class
# which in turn call the underlying CRUD operations through the api methods that implemented here.
'''

import sys, os
from database.dbmanager import DBManager
from database.models.labelbox_details import Labelbox_Details
import database.dbutility as dbutil
from utility.loggingfile import Log

logger = Log().logging.getLogger(__name__)

class Labelbox_Details_DAL(object):
    def __init__(self):
        self.db = DBManager()
        self.db_table_name = 'Labelbox_Details'
        self.order = self.get_lbObj_order()

    def get_lbObj_order(self):
        order = {}
        order['1'] = 'Dataset_Id'
        order['2'] = 'Dataset_Name'
        order['3'] = 'Project_Id'
        order['4'] = 'LB_Project_Id'
        order['5'] = 'UInterface_ID'
        order['6'] = 'UInterface_Name'
        order['7'] = 'Date_Labelbox'

        return order

    def insert_labelbox_row(self, lbObj = Labelbox_Details()):
        """
        Processing insert query

        @input: Labelbox object with the new values

        """
        record = []
        insert_sql = """INSERT INTO "Labelbox_Details"("Dataset_Id",
                                                    "Project_Id",
                                                    "LB_Project_Id",
                                                    "Dataset_Name",
                                                    "UInterface_ID",
                                                    "UInterface_Name",
                                                    "Date_Labelbox")
                                    VALUES(%s, %s, %s, %s, %s, %s, %s) RETURNING "Dataset_Id";"""

        for key, value in vars(lbObj).items():
            record.append(value)

        self.db.db_insert_row(insert_sql, record)
        logger.info(f'Database insert: {self.db_table_name}: {dbutil.dict_to_cs_str(lbObj,self.order)}.')

    def update_labelbox_row(self, lbObj = Labelbox_Details()):
        """
        Processing update query for all parameters except IsDeleted

        @input: Labelbox object with the new values

        """
        record = []
        update_sql = """UPDATE "Labelbox_Details"
                        SET "Project_Id" = %s,
                            "LB_Project_Id" = %s,
                            "Dataset_Name" = %s,
                            "UInterface_ID" = %s,
                            "UInterface_Name" = %s,
                            "Date_Labelbox" = %s
                        WHERE "Dataset_Id" = %s;"""

        for key, value in vars(lbObj).items():
            if key != "Dataset_Id":
                record.append(value)
        record.append(lbObj.Dataset_Id)
        self.db.db_update_row(update_sql, record)
        logger.info(f'Database update: {self.db_table_name}: {dbutil.dict_to_cs_str(lbObj,self.order)}.')


    def hard_delete_labelbox_row(self, lbObj = Labelbox_Details()):
        """
        Processing hard delete query for junk data

        @input: Labelbox object with the new values

        """
        hard_delete_sql = """ DELETE FROM "Labelbox_Details"
                        WHERE "Dataset_Id" = %s;"""
        record = (lbObj.Dataset_Id,)
        self.db.db_delete_row(hard_delete_sql, record)
        logger.info(f'Database hard delete: {self.db_table_name}: {dbutil.dict_to_cs_str(lbObj,self.order)}.')

    def get_all_labelbox_rows(self):
        """
        get all the Labelbox

        """
        sql_query = """SELECT * FROM "Labelbox_Details" """
        rows = self.db.get_all_rows(sql_query)
        obj_list = []
        for row in rows:
            lbox = Labelbox_Details()

            lbox.Dataset_Id = row['Dataset_Id']
            lbox.Project_Id = row['Project_Id']
            lbox.LB_Project_Id = row['LB_Project_Id']
            lbox.Dataset_Name = row['Dataset_Name']
            lbox.UInterface_ID = row['UInterface_ID']
            lbox.UInterface_Name = row['UInterface_Name']
            lbox.Date_Labelbox = row['Date_Labelbox']
            obj_list.append(lbox)

        return obj_list

    def get_distinct_labelbox_rows(self):
        """
        get distinct Labelbox rows

        """
        sql_query = """SELECT DISTINCT "Dataset_Id", "Project_Id", "LB_Project_Id" from "Labelbox_Details" """
        rows = self.db.get_all_rows(sql_query)
        obj_list = []
        for row in rows:
            lbox = Labelbox_Details()

            lbox.Dataset_Id = row['Dataset_Id']
            lbox.Project_Id = row['Project_Id']
            lbox.LB_Project_Id = row['LB_Project_Id']
            obj_list.append(lbox)

        return obj_list

    def get_labelbox_rows_by(self):
        """
        get Labelbox for uploading
        """
        sql_query = """SELECT * FROM "Labelbox_Details" WHERE "Dataset_Id" = %s
                                                        AND "LB_Project_Id" = %s
                                                        AND "Project_Id" = %s"""
        Labeling_Running = 'f'
        Is_Deleted = 'f'
        Quality_Labeling = 0
        record = (Labeling_Running, Is_Deleted, Quality_Labeling)
        rows = self.db.get_rows_by_condition(sql_query, record)

        obj_list = []
        for row in rows:
            lbox = Labelbox_Details()

            lbox.Dataset_Id = row['Dataset_Id']
            lbox.Project_Id = row['Project_Id']
            lbox.LB_Project_Id = row['LB_Project_Id']
            lbox.Dataset_Name = row['Dataset_Name']
            lbox.UInterface_ID = row['UInterface_ID']
            lbox.UInterface_Name = row['UInterface_Name']
            lbox.Date_Labelbox = row['Date_Labelbox']
            obj_list.append(lbox)

        return obj_list


    def get_dataset_id(self, projectId):
        """
        get dataset id by projectId
        @input: projectId

        """
        sql_query = """SELECT "Dataset_Id" FROM "Labelbox_Details" WHERE "Project_Id" = %s"""
        record = (projectId,)
        row = self.db.get_row_by_key(sql_query, record)

        if row is not None:
            return row[0]
        else:
            return None

    def get_labelbox_rows_by_project_id(self, projectId):
        """
        get Labelbox for uploading
        """
        sql_query = """SELECT * FROM "Labelbox_Details" WHERE "Project_Id" = %s"""
        record = (projectId,)
        row = self.db.get_row_by_key(sql_query, record)

        logger.info(f'Database: {row} records get_labelbox_rows_by_project_id successfully.')

        if row is not None:
            lbox = Labelbox_Details()
    
            '''
            lbox.Dataset_Id = row['Dataset_Id']
            lbox.Project_Id = row['Project_Id']
            lbox.LB_Project_Id = row['LB_Project_Id']
            lbox.Dataset_Name = row['Dataset_Name']
            lbox.UInterface_ID = row['UInterface_ID']
            lbox.UInterface_Name = row['UInterface_Name']
            lbox.Date_Labelbox = row['Date_Labelbox']
            '''

            lbox.Dataset_Id = row[0]
            lbox.Dataset_Name = row[1]
            lbox.Project_Id = row[2]
            lbox.LB_Project_Id = row[3]            
            lbox.UInterface_ID = row[4]
            lbox.UInterface_Name = row[5]
            lbox.Date_Labelbox = row[6]

            return lbox

        else:
            return None

    def hard_delete_labelbox_details_row_by_projectId(self, lbObj = Labelbox_Details()):
        """
        Processing hard delete query for junk data

        @input: labelbox object with the new values

        """
        hard_delete_sql = """ DELETE FROM "Labelbox_Details"
                        WHERE "Project_Id" = %s;"""
        record = (lbObj.Project_Id,)
        self.db.db_delete_row(hard_delete_sql, record)


    def get_all_LB_projects_id(self):
        """
        get all the Labelbox project_ids

        """
        sql_query = """SELECT "LB_Project_Id" FROM "Labelbox_Details" """
        rows = self.db.get_all_rows(sql_query)
        obj_list = []
        for row in rows:
            if row not in obj_list:
                obj_list.extend(row)

        return obj_list

    def get_project_name(self,LB_project_id):
        """
        get project_name from Labelbox project id

        """
        sql_query = """SELECT "Project_Name" FROM "Project_Details"
                       INNER JOIN "Labelbox_Details" ON "Labelbox_Details"."Project_Id" = "Project_Details"."Project_Id"
                       WHERE "Labelbox_Details"."LB_Project_Id" = %s;"""
        record = (LB_project_id,)
        row = self.db.get_row_by_key(sql_query, record)

        if row is not None:
            return row[0]
        else:
            return None
