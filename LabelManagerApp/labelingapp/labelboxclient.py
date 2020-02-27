# file: labelboxclient.py
# author: name <email>
# date: 05-21-2019
'''
# LabelBoxClient class implement Labelbox class here.
'''
from database.models.image import Image
from database.models.project import Project
from database.models.labelbox_details import Labelbox_Details
from database.models.label import Label
from database.dal.imagedal import ImageDAL
from database.dal.projectdal import ProjectDAL
from database.dal.labelbox_details_dal import Labelbox_Details_DAL
from database.dal.labeldal import LabelDAL
from settings import Configuration_Settings
from labelingapp.labelbox import Labelbox
from labelimageapp.labelimagecontroller import LabelImageController
from utility.signalhandler import PreventShutdown
from utility.loggingfile import Log

import uuid
import os
from operator import itemgetter
import numpy as np 

logger = Log().logging.getLogger(__name__)

# this is a labelingapp's business logic file which imports LabelManagerApp.database package. 
# From this package and module, labelingapp will implement label box functionality by communicating with LabelManagerApp.database.dal module.


class LabelboxClient():
    def __init__(self):
        self.configuration_obj = Configuration_Settings()        
        self.image_list = []
        self.critical_image_list = []
        self.image_access_obj = ImageDAL()
        self.project_access_obj = ProjectDAL()
        self.labelbox_details_access_obj = Labelbox_Details_DAL()
        self.label_access_obj = LabelDAL()
        self.labelbox_details_list = []
        self.project_ids = []
        self.dataset_ids = []
        self.labelbox_api = Labelbox()
        self.uinterface_id = self.labelbox_api.get_uinterfaceid(self.configuration_obj.LABELBOX_UINTERFACE_NAME)
        self.labelImageClientObject = LabelImageController()

    def initiate_labelbox_api(self):
        logger.info('START UPLOADING LABELBOX')
        logger.info('Start uploading images to Labelbox.')
        # Get all upload images.
        upload_image_info_list = []
        
        self.image_list = self.image_access_obj.get_images_for_uploading()
        logger.info(f'Total number of images to upload: {len(self.image_list)}.')

        if len(self.image_list) != 0:
            # Get all rows from Labelbox_Details
            self.labelbox_details_list = self.labelbox_details_access_obj.get_distinct_labelbox_rows()
            count_lbox_list = len(self.labelbox_details_list)
            logger.debug(f'Total number of labelbox projects in table: Labelbox_Details: {count_lbox_list}.')

            if count_lbox_list != 0 :
                for k, _ in enumerate(self.labelbox_details_list):
                    lbox_details = Labelbox_Details()
                    lbox_details = self.labelbox_details_list[k]
                    self.project_ids.append(lbox_details.Project_Id)
                    self.dataset_ids.append(lbox_details.Dataset_Id)
            project_ids_str = ', '.join(str(x) for x in self.project_ids)
            logger.debug(f'Current project ids in table Labelbox_Details: {project_ids_str}.')

            # Iterate over all the image record and collect the web_url for uploading images
            for key, _ in enumerate(self.image_list):
                img = Image()
                img = self.image_list[key]
                record = []
                record.append(img.Image_Id)
                record.append(img.Project_Id)
                record.append(img.Web_Url)
                upload_image_info_list.append(record)
                logger.debug(f'Project id of processing image: {img.Project_Id}.')

                # initiate Labelbox api functionality
                if img.Project_Id not in self.project_ids:
                    logger.info('Start creating new Labelbox project and dataset.')
                    self.project_ids.append(img.Project_Id)

                    project_name = self.project_access_obj.get_project_name(img.Project_Id)

                    # create a labelbox project
                    labelbox_project_id = self.labelbox_api.add_project(project_name)
                    logger.info(f'New Labelbox project created with Labelbox with project name: {project_name}, project id: {labelbox_project_id}.')

                    # create a labelbox dataset for created project
                    labelbox_dataset_name = project_name + '_dataset'
                    labelbox_dataset_id = self.labelbox_api.add_dataset(project_name + '_dataset')
                    logger.info(f'New Labelbox dataset created with Labelbox with dataset name: {labelbox_dataset_name}, dataset id: {labelbox_dataset_id}.')


                    self.labelbox_api.update_uinterface(self.configuration_obj.LABELBOX_UINTERFACE_LINK)

                    # Linking labelbox_dataset and labelbox_uinterface to labelbox_project by adding.
                    self.labelbox_api.link2project(labelbox_project_id, labelbox_dataset_id, 'add', obj='dataset')
                    logger.info(f'Created dataset linked to created project successfully.')
                    self.labelbox_api.link2project(labelbox_project_id, self.uinterface_id, 'add', obj='uinterface')
                    logger.info(f'User interface linked to created project successfully.')

                    self.labelbox_details_insert(labelbox_dataset_id, img.Project_Id, labelbox_project_id, labelbox_dataset_name, 
                        self.uinterface_id, self.configuration_obj.LABELBOX_UINTERFACE_NAME)

            sorted_upload_image_info_list = sorted(upload_image_info_list, key=itemgetter(1))
            unique_project_ids = [] 
            for i, _ in enumerate(sorted_upload_image_info_list):
                row = sorted_upload_image_info_list[i]
                if row[1] not in unique_project_ids:
                    unique_project_ids.append(row[1])

            n_images_uploadend = 0
            for x in range(len(unique_project_ids)):
                upload_data_for_specific_project = []
                logger.info(f'Processing current project id: {unique_project_ids[x]}.')
                for i, _ in enumerate(sorted_upload_image_info_list):
                    row = sorted_upload_image_info_list[i]
                    if row[1] == unique_project_ids[x]:
                        new_dict = {
                            'imageUrl': row[2],
                            'externalId': row[0]
                            }
                        upload_data_for_specific_project.append(new_dict)

                # Get dataset id from Labelbox_Details table
                datasetid = self.labelbox_details_access_obj.get_dataset_id(unique_project_ids[x])
                if datasetid is not None:
                    self.labelbox_api.add_data(datasetid, imgfiles=upload_data_for_specific_project)
                    logger.info('Data uploaded successfully.')

                    # Images are uploaded to labelbox_dataset. Now update the Labeling_Running of Image_Details entity.
                    logger.info('Updating image status: Labeling_Running: True.')
                    for obj in upload_data_for_specific_project:
                        img_uuid = obj['externalId']
                        # Iterate over all the image record and update Labeling_Running property.
                        for key, _ in enumerate(self.image_list):
                            img = Image()
                            img = self.image_list[key]
                            if img_uuid == img.Image_Id:
                                img.Labeling_Running = True
                                self.image_access_obj.update_image_row(img)
                                n_images_uploadend +=1
        else:
            n_images_uploadend = 0
        
        logger.info(f'End uploading images to Labelox. Total number of uploaded images: {n_images_uploadend}.')
        logger.info('END UPLOADING LABELBOX')
        
    def labelbox_details_insert(self, datasetid, pid, lb_pid, datasetname, uid, uname):
        lb_details = Labelbox_Details()
        lb_details.Dataset_Id = datasetid
        lb_details.Project_Id = pid
        lb_details.LB_Project_Id = lb_pid
        lb_details.Dataset_Name = datasetname
        lb_details.UInterface_ID = uid
        lb_details.UInterface_Name = uname
        self.labelbox_details_access_obj.insert_labelbox_row(lb_details)

    def labelbox_details_delete_project(self, pid, pname):
        logger.info('START DELETING PROJECT')
        logger.info('Start deleting project with dataset in Labelbox.')
        lb_details = Labelbox_Details() 

        try:
            logger.info('Start deleting...')
            logger.debug(f'Current project id: {pid}.')
            if pid == '':
                logger.info(f'Current project name: {pname}.')
                pid = self.project_access_obj.get_project_id(pname)
            if pid is not None:
                logger.info(f'Current project id: {pid}.')
                lb_details.Project_Id = pid
                self.delete_labelbox_api_project_dataset(lb_details)
                logger.info('Deleting project with dataset done.')
            else:
                logger.error(f'No valid project id found. Project id : {pid}', exc_info=True)
                raise
            
            # Get all the images by using pid
            all_images = self.image_access_obj.get_images_by_projectid(pid)
            if len(all_images) != 0:
                logger.info('Start updating all according images from table Image_Details.')
                for key, _ in enumerate(all_images):
                    img = Image()
                    img = all_images[key]
                    img.Labeling_Running = False
                    self.image_access_obj.update_image_row(img)
                logger.info('Updating Image_Details done.')
        except:
            logger.warning('Deleting failed.')
        
        logger.info('End deleting project with dataset in Labelbox.')
        logger.info('END DELETING PROJECT')

    def delete_labelbox_api_project_dataset(self, lb_det_obj = Labelbox_Details()):
        logger.info('Deleting project with dataset from Labelbox.')
        # get labelbox_details api information for a project from labelbox_details table
        lbl_details_obj = self.labelbox_details_access_obj.get_labelbox_rows_by_project_id(lb_det_obj.Project_Id)
        logger.info(f'lbl_details_obj: {lbl_details_obj}.')

        if lbl_details_obj is not None:
            lb_pid = lbl_details_obj.LB_Project_Id
            lb_did = lbl_details_obj.Dataset_Id
            logger.info(f'lbl_details_obj: {lbl_details_obj.LB_Project_Id}.')
            # hard delete project from labelbox_details table
            self.labelbox_details_access_obj.hard_delete_labelbox_details_row_by_projectId(lb_det_obj)

            self.labelbox_api.del_dataset(lb_did)
            logger.info('Dataset deleted successfully.')
            self.labelbox_api.del_project(lb_pid)
            logger.info('Project deleted successfully.')
        else: 
            logger.error('Invalid project id.', exc_info=True)
            raise


    def transfer_images(self):
        logger.info('START DOWNLOADING LABELS')
        logger.info('Start downloading labels form Labelbox.')
        lb_project_id_list = self.labelbox_details_access_obj.get_all_LB_projects_id()
        
        if lb_project_id_list:
            for lb_project_id in lb_project_id_list:
                project_name = self.labelbox_details_access_obj.get_project_name(lb_project_id)
                logger.info(f'Current project: {project_name}. Labelbox project id: {lb_project_id}.')
                
                # export labels form Labelbox
                try:
                    labels = self.labelbox_api.export_labels(lb_project_id, del_labels=False, del_datarows=False)
                    logger.info(f'Number of labels downloaded: {len(labels)}.')
                except:
                    logger.info(f'Number of labels downloaded: 0.')
                    continue

                for label in labels:
                    img_uuid = uuid.UUID(label['External ID']).hex
                    datarow_id = label['DataRow ID']
                    label_info = label['Label']

                    # db entry & move files
                    img = self.image_access_obj.get_image_by_uuid(img_uuid)
                    new_file_name,current_file_path = self.labelImageClientObject.get_image_name_and_path(img)
                    logger.info(f'Image: {new_file_name} : Start processing.')

                    if label_info != 'Skip':
                        # ------------------------------------> MISSING: Download and convert mask into rle format
                        with PreventShutdown() as ps:
                            img.Labeled += 1
                            img.Critical = 0
                            ## updating img.project_id if the project has a parent
                            parent_project_id = self.project_access_obj.get_parent_project_id(img.Project_Id) 
                            
                            if parent_project_id is None:
                                logger.info(f'There is no child (critical) project of parent project id: {img.Project_Id}')
                            else:
                                logger.info(f'Critical (child) project id: {img.Project_Id}, parent project id: {parent_project_id}') 
                                img.Project_Id = parent_project_id 
                            
                            img.Labeling_Running = False
                            #img.Dir_Image = os.path.join(image_path,sub_dir,'')
                            #img.Web_Url = image_url
                            self.labelImageClientObject.dbmodify_and_move_image(img, destination='labeled', option='update')

                            lbl = Label()
                            lbl.Image_Id = img.Image_Id
                            lbl.Is_Deleted = False
                            lbl.Label_Details = label_info
                            label_id = self.label_access_obj.insert_label_row(lbl)

                        logger.info(f'Image: {new_file_name} : Label added successfully. Inserted in database with label id: {label_id}.')

                    elif label_info == 'Skip': 
                        image_path,sub_dir,_ = self.labelImageClientObject.imagefile_move(current_file_path,project_name,new_file_name,'critical')
                        image_url = self.labelImageClientObject.imagefile_web_url(image_path, sub_dir, img.Image_Id, img.Ext_Image)

                        img.Critical += 1
                        img.Labeling_Running = False
                        img.Dir_Image = os.path.join(image_path,sub_dir,'')
                        img.Web_Url = image_url
                        self.image_access_obj.update_image_row(img)
                        
                        logger.info(f'Image: {new_file_name} : Image marked as critical.')

                    # labelbox delete
                    self.labelbox_api.del_labels([label_id])
                    self.labelbox_api.del_datarows([datarow_id])
                    logger.info('Label and Datarow removed from Labelbox successfully')

            # Create project for critical lable where Threshold is 

        logger.info('End downloading labels form Labelbox')
        logger.info('END DOWNLOADING LABELS')

    def create_and_update_project_for_critical_images(self):
        logger.info('START CREATING PROJECT FOR CRITICAL LABELED IMAGES')
        logger.info('GET ALL THE THRESHOLD CRITICAL IMAGES')
        self.critical_image_list = self.image_access_obj.get_images_by_threshold_critical_value(self.configuration_obj.CRITICAL_THRESHOLD)
        logger.info(f'Total number of threshold critical images: {len(self.critical_image_list)}.')
        #logger.info(f'Total number of threshold critical images: {self.critical_image_list}.')

        #critical_project_ids_from_image_details = []
        record = []
        # Iterate over all the image record and collect the project ids
        for key, _ in enumerate(self.critical_image_list):
            img = Image()
            img = self.critical_image_list[key]
            record.append(img.Project_Id)
        
        logger.debug(f'Project ids of critical images from image details table: {record}.')

        unique_ids = np.unique(record)
        unique_project_ids = unique_ids.tolist()
        logger.debug(f'Unique project ids of critical images from image details table: {unique_project_ids}.')

        critical_project_list = []
        critical_project_list = self.project_access_obj.get_all_critical_projects_ids()
        logger.info(f'Total number of critical projects: {len(critical_project_list)}.')
        logger.info(f'Total number of critical projects array: {critical_project_list}.')

        for _, item in enumerate(unique_project_ids):
            if item not in critical_project_list:
                #logger.info(f'New project id: {item}')
                project_name = self.project_access_obj.get_project_name(item)
                #logger.info(f'New project name: {project_name}')
                critical_project_name = project_name + '_critical'
                new_project_id = self.insert_critical_project_info(item, critical_project_name)

                logger.info(f'Created new critical (child) project id: {new_project_id}, parent project id: {item}') 

                for key, _ in enumerate(self.critical_image_list):
                    img = Image()
                    img = self.critical_image_list[key]
                    if item == img.Project_Id:
                        img.Project_Id = new_project_id
                        self.image_access_obj.update_image_row(img)
                    logger.info('Updating the image details table with new critical project id for the threshold critical image: {new_project_id}')
            else:
                critical_project_id = self.project_access_obj.get_critical_project_id(item)

                logger.info(f'Updating critical (child) project id: {critical_project_id}, parent project id: {item}') 

                for key, _ in enumerate(self.critical_image_list):
                    img = Image()
                    img = self.critical_image_list[key]
                    if item == img.Project_Id:
                        img.Project_Id = critical_project_id
                        self.image_access_obj.update_image_row(img)
                    logger.info('Updating the image details table with existing critical project id for the threshold critical image: {new_project_id}')


    
    def insert_critical_project_info(self, project_id, project_name):
        projectObject = Project()
        projectObject.Project_Name = project_name
        projectObject.Parent_Project_Id = project_id
        project_id = self.project_access_obj.insert_project(projectObject)
        return project_id

    def critical_threshold_labeling_handler(self):
        logger.info('START HANDLING CRITICAL LABELED IMAGES')
        self.create_and_update_project_for_critical_images()

        logger.info('START UPLOADING CRITICAL IMAGES TO LABELBOX.')
        # Get all upload critical images.
        upload_image_info_list = []

        self.critical_image_list = self.image_access_obj.get_images_by_threshold_critical_value(self.configuration_obj.CRITICAL_THRESHOLD)
        logger.info(f'Total number of threshold critical images: {len(self.critical_image_list)}.')

        if len(self.critical_image_list) != 0:
            # Get all rows from Labelbox_Details
            self.labelbox_details_list = self.labelbox_details_access_obj.get_distinct_labelbox_rows()
            count_lbox_list = len(self.labelbox_details_list)
            logger.debug(f'Total number of labelbox projects in table: Labelbox_Details: {count_lbox_list}.')

            if count_lbox_list != 0 :
                for k, _ in enumerate(self.labelbox_details_list):
                    lbox_details = Labelbox_Details()
                    lbox_details = self.labelbox_details_list[k]
                    self.project_ids.append(lbox_details.Project_Id)
                    self.dataset_ids.append(lbox_details.Dataset_Id)
            project_ids_str = ', '.join(str(x) for x in self.project_ids)
            logger.debug(f'Current project ids in table Labelbox_Details: {project_ids_str}.')

            # Iterate over all the image record and collect the web_url for uploading images
            for key, _ in enumerate(self.critical_image_list):
                img = Image()
                img = self.critical_image_list[key]
                record = []
                record.append(img.Image_Id)
                record.append(img.Project_Id)
                record.append(img.Web_Url)
                upload_image_info_list.append(record)
                logger.debug(f'Project id of porcessing image: {img.Project_Id}.')

                critical_project_name = self.project_access_obj.get_project_name(img.Project_Id)

                # initiate Labelbox api functionality
                if img.Project_Id not in self.project_ids:
                    logger.info('Start creating new Labelbox project and dataset.')
                    self.project_ids.append(img.Project_Id)

                    # create a labelbox project
                    labelbox_project_id = self.labelbox_api.add_project(critical_project_name)
                    logger.info(f'New Labelbox project created with Labelbox with project name: {critical_project_name}, project id: {labelbox_project_id}.')

                    # create a labelbox dataset for created project
                    labelbox_dataset_name = critical_project_name + '_dataset'
                    labelbox_dataset_id = self.labelbox_api.add_dataset(critical_project_name + '_dataset')
                    logger.info(f'New Labelbox dataset created with Labelbox with dataset name: {labelbox_dataset_name}, dataset id: {labelbox_dataset_id}.')


                    self.labelbox_api.update_uinterface(self.configuration_obj.LABELBOX_UINTERFACE_LINK)

                    # Linking labelbox_dataset and labelbox_uinterface to labelbox_project by adding.
                    self.labelbox_api.link2project(labelbox_project_id, labelbox_dataset_id, 'add', obj='dataset')
                    logger.info(f'Created dataset linked to created project successfully.')
                    self.labelbox_api.link2project(labelbox_project_id, self.uinterface_id, 'add', obj='uinterface')
                    logger.info(f'User interface linked to created project successfully.')

                    self.labelbox_details_insert(labelbox_dataset_id, img.Project_Id, labelbox_project_id, labelbox_dataset_name, 
                        self.uinterface_id, self.configuration_obj.LABELBOX_UINTERFACE_NAME)

            sorted_upload_image_info_list = sorted(upload_image_info_list, key=itemgetter(1))
            unique_project_ids = [] 
            for i, _ in enumerate(sorted_upload_image_info_list):
                row = sorted_upload_image_info_list[i]
                if row[1] not in unique_project_ids:
                    unique_project_ids.append(row[1])

            n_images_uploadend = 0
            for x in range(len(unique_project_ids)):
                upload_data_for_specific_project = []
                logger.info(f'Processing current project id: {unique_project_ids[x]}.')
                for i, _ in enumerate(sorted_upload_image_info_list):
                    row = sorted_upload_image_info_list[i]
                    if row[1] == unique_project_ids[x]:
                        new_dict = {
                            'imageUrl': row[2],
                            'externalId': row[0]
                            }
                        upload_data_for_specific_project.append(new_dict)

                # Get dataset id from Labelbox_Details table
                datasetid = self.labelbox_details_access_obj.get_dataset_id(unique_project_ids[x])
                if datasetid is not None:
                    self.labelbox_api.add_data(datasetid, imgfiles=upload_data_for_specific_project)
                    logger.info('Data uploaded successfully.')

                    # Images are uploaded to labelbox_dataset. Now update the Labeling_Running of Image_Details entity.
                    logger.info('Updating image status: Labeling_Running: True.')
                    for obj in upload_data_for_specific_project:
                        img_uuid = obj['externalId']
                        # Iterate over all the image record and update Labeling_Running property.
                        for key, _ in enumerate(self.critical_image_list):
                            img = Image()
                            img = self.critical_image_list[key]
                            if img_uuid == img.Image_Id:
                                img.Labeling_Running = True
                                self.image_access_obj.update_image_row(img)
                                n_images_uploadend +=1
        else:
            n_images_uploadend = 0
            
        
        logger.info(f'End uploading critical images to Labelox. Total number of uploaded critical images: {n_images_uploadend}.')
        logger.info('END UPLOADING LABELBOX')
        
