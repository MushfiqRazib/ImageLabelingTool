# file: main.py
# author: name <email>
# date: 05-21-2019
'''
# All the packages entry point is from main.py file.
'''

from labelingapp.labelboxclient import LabelboxClient
from labelimageapp.labelimagecontroller import LabelImageController
from utility.scheduler import ScheduleProgram
from utility.loggingfile import Log

import argparse
import sys
import os

logger = Log().logging.getLogger(__name__)


class Main():
    def __init__(self):
        logger.info('Initialize settings.')
        self.labelImageClientObject = LabelImageController()
        self.labelboxClient  = LabelboxClient()

    def single_run(self):
        self.__run()

    def scheduled_run(self):
        schedule_obj = ScheduleProgram()
        schedule_obj.schedule_program(self.__run)

    def __run(self):
        logger.info('Run application.')
        self.labelImageClientObject.scan_and_insert_processes()   
        self.labelboxClient.transfer_images()
        self.labelboxClient.critical_threshold_labeling_handler()
        self.labelImageClientObject.quality_labeling()
        self.labelboxClient.initiate_labelbox_api()
        logger.info('Done running application.')
    
    def delete_project(self, pid, pname):
        self.labelboxClient.labelbox_details_delete_project(pid, pname)

    def revert_quality_labeling(self, pid=None, pname=None):
        self.labelImageClientObject.revert_quality_labeling(pid,pname)

        
if __name__ == '__main__':
    # main entry
    logger.info('START APPLICATION')
    app = Main()

    parser = argparse.ArgumentParser()
    parser.add_argument('-lb', action='store_true', help='running label app')
    parser.add_argument('-rm', metavar='TYPE', type=str, help='input metrics: project, quality-label')
    parser.add_argument('-pid', metavar='TYPE', type=int, help='Please input the project id')
    parser.add_argument('-pname', metavar='TYPE', type=str, help='Please input the project name')
    parser.add_argument('-s', action='store_true', help='Scheduled run at specifc time')
    args = parser.parse_args()
    
    logger.info(f'ARGUMENTS: {sys.argv}')
    #logger.info(f'ARGUMENTS LENGTH: {len(sys.argv)}')

    # single standard run
    #if not len(sys.argv) > 1:
    if args.lb :
        app.single_run()

    # scheduled standard run
    if args.s :
        app.scheduled_run()
    
    # delete project run
    if args.rm == 'project':
        pid = ''
        pname = ''
        if args.pid != None:
            pid = args.pid
        if args.pname != None:
            pname = args.pname
        app.delete_project(pid,pname)

    # delete quality label run
    if args.rm == 'quality-label':
        pid = ''
        pname = ''
        if args.pid != None:
            pid = args.pid
        if args.pname != None:
            pname = args.pname
        app.revert_quality_labeling(pid,pname)

    logger.info('END APPLICATION')



