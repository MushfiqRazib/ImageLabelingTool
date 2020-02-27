# Setting up Labeling Webserver

## Instal Node js:

**sudo apt-get update** <br />

**sudo apt-get install nodejs** <br />

**sudo apt-get install npm** <br />


Finally, install the build-essential package for npm:

**sudo apt-get install build-essential** <br />

To check which version of Node.js you have installed after these initial steps, type:

**nodejs -v** <br />


## Install Apache Web Server

To install Apache, install the latest meta-package apache2 by running:

**sudo apt update** <br />

**sudo apt install apache2**


After letting the command run, all required packages are installed. 

# Checking your Web Server
Check with the systemd init system to make sure the service is running by typing:

**sudo systemctl status apache2** <br /> 

=========================== Output ==================================== <br />
● apache2.service - LSB: Apache2 web server <br />
   Loaded: loaded (/etc/init.d/apache2; bad; vendor preset: enabled) <br />
  Drop-In: /lib/systemd/system/apache2.service.d <br />
           └─apache2-systemd.conf <br />
   **Active: active (running) since Tue 2019-07-23 22:49:28 CEST; 23h ago** <br />
     Docs: man:systemd-sysv-generator(8) <br />
   CGroup: /system.slice/apache2.service <br />
           ├─ 1592 /usr/sbin/apache2 -k start <br />
           ├─30897 /usr/sbin/apache2 -k start <br />
           ├─30898 /usr/sbin/apache2 -k start <br />
           ├─30899 /usr/sbin/apache2 -k start <br />
           ├─30900 /usr/sbin/apache2 -k start <br />
           └─30901 /usr/sbin/apache2 -k start <br />

Jul 23 22:49:28 mushfiqrahman apache2[1529]:  * <br />
Jul 23 22:49:28 mushfiqrahman systemd[1]: Started LSB: Apache2 web server. <br />
Jul 23 20:54:15 mushfiqrahman systemd[1]: Reloading LSB: Apache2 web server. <br />
Jul 23 20:54:15 mushfiqrahman apache2[6726]:  * Reloading Apache httpd web server apache2 <br />
Jul 23 20:54:15 mushfiqrahman apache2[6726]:  * <br />
Jul 23 20:54:15 mushfiqrahman systemd[1]: Reloaded LSB: Apache2 web server. <br />
Jul 24 12:13:07 mushfiqrahman systemd[1]: Reloading LSB: Apache2 web server. <br />
Jul 24 12:13:07 mushfiqrahman apache2[30879]:  * Reloading Apache httpd web server apache2 <br />
Jul 24 12:13:07 mushfiqrahman apache2[30879]:  * <br />
Jul 24 12:13:07 mushfiqrahman systemd[1]: Reloaded LSB: Apache2 web server. <br />

=========================== END OF Output ==================================== <br />

Access the default Apache landing page to confirm that the software is running properly through your IP address: <br />

http://your_server_ip <br />

Ex: **http://localhost**  <br />

You should see the default Ubuntu 16.04 Apache web page. <br />

## Download labelingwebserver codebase from Git
Download the code and copy it to any location in your pc.  <br />
link: https://gitlab.lrz.de/imagerecognition/labeling/tree/develop/labelingwebserver  <br />

## Configure proxy
Next thing we need to proxy all requests incoming on port 80 through the URL of a node.js application to the running local node.js process. 
For this, we need to install/enable mod_proxy and mod_proxy_http modules on the Apache server by using below commands:

**a2enmod proxy** <br /> 

**a2enmod proxy_http**


