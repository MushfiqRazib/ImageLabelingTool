# file: labelimagecontroller.py
# author: name <email>
# date: 05-21-2019
'''
# this is a labelimageapp's controller file which imports LabelManagerApp.database package. 
# From this package and module, labelimageapp will implement labeling functionality by communicating with LabelManagerApp.database.dal module.
'''

import os
import datetime
import uuid
import sys
import shutil
from urllib.parse import urlparse

from database.models.image import Image
from database.models.label import Label
from database.dal.labeldal import LabelDAL
from database.dal.imagedal import ImageDAL
from database.models.project import Project
from database.dal.projectdal import ProjectDAL
from labelimageapp.quality_evaluation import QualityEvaluation
from settings import Configuration_Settings
import labelimageapp.directoryop
import labelimageapp.util
from utility.signalhandler import PreventShutdown
from utility.loggingfile import Log

logger = Log().logging.getLogger(__name__)



class LabelImageController(object):
    def __init__(self):
        self.isImageProcessing = False
        self.configuration_obj = Configuration_Settings()
        self.project_directories = []
        self.project_directories_from_db = []
        self.current_project_id = 0
        self.project_root_dir = labelimageapp.directoryop.DirectoryStructure(self.configuration_obj.ROOT_PATH)
        self.project_access_obj = ProjectDAL()
        self.image_access_obj = ImageDAL()
        self.label_access_obj = LabelDAL()
        self.utility = labelimageapp.util.Utility()
        self.quality_obj = QualityEvaluation()
              
    def scan_and_insert_processes(self):
        logger.info('START SCAN AND INSERT')
        logger.info('Start scan and insert of project root directory.')
        logger.info(f'Project root directory: {self.project_root_dir.project_root_path}.')
        # Get project directories from the db
        self.project_directories_from_db,_ = self.get_all_projects_from_db()

        if os.path.exists(self.project_root_dir.project_root_path):
            self.project_directories = self.project_root_dir.get_immediate_subdirectories(self.configuration_obj.ROOT_PATH)
            project_directories_str = ', '.join(self.project_directories)
            logger.info(f'Project directories in project root: {project_directories_str}.')

            if len(self.project_directories) != 0:
                # iterate over all the project directories
                for ind in range(len(self.project_directories)):
                    cur_project_name = self.project_directories[ind]
                    cur_project_path = os.path.join(self.configuration_obj.ROOT_PATH, cur_project_name,'')
                    logger.info(f'Current project: {cur_project_name}, {cur_project_path}')

                    # check whether the project directory is already exists in db. 
                    # If yes, than get the project id from db for that project. 
                    # If not exists in db than insert it to db and create subdirectories for that project.
                    if cur_project_name in self.project_directories_from_db:
                        logger.info(f'Project: {cur_project_name} already exists in database. No new record created.')
                        self.current_project_id = self.get_project_id_from_db(cur_project_name)
                    else:
                        with PreventShutdown() as ps:
                            self.current_project_id = self.insert_project_info(cur_project_name)
                            logger.info(f'Project: {cur_project_name} does not exist in database. Inserted in database with project id: {self.current_project_id}.')
                            # create sub-directories for this new inserted project.
                            if self.current_project_id is not None:
                                try:    
                                    self.project_root_dir.create_subdirectories(cur_project_name)
                                    logger.debug('Project subdirectories created.')
                                except:
                                    self.delete_project_info(self.current_project_id)
                                    logger.error('Reverted database entry due to file system error.', exc_info=True)
                    
                    # Iterate over project directory files/images and add to database
                    self.scan_project_directory(self.current_project_id, cur_project_path)
            else:
                logger.warning('No project directories available. Create a project directory manually.')
        else:
            logger.error('Project root directory is not a valid directory.', exc_info=True)

        logger.info('End scan and insert of project root directory.')
        logger.info('END SCAN AND INSERT')

    def scan_project_directory(self, project_id, project_path):
        #print('------------------- from scan_project_directory method -----------------')
        # self.project_root_dir = labelimageapp.directoryop.DirectoryStructure(self.configuration_obj.ROOT_PATH)
        # Iterate over project directory files/images
        project_name = self.project_access_obj.get_project_name(project_id)
        logger.info(f'Start inserting and moving images for project: {project_name}.')
        images_inserted = 0
        for fname in os.listdir(project_path):
            if (fname.endswith('.jpg') or fname.endswith('.jpeg') or fname.endswith('.png') or fname.endswith('.gif') or fname.endswith('.bmp')):
                logger.info(f'Start moving and inserting image: {fname}')
                img = self.create_insert_imagefile(fname, project_path, project_id, self.project_root_dir.unlabeled) # inserting and getting uuid of the current insert row  
                self.dbmodify_and_move_image(img, destination='unlabeled',option='insert')
                images_inserted +=1
        logger.info(f'End inserting and moving images for project: {project_name}. Total number of inserted images: {images_inserted}.')
    
    def quality_labeling(self):
        logger.info('START QUALITY EVALUATION')
        logger.info('Start quality labeling evaluation.')

        # get all the images records from Image_details table.
        image_list = self.image_access_obj.get_all_images()

        not_update_required = []
        n_quality_labeled = 0
        for key, value in enumerate(image_list):
            img = Image()
            img = image_list[key]

            if img.Quality_Labeling == 0 and img.Labeling_Running == False:
                img,status = self.quality_obj.quality_criteria(img)
                if status:
                    self.update_and_move_image(img,'quality_labeled')
                    n_quality_labeled += 1
                                 
        logger.info(f'End quality labeling evaluation. Total number of new quality labeled images: {n_quality_labeled}.')   
        logger.info('END QUALITY EVALUATION')

    def revert_quality_labeling(self,pid,pname):
        logger.info('START DELETING QUALITY LABELS')
        logger.info('Start deleting quality labels in database.')

        _, project_id_list = self.get_all_projects_from_db()
        
        projects_ids_to_change = project_id_list
        if pname != '':
            try:
                logger.info(f'Current project name: {pname}.')
                pid = self.project_access_obj.get_project_id(pname)
            except:
                logger.warning(f'Database: Could not access project id with project name.')
        if pid != '':
            logger.info(f'Deleting specific project.')
            projects_ids_to_change = [pid]

        n_revert_quality_labeled = 0
        for project_id in projects_ids_to_change:
            images = self.image_access_obj.get_image_with_quality_label(project_id)
            for img in images:
                img.Quality_Labeling = 0
                self.dbmodify_and_move_image(img, destination='labeled', option='update')
                n_revert_quality_labeled += 1
                
        logger.info(f'End deleting quality labels in database. Total number of deleted quality labeled images: {n_revert_quality_labeled}.')
        logger.info('END DELETING QUALITY LABELS')

    def dbmodify_and_move_image(self, img, destination, option):
        project_name = self.project_access_obj.get_project_name(img.Project_Id)
        new_file_name,current_file_path = self.get_image_name_and_path(img)
        old_img_dir = img.Dir_Image
        if option == 'insert':
            current_file_path = os.path.join(img.Dir_Image,img.Orig_Image_Name + '.' + img.Ext_Image)
        logger.info(f'Database {option} and move image: {new_file_name} from project: {project_name} to {destination}.')

        with PreventShutdown() as ps:
            filesystem_success = False
            database_success = False

            try:
                image_path,sub_dir,_ = self.imagefile_move(current_file_path,project_name,new_file_name, destination)
                filesystem_success = True
            except:
                logger.error(f'Could not execute file system operation.', exc_info=True)
                return None

            image_url = self.imagefile_web_url(image_path, sub_dir, img.Image_Id, img.Ext_Image)
            img.Dir_Image = os.path.join(image_path,sub_dir,'')
            img.Web_Url = image_url

            if filesystem_success == True:
                try:
                    if option == 'insert':
                        self.image_access_obj.insert_image_row(img)
                    elif option == 'update':
                        self.image_access_obj.update_image_row(img)
                    database_success = True
                except:
                    logger.error(f'Could not execute database operation for image: {img.Image_Id}. Revert file system operation ...', exc_info=True)
                    current_file_path,project_name,new_file_name, destination = self.revert_direction_filepath(current_file_path,project_name,new_file_name, destination)
                    self.imagefile_move(current_file_path,project_name,new_file_name, destination)
                    logger.error(f'Could not execute database operation. Revert file system operation done.', exc_info=True)
                    raise

    def insert_project_info(self, project_name):
        projectObject = Project()
        projectObject.Project_Name = project_name
        
        project_id = self.project_access_obj.insert_project(projectObject)
        return project_id

    def delete_project_info(self, project_id):
        projectObject = Project() 
        projectObject.Project_Id = project_id

        self.project_access_obj.hard_delete_project_row(projectObject)

    def get_all_projects_from_db(self):
        project_name_list = self.project_access_obj.get_all_projects_name()
        project_id_list = self.project_access_obj.get_all_projects_ids()
        return project_name_list, project_id_list

    def get_project_id_from_db(self, project_name):
        projectid = self.project_access_obj.get_project_id(project_name)
        return projectid

    def create_insert_imagefile(self, filenamewithextension, image_dir, project_id, sub_dir):
        img = Image()
        
        #img.No_Of_Image = 0
        filename = os.path.splitext(filenamewithextension)[0]
        ext_name = os.path.splitext(filenamewithextension)[1][1:]

        # populate all the image properties/values        
        img.Ext_Image = ext_name
        img.Dir_Image = image_dir
        img.Web_Url = self.imagefile_web_url(image_dir, sub_dir, img.Image_Id, img.Ext_Image)
        img.Project_Id = project_id
        img.Labeled = 0
        img.Critical = 0
        img.Labeling_Running = False
        img.Quality_Labeling = 0
        img.Is_Deleted = False
        img.Orig_Image_Name = filename

        return img

    def delete_imagefile(self, image_id):
        img = Image()
        img.Image_Id = image_id

        self.image_access_obj.hard_delete_image_row(img)

    def imagefile_move(self,current_file_path,project_name,new_file_name,ftype):
        destination =  {'unlabeled':self.project_root_dir.unlabeled,
                        'labeled':self.project_root_dir.labeled,
                        'quality_labeled':self.project_root_dir.quality_labeled,
                        'critical':self.project_root_dir.critical}
        
        current_file_name = os.path.basename(current_file_path)
        destination_path1 = os.path.join(self.project_root_dir.project_root_path,str(project_name),'')
        if ftype.lower() in destination:
            sub_dir = destination[ftype.lower()]
            destination_path2 = os.path.join(destination_path1,sub_dir,'')
        elif ftype == '':
            sub_dir = ''
            destination_path2 = destination_path1
        self.project_root_dir.rename_move_file(current_file_path, destination_path2, new_file_name)
        logger.debug(f'New image name: {new_file_name}, original image name: {current_file_name}, file location: {destination_path2}.')

        return destination_path1, sub_dir, new_file_name

    def revert_direction_filepath(self,current_file_path,project_name,new_file_name,ftype):
        destination =  {'unlabeled':self.project_root_dir.unlabeled,
                        'labeled':self.project_root_dir.labeled,
                        'quality_labeled':self.project_root_dir.quality_labeled,
                        'critical':self.project_root_dir.critical}
        
        reverted_file_name = os.path.basename(current_file_path)
        reverted_file_path = os.path.join(self.project_root_dir.project_root_path,str(project_name),ftype,new_file_name)

        parent_dir_level_1 = os.path.split(os.path.split(current_file_path)[0])[1]
        reverted_ftype = ''
        if parent_dir_level_1 in destination:
            reverted_ftype = parent_dir_level_1

        return reverted_file_path,project_name,reverted_file_name,reverted_ftype

    def imagefile_web_url(self, image_dir, subdir, image_uuid, image_ext):
        image_web_url = self.utility.get_web_url(image_dir, subdir, image_uuid, image_ext)
        
        return image_web_url

    def get_image_name_and_path(self,img):
        image_path = os.path.join(img.Dir_Image,img.Image_Id + '.' + img.Ext_Image)
        image_name = img.Image_Id + '.' + img.Ext_Image

        return image_name,image_path

