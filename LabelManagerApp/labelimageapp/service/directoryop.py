# file: directoryop.py
# author: Muhammad Mushfiqur Rahman <mushfiq.rahman@tum.de>
# date: 26-06-2019

from utility.loggingfile import Log

import sys
import os
import uuid
import shutil

logger = Log().logging.getLogger(__name__)



class DirectoryStructure(object):
    def __init__(self, root_path):
        self.dir_name = ""
        self.project_root_path = root_path
        self.labeled = 'Labeled'
        self.unlabeled = 'Unlabeled'
        self.critical = 'Critical'
        self.quality_labeled = 'Quality_Labeled'
        self.current_project_name = ''
        self.current_project_path = ''

    # create a new project directory
    def create_subdirectories(self, project_name):        
        try:
            self.dir_name = project_name
            self.current_project_path = os.path.join(self.project_root_path,self.dir_name)
            folders = self.all_directories_subdirectories()
            folders_str = ', '.join(folders)
            
            cwd = os.getcwd()
            os.chdir(self.current_project_path)
            os.mkdir(self.labeled)
            os.mkdir(self.unlabeled)
            os.mkdir(self.critical)
            os.mkdir(self.quality_labeled)
            os.chdir(cwd)

            logger.debug(f'Project: {project_name}. Created subdirectories: {folders_str}')
            return self.current_project_name
        except:
            logger.error(f'Project: {project_name}. No subdirectories created.', exc_info=True)
            raise

    # rename and move an image file.
    def rename_move_file(self, cur_dir, dest_dir, new_name):
        dest_path = dest_dir + new_name
        if dest_path == cur_dir:
            logger.warning(f'File aready in destination directory: {dest_dir}. File not moved.')
            return None 
        shutil.move(cur_dir, dest_path)
        logger.info(f'File system: 1 record moved successfully.')

        return dest_path

    def get_immediate_subdirectories(self, cur_dir):
        return [name for name in os.listdir(cur_dir) if os.path.isdir(os.path.join(cur_dir, name))]

    def all_directories_subdirectories(self):
        folders = []

        # r=root, d=directories, f = files
        for r, d, f in os.walk(self.current_project_path):
            for folder in d:
                folders.append(os.path.join(r, folder))

        return folders


    
    

    
