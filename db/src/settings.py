# Copyright (C) 2019 FZG LEHRSTUHL FÜR MASCHINENELEMENTE. All rights reserved.
# file: settings.py
# author: name <email>
# date: 05-21-2019
'''
This is the application settings file.
'''
DEFAULT_CONFIG = {"user": "user1", "database": "db1"}

class Configuration_Settings(object):
    def __init__(self):
        # database settings
        self.DATABASE_NAME = "labelingdb"
        self.DATABASE_USER = "postgres"
        self.DATABASE_PASSWORD = "postgres"
        self.DATABASE_HOST = "localhost"
        self.DATABASE_PORT = "5432"

        # project root settings
        #self.ROOT_PATH = r"/home/mushfiqrahman/dev/develop_branch/labeling/db"
        #elf.ROOT_PATH = r"/home/mushfiqrahman/dev/backupdb"
        self.ROOT_PATH = r"/usr/src/app/data"
        

        # logging
        self.LOG_CONSOLE_ENABLE = True
        self.LOG_FILE_ENABLE = True        
        self.LOG_CONFIG_DIR = ''
        self.LOG_FILE_DIR = 'logs'

        # run schedule
        self.SCHEDULE_TIME = '03:30'
        


