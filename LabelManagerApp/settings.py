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
        #self.ROOT_PATH = r"/home/mushfiqrahman/dev/ProjectRoot"
        #self.ROOT_PATH = r"/home/labelapp/labelingapp/data"
        self.ROOT_PATH = r"/home/labelapp/FZG-NAS/461_DatenBilderkennung"

        # webserver settings
        #self.WEB_SERVER_HOST = "localhost:9000" 
        self.WEB_SERVER_HOST = "tumwfzg-lise.srv.mwn.de:9000"
        
        self.WEB_SERVER_HTTPS = True # True in production 

        # labelbox settings
        self.LABELBOX_UINTERFACE_NAME = "FZG Image Labeling"
        self.LABELBOX_UINTERFACE_LINK = 'https://image-segmentation-v4.labelbox.com'
        self.LABELBOX_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJjanQ1cGRoZGpqcW85MDc4N2Z3dTd2emNxIiwib3JnYW5pemF0aW9uSWQiOiJjanQ1cGRoY3Zqb3BkMDgxMGJyZG5obXMxIiwiYXBpS2V5SWQiOiJjanRpdGM3ZGF6N200MDg1NW9kMXB6Y3VmIiwiaWF0IjoxNTUzMTgzNDc1LCJleHAiOjIxODQzMzU0NzV9.eqeWUOxEPZWowwBretZj4hLhTehLY0aauuJFLayxMjY"

        # logging
        self.LOG_CONSOLE_ENABLE = True
        self.LOG_FILE_ENABLE = True        
        self.LOG_CONFIG_DIR = ''
        self.LOG_FILE_DIR = 'logs'

        # run schedule
        self.SCHEDULE_TIME = '03:30'

        # critical threshold
        self.CRITICAL_THRESHOLD = 3 

