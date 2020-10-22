#!/usr/bin/python
# coding=utf-8
# file: main.py
# author: name <email>
# date: 05-21-2019
'''
# All the packages entry point is from main.py file.
'''

from databasebackupcontroller import DBBackupController
from utility.scheduler import ScheduleProgram
from utility.loggingfile import Log

import argparse
import sys
import os

logger = Log().logging.getLogger(__name__)


class Main():
    def __init__(self):
        logger.info('Initialize settings.')
        self.DBBackupControllerObject = DBBackupController()
        
    def single_run(self):
        self.__run()

    def scheduled_run(self):
        schedule_obj = ScheduleProgram()
        schedule_obj.schedule_program(self.__run)

    def __run(self):
        logger.info('Run database backup process.')
        
        self.DBBackupControllerObject.database_backup()
        logger.info('Database backup is completed.')

    def run_database_restore(self, filepath):
        logger.info('Run database store process.')
        
        self.DBBackupControllerObject.database_restore(filepath)
        logger.info('Database restore is completed.')

        
if __name__ == '__main__':
    # main entry
    logger.info('START APPLICATION')
    app = Main()

    parser = argparse.ArgumentParser()
    parser.add_argument('-pd', metavar='TYPE', type=str, help='input metrics: backup, restore')
    parser.add_argument('-s', action='store_true', help='Scheduled run at specific time')
    parser.add_argument('-f', action='store', help='Insert the path to the backup file')

    args = parser.parse_args()

    # single backup standard run
    if args.pd == 'backup':
        app.single_run()

    # restore run
    if args.pd == 'restore':
        #read content of flag -f and use it
        filepath = args.f
        app.run_database_restore(filepath)
        
    # scheduled backup standard run
    if args.s :
        app.scheduled_run()   

    logger.info('END APPLICATION')




