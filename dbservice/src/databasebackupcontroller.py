# file: labelimagecontroller.py
# author: name <email>
# date: 05-21-2019
'''
# this is a database backup's controller file
'''

import os
from datetime import date
import uuid
import sys
import shutil
from urllib.parse import urlparse
import gzip
#from sh import pg_dump, pg_restore
from pathlib import Path
import psycopg2
import subprocess

from settings import Configuration_Settings
#import labelimageapp.directoryop
#import labelimageapp.util
from utility.signalhandler import PreventShutdown
from utility.loggingfile import Log

logger = Log().logging.getLogger(__name__)

class DBBackupController(object):
    def __init__(self):
        self.configuration_obj = Configuration_Settings()
        self.USER = self.configuration_obj.DATABASE_USER
        self.PORT = self.configuration_obj.DATABASE_PORT
        self.DBNAME = self.configuration_obj.DATABASE_NAME
        self.HOST = self.configuration_obj.DATABASE_HOST
        self.PASSWORD = self.configuration_obj.DATABASE_PASSWORD
        self.date = (date.today()).strftime("%Y%m%d")
        self.location = Path(self.configuration_obj.ROOT_PATH)

    def create_newdb(self):
        """ create tables in the PostgreSQL database"""

        new_db_name = 'db_backup'
    
        command = "CREATE DATABASE " + new_db_name + ";"
    
        conn = None
        try:
            # connect to the PostgreSQL server
            conn = psycopg2.connect(dbname = self.DBNAME, port = self.PORT, user = self.USER, password = self.PASSWORD, host = self.HOST)
            conn.autocommit = True
            cur = conn.cursor()
            # create database
            cur.execute(command)
            cur.execute("GRANT ALL PRIVILEGES ON DATABASE {} TO {} ;".format(new_db_name, self.configuration_obj.DATABASE_USER))
            # close communication with the PostgreSQL database server
            cur.close()
            # commit the changes
            conn.commit()
            logger.info('New database has been created!')
        except (Exception, psycopg2.DatabaseError) as error:
            logger.info(error)
        finally:
            if conn is not None:
                conn.close()
        return new_db_name
                
    
    def delete_db(self):
        """ delete database from the PostgreSQL server"""
        logger.info('BEGIN OLD DATABASE DELETE OPERATION')
        conn = None
        try:           
            # connect to the PostgreSQL server
            conn = psycopg2.connect(dbname = "db_backup", port = self.PORT, user = self.USER, password = self.PASSWORD, host = self.HOST)
            conn.autocommit = True
            cur = conn.cursor()

            cur.execute("SELECT pg_terminate_backend( pid ) "
                    "FROM pg_stat_activity "
                    "WHERE pid <> pg_backend_pid( ) "
                    "AND datname = '{}'".format(self.configuration_obj.DATABASE_NAME))


            # delete old postgres db
            command = "DROP DATABASE " + self.configuration_obj.DATABASE_NAME + ";"
            cur.execute(command)
            
            '''
            cur.execute("SELECT pg_terminate_backend( pid ) "
                    "FROM pg_stat_activity "
                    "WHERE datname = '{}'".format(new_db_name))

            rename_command = "ALTER DATABASE " + new_db_name + " RENAME TO " + self.configuration_obj.DATABASE_NAME + ";"
            cur.execute(rename_command)
            '''

            # close communication with the PostgreSQL database server
            cur.close()
            # commit the changes
            conn.commit()
            logger.info('Old database has been dropped!')
        except (Exception, psycopg2.DatabaseError) as error:
            logger.info(error)
            logger.info('Error from old database delete.')
        finally:
            if conn is not None:
                conn.close()

    def rename_db(self):
        """ rename restored database to old database name"""
        logger.info('BEGIN DATABASE RENAME OPERATION')    
        conn = None
        try:           
            # connect to the PostgreSQL server
            new_db_name = 'db_backup'
            conn = psycopg2.connect(dbname = "postgres", port = self.PORT, user = self.USER, password = self.PASSWORD, host = self.HOST)
            conn.autocommit = True
            cur = conn.cursor()

            '''
            cur.execute("SELECT pg_terminate_backend( pid ) "
                    "FROM pg_stat_activity "
                    "WHERE pid <> pg_backend_pid( ) "
                    "AND datname = '{}'".format(self.configuration_obj.DATABASE_NAME))


            # delete old postgres db
            command = "DROP DATABASE " + self.configuration_obj.DATABASE_NAME + ";"
            cur.execute(command)
            '''

            cur.execute("SELECT pg_terminate_backend( pid ) "
                    "FROM pg_stat_activity "
                    "WHERE datname = '{}'".format(new_db_name))

            rename_command = "ALTER DATABASE " + new_db_name + " RENAME TO " + self.configuration_obj.DATABASE_NAME + ";"
            cur.execute(rename_command)
            # close communication with the PostgreSQL database server
            cur.close()
            # commit the changes
            conn.commit()
            logger.info('Database is successfully renmaed!')
        except (Exception, psycopg2.DatabaseError) as error:
            logger.info(error)
            logger.info('Error from rename.')
        finally:
            if conn is not None:
                conn.close()    

    # using subprocess module, taking backup of the postgres one database i.e. our labeling database in verbose mode.
    def database_backup(self):
        logger.info('STARTING BACKUP PROCESS')
        folderLocation = self.location / 'backup'
        #THIS CREATES THE FOLDER BACKUP
        if not os.path.exists(folderLocation):
            try:
                os.mkdir(folderLocation)
            except OSError:
                logger.info('Creation of the directory failed.')
            
        folderLocation = folderLocation / str(date.today().year)
        #this creates the subdirectory of the year
        if not os.path.exists(folderLocation):
            try:
                os.mkdir(folderLocation)
            except OSError:
                logger.info('Creation of the directory failed.')

        # filename = self.date + '-labelapp-backup.gz'
        filename = self.date + '-labelapp-backup.tar'
        folderLocation = folderLocation / filename
        logger.info(f'Backup file path: {folderLocation}')

        try:
            process = subprocess.Popen(
                ['pg_dump',
                 '--dbname=postgres://{}:{}@{}:{}/{}'.format(self.configuration_obj.DATABASE_USER, 
                                                       self.configuration_obj.DATABASE_PASSWORD, 
                                                       self.configuration_obj.DATABASE_HOST, 
                                                       self.configuration_obj.DATABASE_PORT, 
                                                       self.configuration_obj.DATABASE_NAME),
                 '-Fc',
                 '-f', folderLocation,
                 '-v'],
                stdout=subprocess.PIPE
            )
            output = process.communicate()[0]
            if int(process.returncode) != 0:
                print('Command failed. Return code : {}'.format(process.returncode))
                exit(1)
            return output
        except Exception as e:
            print(e)
            exit(1)

        logger.info('END BACKUP PROCESS')

    '''
    def database_backup(self):
        logger.info('STARTING BACKUP PROCESS')
        folderLocation = self.location / 'backup'
        #THIS CREATES THE FOLDER BACKUP
        if not os.path.exists(folderLocation):
            try:
                os.mkdir(folderLocation)
            except OSError:
                logger.info('Creation of the directory failed.')
            
        folderLocation = folderLocation / str(date.today().year)
        #this creates the subdirectory of the year
        if not os.path.exists(folderLocation):
            try:
                os.mkdir(folderLocation)
            except OSError:
                logger.info('Creation of the directory failed.')

        # filename = self.date + '-labelapp-backup.gz'
        filename = self.date + '-labelapp-backup.tar'
        folderLocation = folderLocation / filename
        with gzip.open(folderLocation, 'wb') as f:
            pg_dump('-h', self.configuration_obj.DATABASE_HOST, '-U', self.configuration_obj.DATABASE_USER, '-Ft', self.configuration_obj.DATABASE_NAME, _out=f)
            
        
        logger.info('END BACKUP PROCESS')
    '''
    
    # /home/mushfiqrahman/dev/develop_branch/labeling/db/backup/2020/20200116-labelapp-backup.tar

    def database_restore(self, filepath):
        #create a new database with name db_backup and then restore the backup file (from filepath) on this new db.

        try:
            logger.info('BEGIN Database restore')           
            
            new_db_name = self.create_newdb()

            try: 
                process = subprocess.Popen(
                    ['pg_restore',
                    '--no-owner',
                    '--dbname=postgres://{}:{}@{}:{}/{}'.format(self.configuration_obj.DATABASE_USER, 
                                                            self.configuration_obj.DATABASE_PASSWORD, 
                                                            self.configuration_obj.DATABASE_HOST, 
                                                            self.configuration_obj.DATABASE_PORT, 
                                                            new_db_name),
                    '-v',
                    filepath],
                    stdout=subprocess.PIPE
                )
                output = process.communicate()[0]
                if int(process.returncode) != 0:
                    print('Command failed. Return code : {}'.format(process.returncode))
                return output
            except Exception as e:
                print("Issue with the db restore : {}".format(e))
        
        except EnvironmentError as error:
            logger.info(error)
        finally:
            self.delete_db()
            self.rename_db()
            logger.info('END Database restore')
            #pass

    '''
    def database_restore(self, filepath):
        #create a new database with name DB_BACKUP
        #if creation is successful, delete old db and rename this one as the deleted one
        #if error stop
        try:
            logger.info('BEGIN Database restore')           
            
            self.create_newdb()
            #self.delete_rename_db()
            self.configuration_obj.DATABASE_NAME = 'postgres'
            self.DBNAME = 'db_backup'
            logger.info('START Database restore')
            pg_restore('-h', self.HOST,'-p', self.PORT, '-U', self.USER,'-Fc', '-d', self.DBNAME, filepath)
            logger.info('END Database restore')
        except EnvironmentError as error:
            logger.info(error)
        finally:
            pass

    '''