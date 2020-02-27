# pull official base image
#FROM python:3.7-slim-buster
#FROM python:3.8.0-alpine

FROM alpine:3.11

# set work directory
#WORKDIR /usr/src/labelapp
RUN mkdir -p /home/labelapp/labelingapp
WORKDIR /home/labelapp/labelingapp

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev postgresql-client gcc musl-dev python3-dev tzdata

RUN python3 -m pip install pip

#RUN pip install --upgrade pip
RUN python3 -m pip install --no-cache-dir setuptools pyyaml schedule

# install dependencies
RUN pip3 install --upgrade pip
COPY ./requirements.txt /home/labelapp/labelingapp/requirements.txt
#COPY ./Pipfile /usr/src/labelingapp/Pipfile
RUN pip3 install -r requirements.txt
#RUN pip3 install psycopg2

ENV TZ Europe/Berlin

# copy project
COPY . /home/labelapp/labelingapp
#VOLUME /home/labelapp/FZG-NAS/461_DatenBilderkennung

ENTRYPOINT ["python3", "main.py"]
#CMD [""]