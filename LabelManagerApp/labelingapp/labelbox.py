# file: labelbox.py
# author: name <email>
# date: 05-21-2019
'''
# Labelbox class implements GraphQLClient api methods.
'''

import json
import datetime
import time
import urllib.request
from urllib.error import HTTPError
import requests
from graphqlclient import GraphQLClient
from settings import Configuration_Settings
from utility.loggingfile import Log

logger = Log().logging.getLogger(__name__)


class Labelbox():
    '''
    The Labelbox object connects and interacts with Labelbox(c).


    Attributes:
        __tmp
        __labelbox_graphql
        __apikey

    Methods (public):
        add_dataset
        del_dataset
        add_data
        del_datarows
        link2project
        add_project
        del_project
        add_uinterface
        update_uinterface
        get_projectname
        get_projectid
        get_datasetname
        get_datasetid
        get_uinterfacename
        get_uinterfaceid
        export_labels
        del_labels

    Methods (private):
        __read_apikey
        __connect
        __execute_graphql
        __upload_data_bulk
        __upload_data_row
        __get_projectsinfo
        __get_datasetinfo
        __get_uinterfaceinfo

    ToDo:
        * Bulk data upload needs a server file upload (json file via https)

    '''

    __slots__ = ('__tmp', '__labelbox_graphql', '__apikey', 'configuration_obj', '__labelbox_name')

    def __init__(self) -> None:
        self.__labelbox_name = 'Labelbox API'
        self.configuration_obj = Configuration_Settings() 
        self.__tmp = ''
        self.__labelbox_graphql = r'https://api.labelbox.com/graphql'
        self.__read_apikey()

    def __read_apikey(self) -> None:
        '''
        READ API Key from settings.py file.
        Returns:
            None

        '''
        self.__apikey = self.configuration_obj.LABELBOX_API_KEY

    def __connect(self) -> GraphQLClient:
        '''
        Connect to Labelbox using GraphQLClient.

        Returns:
            client (GraphQLClient): GraphQL client to Labelbox

        '''
        logger.info(f'{self.__labelbox_name}: Trying to connect...')
        labelbox_graphql = self.__labelbox_graphql
        api_key = self.__apikey

        client = GraphQLClient(labelbox_graphql)
        client.inject_token('Bearer ' + api_key)        

        return client

    def __execute_graphql(self, query: str, **kwargs) -> dict:
        '''
        Build and run GraphQL query or mutation with variables

        Args:
            query (str): GraphQL query with variables like '$<name>'

        Kwargs:
            variables (dict): Variables with dictionary key: '$<name>' name of
            variable in GraphQL query and dictionary value: <name> the python
            variable.
            $name  -> "name"
            $$name -> name
            **kwargs = {'variables':{'$name':'value'}}

        Returns:
            res(dict): GraphQL answer

        '''
        try:
            for key in kwargs['variables']:
                # '$'
                symbol = '"'
                # '$$'
                if key[1] == '$':
                    symbol = ''
                if isinstance(kwargs['variables'][key], list):
                    kwargs['variables'][key] = '["' + '","'.join(
                        kwargs['variables'][key]) + '"]'
                    symbol = ''
                query = query.replace(
                    key, symbol + kwargs['variables'][key] + symbol)
        except KeyError:
            pass

        num = 0
        while True:
            try:
                num += 1
                logger.info(f'{self.__labelbox_name}: Initializing connection.')
                client = self.__connect()
                res_str = client.execute(query)
                logger.info(f'{self.__labelbox_name}: Connection established.')
                break
            except HTTPError:
                if num <= 10:
                    logger.warning(f'{self.__labelbox_name}: Could not connect to Labelbox API. Reconnecting...')
                    time.sleep(5)
                    continue
                else:
                    logger.error(f'{self.__labelbox_name}: Could not connect to Labelbox API finally. Terminate trial.')
                    raise HTTPError

        res = json.loads(res_str)

        return res

    def add_dataset(self, name: str) -> str:
        '''
        Add a new dataset to Labelbox(c). Same name than an existing dataset
        results in the creating of a new dataset with different dataset Id.

        Args:
            name (str): name of the dataset to create

        Returns:
            datasetid (str): Id of the created dataset

        '''

        datasets = self.__get_datasetinfo()
        datasetnames_existing = [dataset['name'] for dataset in datasets]

        #name = extend_name(datasetnames_existing, name)        
        name = self.extendName(datasetnames_existing, name)

        res = self.__execute_graphql("""
        mutation{
          createDataset(data:{
            name: $name
          }){
            id
          }
        }
        """,
                                     variables={'$name': name})

        datasetid = res['data']['createDataset']['id']

        logger.info(f'{self.__labelbox_name}: Dataset created. Name: {name}, id: {datasetid}.')

        return datasetid

    def del_dataset(self, datasetid: str) -> None:
        '''
        Delete a Labelbox dataset with dataset Id.

        Args:
            datasetid (str): Id of the dataset

        Returns:
            None

        '''

        # look up name of dataset
        res = self.__execute_graphql('''
        query{
        dataset(where:{id:$id}){
        name
        }
        }
        ''',
                                     variables={'$id': datasetid})
        name = res['data']['dataset']['name']

        # delete dataset
        self.__execute_graphql('''
        mutation{
        deleteDataset(data:{
            id: $id
            }){id}
        }
        ''',
                               variables={'$id': datasetid})

        logger.info(f'{self.__labelbox_name}: Dataset deleted. Name: {name}, dataset id: {datasetid}.')

    def add_data(self, datasetid: str, **kwargs) -> None:
        '''
        Add Data to an existing dataset. Using row-by-row import. Bulk import
        needs server file upload.Input: <imgfiles> or <json_path> required.

        Args:
            datasetid (str): Id of the dataset


        Keyword Args:
            json_path (str): path to json file containing files
            imgfiles (list): list of dictionaries containing <image_url> of
            file
            and <externalid> of file

        '''
        try:
            if 'imgfiles' in kwargs:
                files = kwargs['imgfiles']
            elif 'json_path' in kwargs:
                with open(kwargs['json_path'], 'r') as file:
                    files = json.load(file)

            for file in files:
                file_imageurl = file['imageUrl']  # type: ignore
                file_externalid = file['externalId']  # type: ignore
                self.__upload_data_row(datasetid, file_imageurl,
                                       file_externalid)

        except Exception as fileexist:
            logger.error(f'{self.__labelbox_name}: Json file for adding data neither existing nor built.', exc_info=True)
            raise

        logger.info(f'{self.__labelbox_name}: Data added. Dataset id: {datasetid}.')

    def __upload_data_bulk(self, datasetid: str, json_path: str) -> str:
        '''
        Bulk upload data to Labelbox. Not in use!


        Args:
            datasetid (str): Id of the dataset
            json_path (str): path to json file containing files

        Returns:
            bulk_accepted (bool)

        '''
        upload_bulk = False

        if not upload_bulk:
            raise Exception(
                'Bulk upload uses external upload server. '
                + 'Consider using Row-by-Row upload or resolve problem!')
        if upload_bulk:
            # using file.io upload
            with open(json_path, 'r') as file:
                filedata = json.load(file)

            data = str.encode(json.dumps(filedata))
            files = {'file': data}
            reply = requests.post("https://file.io/?expires=1d", files=files)
            file_info = json.loads(reply.text)
            json_url = file_info['link']

            res = self.__execute_graphql("""
              mutation {
                appendRowsToDataset(
                  data:{
                    datasetId: $datasetid,
                    jsonFileUrl: $jsonFileUrl
                  }
                ){
                  accepted
                }
              }
            """,
                                         variables={
                                             '$datasetid': datasetid,
                                             '$jsonFileUrl': json_url
                                         })

            bulk_accepted = res['data']['appendRowsToDataset']['accepted']

        return bulk_accepted

    def __upload_data_row(self, datasetid: str, image_url: str,
                          externalid: str) -> str:
        '''
        Row-by-row upload data to Labelbox.

        Args:
            datasetid (str): Id of the dataset
            image_url (str): URL of image file
            externalid (str): external Id of image file

        Returns:
            datarowid (str): Id of data row uploaded

        '''

        res = self.__execute_graphql("""
        mutation {
        createDataRow(
            data: {
            rowData: $image_url,
            externalId: $external_id,
            dataset: {
            connect: {
            id: $dataset_id
            }
            },
            }
            ) {
            id
            }
            }
            """,
                                     variables={
                                         '$dataset_id': datasetid,
                                         '$image_url': image_url,
                                         '$external_id': externalid
                                     })

        datarowid = res['data']['createDataRow']['id']

        return datarowid

    def del_datarows(self, datarowids: list) -> bool:
        '''
        Delete datarows with datarow Ids from dataset.


        Args:
            datarowids (list): data row id list

        Returns:
            status_deleted (bool)

        '''
        status_deleted = True
        try:
            res = self.__execute_graphql("""
              mutation {
                deleteDataRows(where:{
                  dataRowIds: $datarowIds
                }){
                  id
                  deleted
                }
              }
            """,
                                         variables={'$datarowIds': datarowids})
            deleted = [
                datarow['deleted'] for datarow in res['data']['deleteDataRows']
            ]
            if 'False' in deleted:
                status_deleted = False
        except TypeError:
            status_deleted = False

        logger.info(f'{self.__labelbox_name}: Delete data rows. Status: {status_deleted}.')

        return status_deleted

    def add_project(self,
                    projectname: str) -> str:
        '''
        Add project to Labelbox(c).


        Args:
            projectname (str): name of the project

        Returns:
            projectid (str): id of project  

        '''
        projects_existing = self.__get_projectsinfo()
        projectnames_existing = [
            project['name'] for project in projects_existing
        ]

        projectname = self.extendName(projectnames_existing, projectname)

        today = datetime.date.today()
        projectdescription = 'Created automatically on ' + today.strftime('%d-%b-%Y') + '.'

        res = self.__execute_graphql('''
          mutation{
            createProject(data:
            {
                name:$name,
                description:$description
            }
            )
            {
                id
            }
          }
        ''',
                                     variables={
                                         '$name': projectname,
                                         '$description': projectdescription
                                     })
        projectid = res['data']['createProject']['id']

        logger.info(f'{self.__labelbox_name}: Project created. Project id: {projectid}.')

        now = datetime.datetime.now()
        setup_date_time = now.isoformat()
        self.__execute_graphql('''
        mutation{
        updateProject(
        where:
            {
            id:$projectid
            },
        data:
            {
            setupComplete:$setupdatetime
            }
        )
            {
            setupComplete
            }
        }
        ''',
                               variables={
                                   '$projectid': projectid,
                                   '$setupdatetime': setup_date_time
                               })


        return projectid


    def del_project(self, projectid: str) -> None:
        '''
        Delete a Labelbox project with project Id.

        Args:
            projectid (str): Id of the project

        Returns:
            None

        '''

        # look up name of dataset
        res = self.__execute_graphql('''
        query{
        project(where:{id:$id}){
        name
        }
        }
        ''',
                                     variables={'$id': projectid})
        name = res['data']['project']['name']

        # delete dataset
        self.__execute_graphql('''
        mutation{
        updateProject(where:{id:$id},data:{deleted:true})
        {
        id,name,deleted
        }
        }
        ''',
                               variables={'$id': projectid})

        logger.info(f'{self.__labelbox_name}: Project deleted. Name: {name}, project id: {projectid}.')


    def __get_projectsinfo(self) -> list:
        '''
        Get details of all projects.


        Returns:
            projects (list): list of dictionaries containing infos of each
            projects

        '''

        res = self.__execute_graphql('''
          query{
            projects(where:{deleted_not:true}){
              name,id,labelingFrontend{id},datasets {
                id,name
              },
              setupComplete
            }
          }
        ''')
        projects = res['data']['projects']

        return projects

    def __get_datasetinfo(self) -> list:
        '''
        Get details of all existing datasets.


        Returns:
            datasets (list): list of dictionaries containing infos of
            each dataset (not deleted)

        '''
        res = self.__execute_graphql('''
                  query{
          datasets(where:{deleted_not:true}){
            name,id,deleted
          }
        }
        ''')
        datasets = res['data']['datasets']

        return datasets

    def link2project(self,
                     projectid: str,
                     objectid: str,
                     add_or_remove: str = 'add',
                     **kwargs) -> bool:
        '''
        Add or remove dataset or user interface to project.


        Args:
            projectid (str)
            objectid (str)
            add_or_remove (str): add <add> oder remove <rem> a dataset from a
            project

        Kwargs:
            obj: 'dataset','uinterface'

        Returns:
            setup_complete (bool): status if project is setup completely

        '''
        add_rem = {'add': 'connect', 'rem': 'disconnect'}
        obj = {'dataset': 'datasets', 'uinterface': 'labelingFrontend'}

        res = self.__execute_graphql('''
        mutation{
          updateProject(
            where:{
            id: $projectid
            },
            data:
            {
            $$obj:
                {
                $$addrem:
                    {
                    id: $objectid
                    }
                }
            }
            ){
            setupComplete
            }
        }
        ''',
                                     variables={
                                         '$projectid': projectid,
                                         '$objectid': objectid,
                                         '$$addrem': add_rem[add_or_remove],
                                         '$$obj': obj[kwargs['obj']]
                                     })

        setup_complete_value = res['data']['updateProject']['setupComplete']

        logger.info(f'{self.__labelbox_name}: {kwargs["obj"]} linked to project ({add_or_remove}). Project id: {projectid}, {kwargs["obj"]} Id: {objectid}.')

        if setup_complete_value is None:
            setup_complete = False
        else:
            setup_complete = True

        return setup_complete

    def add_uinterface(self,
                       uinterfacename: str,
                       uinterfaceurl: str,
                       uinterfacedescription: str = 'Created Automatically'
                       ) -> str:
        '''
        Add custom Labeling Interface to Labelbox(c).


        Args:
            uinterfacename (str): name of labeling user interface
            uinterfaceurl (str): url of labeling user interface
            uinterfacedescription (str): description of labeling user interface

        Returns:
            uinterfaceid (str): labeling user interface Id

        '''
        create_new_interface = False

        if not create_new_interface:
            raise Exception('New user interfaces cannot be deleted. '
                            + 'Consider updating an existing one!')
        if create_new_interface:
            res = self.__execute_graphql('''
            mutation{
                createLabelingFrontend(data:
                {
                    name:$name,
                    description:$description,
                    iframeUrlPath:$iframeUrlPath
                }
                )
                {
                    id
                }
            }
            ''',
                                         variables={
                                             '$name': uinterfacename,
                                             '$description':
                                             uinterfacedescription,
                                             '$iframeUrlPath': uinterfaceurl
                                         })
            uinterfaceid = res['data']['createLabelingFrontend']['id']

        return uinterfaceid

    def __get_uinterfaceinfo(self) -> list:
        '''
        Get details of all existing labeling user interfaces.


        Returns:
            uinterfaces (list): list of dictionaries containing infos
            of each user interface (not deleted)

        '''
        res = self.__execute_graphql('''
                  query{
          labelingFrontends(where:{deleted_not:true}){
            name,id,deleted
          }
        }
        ''')
        uinterfaces = res['data']['labelingFrontends']

        return uinterfaces

    def update_uinterface(self,
                          uinterfaceurl: str,
                          uinterfaceid: str = "cjufm6cfppyc1075549l39t9o"
                          ) -> str:
        '''
        Update url of labeling user interface.


        Args:
            uinterfaceurl (str): user interface url
            uinterfaceid (str): user interface id


        '''
        res = self.__execute_graphql('''
        mutation{
        updateLabelingFrontend(
        where:
        {
            id:$uinterfaceid
        },
        data:
        {
            iframeUrlPath: $uinterfaceurl
        }
        )
        {
            id
        }
        }
        ''',
                                     variables={
                                         '$uinterfaceid': uinterfaceid,
                                         '$uinterfaceurl': uinterfaceurl
                                     })
        uinterfaceid = res['data']['updateLabelingFrontend']['id']

        return uinterfaceid

    def get_projectname(self, projectid: str) -> str:
        '''
        Get name of project from project Id:

        Args:
            projectid (str): id of project

        Returns:
            projectname (str): name of the project

        '''
        res = self.__execute_graphql('''
          query{
            projects(where:{
            deleted_not:true,
            id:$projectid
            }){
              name
            }
          }
        ''',
                                     variables={'$projectid': projectid})
        projectname = res['data']['projects'][0]['name']

        return projectname

    def get_projectid(self, projectname: str) -> str:
        '''
        Get Id of project form project name.


        Args:
            projectname (str): name of the project

        Returns:
            projectid (str): id of project

        '''
        res = self.__execute_graphql('''
          query{
            projects(where:{
            deleted_not:true,
            name:$projectname
            }){
              id
            }
          }
        ''',
                                     variables={'$projectname': projectname})
        projectid = res['data']['projects'][0]['id']

        return projectid

    def get_datasetname(self, datasetid: str) -> str:
        '''
        Get name of dataset from dataset Id:


        Args:
            datasetid (str): id of dataset

        Returns:
            datasetname (str): name of the dataset

        '''
        res = self.__execute_graphql('''
                  query{
          datasets(where:{
          deleted_not:true,
          id:$datasetid
          }){
            name
          }
        }
        ''',
                                     variables={'$datasetid': datasetid})
        datasetname = res['data']['datasets'][0]['name']

        return datasetname

    def get_datasetid(self, datasetname: str) -> str:
        '''
        Get Id of dataset form dataset name.


        Args:
            datasetname (str): name of the dataset

        Returns:
            datasetid (str): id of dataset

        '''
        res = self.__execute_graphql('''
                  query{
          datasets(where:{
          deleted_not:true,
          name:$datasetname
          }){
            id
          }
        }
        ''',
                                     variables={'$datasetname': datasetname})
        datasetid = res['data']['datasets'][0]['id']

        return datasetid

    def get_uinterfacename(self, uinterfaceid: str) -> str:
        '''
        Get name of labeling user interface id.


        Args:
            uinterfaceid (str): id of user interface

        Returns:
            uinterfacename (str): name of the user interface

        '''
        res = self.__execute_graphql('''
                  query{
          labelingFrontends(where:{
          deleted_not:true,
          id:$uinterfaceid
          }){
            name
          }
        }
        ''',
                                     variables={'$uinterfaceid': uinterfaceid})
        uinterfacename = res['data']['labelingFrontends'][0]['name']

        return uinterfacename

    def get_uinterfaceid(self, uinterfacename: str) -> str:
        '''
        Get id of labeling user interface name.


        Args:
            uinterfacename (str): name of the user interface

        Returns:
            uinterfaceid (str): id of user interface

        '''
        res = self.__execute_graphql(
            '''
                  query{
          labelingFrontends(where:{
          deleted_not:true,
          name:$uinterfacename
          }){
            id
          }
        }
        ''',
            variables={'$uinterfacename': uinterfacename})
        uinterfaceid = res['data']['labelingFrontends'][0]['id']

        return uinterfaceid

    def export_labels(self,
                      projectid: str,
                      flag_download: bool = False,
                      del_labels: bool = False,
                      del_datarows: bool = False,
                      **kwargs) -> dict:
        '''
        Export labels from Labelbox. Optional write to json file.
        New link is created only every 30 mins (Labelbox restriction).

        Args:
            projectid (str): id of project
            flag_download (bool)
            del_labels (bool): (<False>),<True>: delete labels after exporting
            labels
            del_datarows (bool): (<False>),<True>: delete data rows after
            exporting labels

        Kwargs:
            'writefile': {'folder':<foldername>,'name':<filename>}: write
            labels to a json file with specified file location

        Returns:
            labels (dict): labels
            path (str): path to json label file (optional)
            label_ids (list): ids of labels
            datarowIds (list): ids of data rows

        '''

        res = self.__execute_graphql('''
        mutation {
        exportLabels(
        data:
            {
            projectId: $projectid
            }
        )
            {
            downloadUrl,
            createdAt,
            shouldPoll,
            }
        }
        ''',variables={'$projectid': projectid})

        export_job = res['data']['exportLabels']

        while True:
            if export_job['shouldPoll']:
                flag_download = True
                logger.info(f'{self.__labelbox_name}: Export url of labels generating...')
                time.sleep(3)
                return self.export_labels(projectid,flag_download, del_labels, del_datarows,
                                          **kwargs)
            break

        if flag_download:
            with urllib.request.urlopen(export_job['downloadUrl']) as url:
                labels = json.loads(url.read().decode())

            logger.info(f'{self.__labelbox_name}: Labels exported. Project id: {projectid}, export url: {export_job["downloadUrl"]}.')

            path = ''
            if 'writefile' in kwargs:
                try:
                    _, path = self.dicts2jsonfile(labels, kwargs['writefile']['folder'],
                                            kwargs['writefile']['name'])
                except Exception:
                    raise Exception('Filepath not specified.')
        else:
            logger.info(f'{self.__labelbox_name}: No new labels to export or no new download url.')
            labels = None

        return labels
        

    def del_labels(self, label_ids: list) -> bool:
        '''
        Delete labels and reenque them.


        Args:
            labelIDs (list): list of label ids

        Returns:
            status_deleted (bool): <True>: all labels deleted

        '''
        label_ids_list = []
        num_items = 9000  # Labelbox restriction
        while True:
            if len(label_ids) >= num_items:
                label_ids_list.append(label_ids[0:num_items])
                label_ids = label_ids[num_items:]
                continue
            label_ids_list.append(label_ids)
            break

        status_deleted = True
        for lbl_ids in label_ids_list:
            try:
                res = self.__execute_graphql('''
                mutation{
                deleteLabels(
                    labelIds: $labelId,
                    waitForQueue:true
                )
                {
                    id,deleted
                }
                }
                ''',
                                             variables={'$labelId': lbl_ids})
                deleted = [
                    labels['deleted'] for labels in res['data']['deleteLabels']
                ]
                if 'False' in deleted:
                    status_deleted = False
            except KeyError:
                status_deleted = False

            logger.info(f'{self.__labelbox_name}: Delete labels. Status: {status_deleted}.')

        return status_deleted

    def extendName(self, listofnames, name):
        '''
        Check if name already exists and eventually extend name.
        Args:
            listofnames (str)
            name (str)
        Returns:
            nameNew (str)
        '''
        idx=1
        name_tmp = name
        while True:
            if name in listofnames:
                name = name_tmp + '(' + str(idx) + ')'
                idx+=1
                continue
            break
    
        return name

    def dicts2jsonfile(dataList:list,filepath:str,filename:str) -> tuple:
        '''
        Write a list of dictionaries to a json file.
        Args: 
        dataList (list): data as a list of dictionaries
        filepath (str): folder path
        filename (str): name of file without extension
        Return:
        status, path (tuple): <True>: successfull, <False>: not successful, path of file
        '''

        dataJson=json.dumps(dataList,indent=2)
        path = os.path.join(filepath,filename + '.json')
        try:
            with open(path,'w') as file:
                file.write(dataJson)
            status = True
        except Exception: 
            status = False
    
        return status, path
    

