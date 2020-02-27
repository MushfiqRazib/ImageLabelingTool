# file: dbmanager.py
# author: Muhammad Mushfiqur Rahman <mushfiq.rahman@tum.de>
# date: 05-21-2019
'''
# dbmanager.py file implemented only basic CRUD operations of database operations.
# DBManager only provide us the basic insert, update, delete and retrieve operations. Retrieve/Fetching operations have to write here.
# For bulk insert, update, delete operations with multiple rows, Cursor.executemany() have to be implemented in separate methods for PostgreSQL table.
# From the database.dal, underlying database basic operations will be called with necessary sql command queries.
'''
import sys, os
import psycopg2
import psycopg2.extras
from settings import Configuration_Settings
from utility.loggingfile import Log

logger = Log().logging.getLogger(__name__)


# settings file contain database related credentials information like user, pwd, host, port, db name etc.
# DBManager class is a singleton class.
# didn't implement db connection singleton here.. needs to be done later.

# #example code -
class DBManager(object):
    def __init__(self):
        self.configuration_obj = Configuration_Settings()
        self.DATABASE_NAME = self.configuration_obj.DATABASE_NAME
        self.USER = self.configuration_obj.DATABASE_USER
        self.HOST = self.configuration_obj.DATABASE_HOST
        self.PASSWORD = self.configuration_obj.DATABASE_PASSWORD
        self.PORT = self.configuration_obj.DATABASE_PORT


    def __db_connect(self):
        # open the db connection
        logger.info(f'Database: Starting to connect.')
        connection = psycopg2.connect(user=self.USER,
                                password=self.PASSWORD,
                                host=self.HOST,
                                port=self.PORT,
                                database=self.DATABASE_NAME)
        logger.info(f'Database: Connection established.')
        return connection

    def __db_close(self,cursor,connection):
        # close the db connection
        cursor.close()
        connection.close()
        logger.info(f'Database: Connection closed.')

    def db_insert_row(self, sql_insert_query, record):
        # define database insert operation
        new_row_id = ''
        try:
            connection = self.__db_connect()
            cursor = connection.cursor()
            cursor.execute(sql_insert_query, record)
            connection.commit()
            count = cursor.rowcount
            new_row_id = cursor.fetchone()[0]
            logger.info(f'Database: {count} record inserted successfully.')
        except (Exception, psycopg2.Error) as error :
            if(connection):
                logger.error("Database: Failed to insert record.", exc_info=True)
            return -99
        finally:
            #closing database connection.
            if(connection):
                self.__db_close(cursor,connection)
            return new_row_id


    def db_update_row(self, sql_update_query, record):
        try:
            connection = self.__db_connect()
            cursor = connection.cursor()
            cursor.execute(sql_update_query, record)
            connection.commit()

            count = cursor.rowcount
            logger.info(f'Database: {count} record updated successfully.')
        except (Exception, psycopg2.Error) as error:
            logger.error("Database: Failed to update record.", exc_info=True)
        finally:
            # closing database connection.
            if (connection):
                self.__db_close(cursor,connection)

    def db_delete_row(self, sql_delete_query, anyId):
        try:
            connection = self.__db_connect()
            cursor = connection.cursor()
            cursor.execute(sql_delete_query, (anyId, ))
            connection.commit()
            count = cursor.rowcount
            logger.info(f'Database: {count} record deleted successfully.')

        except (Exception, psycopg2.Error) as error:
            logger.error("Database: Failed to delete record.", exc_info=True)

        finally:
            # closing database connection.
            if (connection):
                self.__db_close(cursor,connection)

    # Get all rows from a table
    def get_all_rows(self, sql_fetch_query):
        try:
            connection = self.__db_connect()
            cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute(sql_fetch_query)
            all_rows = cursor.fetchall()
            connection.commit()
            count = cursor.rowcount
        except (Exception, psycopg2.Error) as error:
            logger.error("Database: Failed to get all rows.", exc_info=True)
            return -999
        finally:
            # closing database connection.
            if (connection):
                self.__db_close(cursor,connection)
            return all_rows

    def get_row_by_key(self, sql_fetch_query, anyKey):
        try:
            connection = self.__db_connect()
            cursor = connection.cursor()
            cursor.execute(sql_fetch_query, (anyKey, ))
            row = cursor.fetchone()
            connection.commit()
            count = cursor.rowcount
            #logger.info(f'Database: {count} records get_row_by_key successfully.')
        except (Exception, psycopg2.Error) as error:
            logger.error("Database: Failed to get row by key.", exc_info=True)
            return -999
        finally:
            # closing database connection.
            if (connection):
                self.__db_close(cursor,connection)
            #logger.info(f'Database: {row} records get_row_by_key successfully.')
            return row


    # Get all rows from a table
    def get_rows_by_condition(self, sql_fetch_query, record):
        try:
            connection = self.__db_connect()
            cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
            #logger.info(f'sql_fetch_query: {sql_fetch_query} {record}')
            cursor.execute(sql_fetch_query, record)
            all_rows = cursor.fetchall()
            #logger.info(f'all_rows[0]: {all_rows[0]} retrieved')
            connection.commit()
        except (Exception, psycopg2.Error) as error:
            logger.error("Database: Failed to get row by condition.", exc_info=True)
            return -999
        finally:
            # closing database connection.
            if (connection):
                self.__db_close(cursor,connection)
            return all_rows
