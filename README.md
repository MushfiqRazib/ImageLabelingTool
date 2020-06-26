# Labeling Tool for Image Recognition 

## Steps for Webserver Deployment Using Docker

To run the webserver, below steps are taking place:

1. Assign the rootDir value (image files location) in index.js file. 

2. Assign the same image files location to the Nginx configuration file named as 'default' file: [https://gitlab.lrz.de/imagerecognition/labeling/-/blob/develop/labelingwebserver/default](https://gitlab.lrz.de/imagerecognition/labeling/-/blob/develop/labelingwebserver/default)
  
   ```
   location /labelimg/ {
                # alias /home/mushfiqrahman/dev/ProjectRoot/;
                alias /home/labelapp/FZG-NAS/461_DatenBilderkennung/; 
        }

   ```
   After alias command, the image files location should be placed there which is similar to rootDir value.

3. Make a directory in the server pc where you are going to deploy the webserver. Lets' call it 'label_webserver'. 
   
   So, the path location will be:` /home/labelapp/label_webserver `
   
   Put this path location in the Dockerfile file. The changed line command in the Dockerfile will be given below:

   `RUN mkdir -p /home/label_app/label_webserver`

4. Log in to gitlab docker container where the labelwebserver image file is uploaded. 

   `docker login gitlab.lrz.de:5005`

5. pull the application image from the gitlab container or any docker container by the following command:
   
   `sudo docker pull containerimagename`

6. Run the labelwebserver image by below command: 
   
   `sudo docker run -d -p 9000:443 --name labelwebserver -v /home/labelapp/FZG-NAS/461_DatenBilderkennung:/home/labelapp/FZG-NAS/461_DatenBilderkennung labelwebserver:latest`

   Here, the volume -v is mounted to the original images location.

## Docker Build command:

`docker build -t labelingapp:latest .`

`docker push labelingapp:latest`


N.B.: login credential error for docker.io has been solved. 

Useful link:[https://github.com/docker/docker-credential-helpers/issues/102](https://github.com/docker/docker-credential-helpers/issues/102)

## Dockering labeling app:

1. Build docker image for labeling app using LabelManagerApp docker file: [https://gitlab.lrz.de/imagerecognition/labeling/-/blob/develop/LabelManagerApp/Dockerfile](https://gitlab.lrz.de/imagerecognition/labeling/-/blob/develop/LabelManagerApp/Dockerfile) 
   
   Docker build command for labeling app:

   `docker build -t labelingapp:latest .`
   
2. Push labeling docker image to docker hub: 

   `docker push labelingapp:latest`

3. Pull labeling docker image to server:

   `docker push labelingapp:latest`

4. Run labeling docker from commandline with below commands:

   a. Run general labelingapp:

      `sudo docker run --rm -it --network=host --name labelapp -v /home/labelapp/FZG-NAS/461_DatenBilderkennung:/home/labelapp/labelingapp/data:rw labelingapp:latest -lb`

   b. Change project id with below comamnd:
 
      `sudo docker run --rm -it --network=host --name labelapp -v /home/labelapp/FZG-NAS/461_DatenBilderkennung:/home/labelapp/labelingapp/data:rw labelingapp:latest -rm 'project' -pid 1`

   c. Change project name with below command: 
 
      `sudo docker run --rm -it --network=host --name labelapp -v /home/labelapp/FZG-NAS/461_DatenBilderkennung:/home/labelapp/labelingapp/data:rw labelingapp:latest -rm 'project' -pname 'project2'`


## Install Postgresql:

```
sudo apt update && sudo apt install postgresql-12
systemctl status postgresql
```

To check whether the Postgresql install or not, following commands can be used: 

```
sudo systemctl stop postgresql.service
sudo systemctl start postgresql.service
sudo systemctl enable postgresql.service
sudo systemctl status postgresql.service

```

Postgresql version check:

```
sudo -u postgres psql 
SHOW server_version;
```

For Postgres user, need to update password:

```
sudo -u postgres psql
ALTER USER postgres PASSWORD 'postgres';
```

Configuration file i.e. pg_hba.conf check: 

```
sudo gedit /etc/postgresql/12/main/pg_hba.conf
host    all         all         127.0.0.1/32         trust
```

To restart postgresql service:

`sudo systemctl restart postgresql`

To check the status of the postgresql:

`systemctl status postgresql`

Commandline psql queries:

```
sudo -u postgres psql
postgres=# CREATE DATABASE labelingdb;
```

Enter command \l to get a list of all databases

To connect to a Database use the command:
```
\c labeldb
\dt  (list all the tables)
\pset pager off
```

Paste the all the tables script then.

Now in Psql you could run commands such as:

```
\? list all the commands
\l list databases
\conninfo display information about current connection
\c [DBNAME] connect to new database, e.g., \c template1
\dt list tables of the public schema
\dt <schema-name>.* list tables of certain schema, e.g., \dt public.*
\dt *.* list tables of all schemas
Then you can run SQL statements, e.g., SELECT * FROM my_table;(Note: a statement must be terminated with semicolon ;)
\q quit psql
```

For testing a table creation, create below table script: 

```
CREATE TABLE playground (
    equip_id serial PRIMARY KEY,
    type varchar (50) NOT NULL,
    color varchar (25) NOT NULL,
    location varchar(25) check (location in ('north', 'south', 'west', 'east', 'northeast', 'southeast', 'southwest', 'northwest')),
    install_date date
);
```

## Dockering Database Backup & Restore 

1. Change the root path where backup files will be stored from settings file: [https://gitlab.lrz.de/imagerecognition/labeling/-/blob/develop/db/code/settings.py](https://gitlab.lrz.de/imagerecognition/labeling/-/blob/develop/db/code/settings.py)

   `self.ROOT_PATH = r"/usr/src/app/data"`

2. Build docker image for database app docker file: [https://gitlab.lrz.de/imagerecognition/labeling/-/blob/develop/db/code/Dockerfile](https://gitlab.lrz.de/imagerecognition/labeling/-/blob/develop/db/code/Dockerfile) 
   
   Docker build command for labeldb app:

   `docker build -t labeldbapp:latest .`

3. Push labeldb docker image to docker hub: 

   `docker push labeldbapp:latest`

4. Pull labeling docker image to server:

   `docker push labeldbapp:latest`

5. Docker command for backup db: 

   `sudo docker run --rm -it --network=host --name labeldb_backup -v /home/labelapp/labelingdb:/usr/src/app/data/:rw labeldbapp:latest -pd backup`

6. Docker command for restore db: 

   `sudo docker run --rm -it --network=host --name labeldb_restore -v /home/labelapp/labelingdb:/usr/src/app/data/:rw labeldbapp:latest -pd restore -f /usr/src/app/data/backup/2020/20200122-labelapp-backup.tar`


##  Docker-Compose Implementation 

Installing docker-compose:

```
sudo curl -L "https://github.com/docker/compose/releases/download/1.25.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
```

checking docker-compose version:

```
docker-compose --version
docker-compose version 1.25.4, build 1110ad01
```

Remove docker-compose:

```
which docker-compose
sudo rm -rf /usr/bin/docker-compose
```

Before docker-compose running, pull all the related docker images from the docker hub to the server machine. For example:

```
sudo docker login -u rahman19  ## docker hub login

docker hub user: rahman19 pwd: adminhub19
```

Pulling images from the docker hub commands:

```
sudo docker pull labelwebserver:latest
sudo docker pull labeldbapp:latest
sudo docker pull labelingapp:latest
```

Writing ['docker-compose.yml'](https://gitlab.lrz.de/imagerecognition/labeling/-/blob/develop/docker-compose.yml) file:

1. Check that all the 3 images have the same name as deployed image names into the server machine.

Copy ['docker-compose.yml'](https://gitlab.lrz.de/imagerecognition/labeling/-/blob/develop/docker-compose.yml) file from git branch to the server machine. For example:

`rsync -r -a -v ssh /home/mushfiqrahman/dev/develop_branch/labeling/docker-compose.yml labelapp@tumwfzg-lise.srv.mwn.de:/home/labelapp/labelingapp`

Running docker-compose file:

```
sudo docker-compose up
sudo docker-compose ps -a
```
After docker-compose running, execute the command for labeling app and database backup/restore app like below:

```
sudo docker exec -it labelingapp python3 main.py -lb  # for running labelingapp application

sudo docker exec -it labeldbapp  python3 main.py -pd backup  # for backup labeldb db
```




