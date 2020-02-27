# Copyright (C) 2019 FZG LEHRSTUHL FÜR MASCHINENELEMENTE. All rights reserved.
# file: loggingfile.py
# author: name <email>
# date: 05-21-2019
'''
# Logging class.
'''

from settings import Configuration_Settings

import logging
import logging.config
import yaml
import os
import datetime


class Log():
    def __init__(self):
        self.configuration_obj = Configuration_Settings()
        self.logging = self.init_logger()

    def init_logger(self):
        with open(os.path.join(self.configuration_obj.LOG_CONFIG_DIR ,'log-config.yaml'), 'r') as f:
            config = yaml.safe_load(f.read())

        handlers = config['handlers']
        stream_handlers = []
        file_handlers =[]
        for handler in handlers:
            handler_name = handlers[handler]['class']
            handler_level = handlers[handler]['level']
            if handler_name == 'logging.StreamHandler':
                stream_handlers.append({'name':handler,'level':handler_level})
            else:
                handler_level = handlers[handler]['level']
                file_handlers.append({'name':handler,'level':handler_level})

        for file_handler in file_handlers:
            file_handler_name = file_handler['name']
            config_file_name = config['handlers'][file_handler_name]['filename']
            year_month_extention = self.get_year_month()
            logfilename = year_month_extention + '-' + config_file_name
            config['handlers'][file_handler_name]['filename'] = os.path.join(self.configuration_obj.LOG_FILE_DIR,logfilename)

        handler_root=[]
        if self.configuration_obj.LOG_CONSOLE_ENABLE == True:
            for stream_handler in stream_handlers:
                handler_root.append(stream_handler['name'])
        if self.configuration_obj.LOG_FILE_ENABLE == True:
            self.check_and_create_folder(self.configuration_obj.LOG_FILE_DIR)
            for file_handler in file_handlers:
                handler_root.append(file_handler['name'])
        config['root']['handlers'] = handler_root

        logging.config.dictConfig(config)

        return logging

    def get_year_month(self):
        year = datetime.date.today().year
        month = datetime.date.today().month
        year_month = f'{year:04}{month:02}'        
        return year_month

    def check_and_create_folder(self,pathname):
        if not os.path.exists(pathname) and not pathname == '':
            os.makedirs(pathname)

