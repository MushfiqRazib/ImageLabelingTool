# file: projectdal.py
# author: Muhammad Mushfiqur Rahman <mushfiq.rahman@tum.de>
# date: 05-21-2019
'''
# This is a Project Data Access Layer Class file.
# From this layer, DBManager's raw CRUD operations will be called. It will be acted as a wrapper class
# which in turn call the underlying CRUD operations through the api methods that implemented here.
'''

import sys, os

from database.dbmanager import DBManager
from database.models.project import Project
import database.dbutility as dbutil
from utility.loggingfile import Log

logger = Log().logging.getLogger(__name__)

class ProjectDAL(object):
    def __init__(self):
        self.db = DBManager()
        self.db_table_name = 'Project_Details'
        self.order = self.get_project_order()

    def get_project_order(self):
        order = {}
        order['1'] = 'Project_Id'
        order['2'] = 'Project_Name'
        order['3'] = 'Date_Project'
        order['4'] = 'Parent_Project_Id'

        return order

    def insert_project(self, project = Project()):
        """
        Processing insert query

        @input: Project object with the new values

        """
        record = []

        insert_sql = """INSERT INTO "Project_Details"("Project_Name","Date_Project", "Parent_Project_Id")
             VALUES(%s, %s, %s) RETURNING "Project_Id";"""

        for key, value in vars(project).items():
            if key != 'Project_Id':
                record.append(value)

        #logger.info(f'Database insert_sql query: {insert_sql}')
        row_id = self.db.db_insert_row(insert_sql, record)
        project.Project_Id = row_id
        logger.info(f'Database insert: {self.db_table_name}: {dbutil.dict_to_cs_str(project,self.order)}.')
        return row_id

    def update_project(self, project = Project()):
        """
        Processing update query for all parameters except IsDeleted

        @input: Project object with the new values

        """
        record = []
        sql_query = """UPDATE "Project_Details"
                        SET "Project_Name" = %s, "Date_Project" = %s WHERE "Project_Id" = %s"""

        for key, value in vars(project).items():
            if key != "Project_Id":
                record.append(value)
        self.db.db_update_row(sql_query, record)
        logger.info(f'Database update: {self.db_table_name}: {dbutil.dict_to_cs_str(project,self.order)}.')


    def soft_delete_project_row(self, project = Project()):
        """
        Processing soft delete query

        @input: project object with the new values

        """
        soft_delete_sql = """ UPDATE "Project_Details"
                        SET "Is_Deleted" = TRUE
                        WHERE "Project_Id" = %s;"""
        record = (project.Project_Id,)
        self.db.db_delete_row(soft_delete_sql, record)
        logger.info(f'Database soft delete: {self.db_table_name}: {dbutil.dict_to_cs_str(project,self.order)}.')


    def hard_delete_project_row(self, project = Project()):
        """
        Processing hard delete query for junk data

        @input: project object with the new values

        """
        hard_delete_sql = """ DELETE FROM "Project_Details"
                        WHERE "Project_Id" = %s;"""
        record = (project.Project_Id,)
        self.db.db_delete_row(hard_delete_sql, record)
        logger.info(f'Database hard delete: {self.db_table_name}: {dbutil.dict_to_cs_str(project,self.order)}.')

    def get_all_projects_ids(self):
        """
        get all the projects ids

        """
        sql_query = """SELECT * FROM "Project_Details" """
        rows = self.db.get_all_rows(sql_query)
        project_ids_list = []
        for row in rows:
            project_ids_list.append(row['Project_Id'])
        return project_ids_list

    def get_all_parent_projects_ids(self):
        """
        get all the parent projects ids 

        """
        sql_query = """select * from "Project_Details" WHERE "Parent_Project_Id" IS NULL """
        rows = self.db.get_all_rows(sql_query)
        parent_project_ids_list = []
        for row in rows:
            parent_project_ids_list.append(row['Project_Id'])
        return parent_project_ids_list

    def get_all_critical_projects_ids(self):
        """
        get all the critical (child) projects ids 

        """
        sql_query = """select * from "Project_Details" WHERE "Parent_Project_Id" IS NOT NULL """
        rows = self.db.get_all_rows(sql_query)
        critical_project_ids_list = []
        for row in rows:
            critical_project_ids_list.append(row['Parent_Project_Id'])
        return critical_project_ids_list

    def get_project_id(self, projectName):
        """
        get project name by projectName
        @input: projectName

        """
        update_sql = """SELECT "Project_Id" FROM "Project_Details" WHERE "Project_Name" = %s"""
        record = (projectName,)
        project_row = self.db.get_row_by_key(update_sql, record)

        if project_row is None:
            logger.error('Invalid Project Name.', exc_info=True)
            return None
        else:
            return project_row[0]

    def get_critical_project_id(self, parent_id):
        """
        get project name by projectName
        @input: projectName

        """
        update_sql = """select * from "Project_Details" WHERE "Parent_Project_Id" = %s"""
        record = (parent_id,)
        project_row = self.db.get_row_by_key(update_sql, record)

        if project_row is None:
            logger.error('Invalid Project id.', exc_info=True)
            return None
        else:
            return project_row[0]

    def get_parent_project_id(self, critical_id):
        """
        get parent project id by critical_id
        @input: critical_id

        """
        update_sql = """select "Parent_Project_Id" from "Project_Details" WHERE "Project_Id" = %s"""
        record = (critical_id,)
        project_row = self.db.get_row_by_key(update_sql, record)

        if project_row is None:
            logger.error('Invalid Project id.', exc_info=True)
            return None
        else:
            return project_row[0]

    def get_all_projects_name(self):
        """
        get all the projects name

        """
        sql_query = """SELECT * FROM "Project_Details" """
        rows = self.db.get_all_rows(sql_query)
        project_names_list = []
        for row in rows:
            project_names_list.append(row['Project_Name'])
        return project_names_list


    def get_project_name(self, project_id):
        """
        get project name by project id

        """
        update_sql = """SELECT "Project_Name" FROM "Project_Details" WHERE "Project_Id" = %s"""
        record = (project_id,)
        project_row = self.db.get_row_by_key(update_sql, record)

        if project_row is None:
            logger.error('Invalid Project Name.', exc_info=True)
            return None
        else:
            return project_row[0]