## Configure apache conf file
1. Go to **/etc/apache2/sites-available/**
2. You will find **000-default.conf** file 
3. open up the conf file by using any editor. For exampe, to open the conf file in vi editor, below command is used:
   sudo vi 000-default.conf or sudo geddit 000-default.conf
4. Edit the file like the below example conf file: 

========================================== 000-default.conf =================================== <br />

<VirtualHost *:80>

	ServerAdmin webmaster@localhost
	ServerName mysite
	ServerAlias www.mysite.com
        DocumentRoot /var/www/html/mysite
	Alias   "/labelingwebserver/" "/home/mushfiqrahman/dev/labeling_dev_branch/labeling/labelingwebserver/"
	<Directory />
		Options -Indexes +FollowSymLinks
		AllowOverride None
		Require all granted
	</Directory>


	# AddHandler cgi-script .py
	# The ServerName directive sets the request scheme, hostname and port that
	# the server uses to identify itself. This is used when creating
	# redirection URLs. In the context of virtual hosts, the ServerName
	# specifies what hostname must appear in the request's Host: header to
	# match this virtual host. For the default virtual host (this file) this
	# value is not decisive as it is used as a last resort host regardless.
	# However, you must set it for any further virtual host explicitly.
	# ServerName www.example.com

	ProxyRequests Off
	ProxyPreserveHost On
	ProxyVia Full
	<Proxy *>
		Require all granted
	</Proxy>

	<Directory "/mushfiqrahman/dev/labeling_dev_branch/labeling/labelingwebserver/">
                Order allow,deny
                Allow from all
    </Directory>

	<Location "/home/mushfiqrahman/dev/labeling_dev_branch/labeling/labelingwebserver/">
		ProxyPass http://127.0.0.1:3000
		ProxyPassReverse http://127.0.0.1:3000
	</Location>

	Alias "/outimg/" "/home/mushfiqrahman/dev/Project_Root/"
	<Directory "/home/mushfiqrahman/dev/Project_Root/">
		Order allow,deny
		Allow from all
	</Directory>


	# Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
	# error, crit, alert, emerg.
	# It is also possible to configure the loglevel for particular
	# modules, e.g.
	#LogLevel info ssl:warn

	ErrorLog ${APACHE_LOG_DIR}/error.log
	CustomLog ${APACHE_LOG_DIR}/access.log combined

	# For most configuration files from conf-available/, which are
	# enabled or disabled at a global level, it is possible to
	# include a line for only one particular virtual host. For example the
	# following line enables the CGI configuration for this host only
	# after it has been globally disabled with "a2disconf".
	#Include conf-available/serve-cgi-bin.conf
</VirtualHost>

=============================== END of CONF FILE =================================== <br />

Run this command to restart the apache after updating and exit from conf file: 

**sudo systemctl restart apache2**

## Commands to generate private key, certificate files

At first go to the labelingwebserver codebase from command prompt. <br />

Ex: /dev/mushfiqrahman/labeling_dev_branch/labeling/labelingwebserver/ <br />

Run below commands from the command prompt: 

1. **openssl genrsa -out privatekey.pem 1024** <br />

   This will generate a RSA private key file named as privatekey.pem reside at the same location i.e. webserver root directory.
 
2. **openssl req -new -key privatekey.pem -out certrequest.csr** <br />

   This command will ask you some questionnaire and you have to answer this questions. Then the command will generate a certrequest.csr file also in the web root directory.

3. **openssl x509 -req -in certrequest.csr -signkey privatekey.pem -out certificate.pem** <br />

   This command executes signing the .csr file with private key file and generate a certificate.pem file. (also reside at the web root directory)

## Change index.js file:

Change below line of code from index.js file:  <br />

rootDir = '/home/mushfiqrahman/dev/Project_Root/' to *rootDir = 'the/path/you/mentioned/in/the/Alias/outimg/of/default.conf/file'*

## Run the index.js file:
To run the server, at first go to the labelingwebserver codebase from command prompt. <br /> 

Ex: /dev/mushfiqrahman/labeling_dev_branch/labeling/labelingwebserver/

Run the command: <br />

**nodejs index.js**

output: 

*Server running at https://127.0.0.1:3000/*  <br />

Paste the link to web browser. Since, this https, it will require advanced option to be clikced and then click on proceed link.
Then you will see the webserver with the generated web urls of the images from the specified Project_Root direcoty. 

## Stop the Labeling Webserver:

So, to stop the webserver, below 2 ways are sufficient. 
1. The easiest one is - Pressing **Ctrl + C**

   Ctrl + C sends SIGINT, which allows the program to end gracefully, unbinding from any ports it is listening on.

2. For the second one, run this below command from a separate terminal which also shut down the webserver.

    **sudo killall nodejs**


N.B.: You can run the whole codebase from a pip virtual environment or anaconda virtual environment. Also, without virtual environment, this webserver is running perfectly.

~ Cheers

## Setting.py
*  WEB_SERVER_HTTPS = True

