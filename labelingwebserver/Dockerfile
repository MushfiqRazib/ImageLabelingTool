FROM ubuntu:18.04

# Install Utilities
RUN apt-get update -q  \
    && apt-get install -yqq \
    curl \
    make \
    build-essential \
    libkrb5-dev \
    net-tools \
    apt-utils 

# Install nodejs
RUN apt-get update \
    && apt-get install -yqq nodejs

# Install and copy Nginx
RUN apt-get update \
    && apt-get install -y nginx

COPY default /etc/nginx/sites-enabled/

# Copy supervisord conf
#COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

COPY nginx-selfsigned.key /etc/ssl/private/
COPY nginx-selfsigned.crt /etc/ssl/certs/
COPY dhparam.pem /etc/ssl/certs/

RUN mkdir -p /home/sslserver

RUN mkdir -p /home/labelapp/label_webserver

WORKDIR /home/sslserver

COPY . .

EXPOSE 9000

RUN apt-get update \ 
    && apt-get install -y npm 

RUN chmod +x entry.sh
CMD ["/bin/sh", "./entry.sh"]