# pull official base image
#FROM python:3.7-slim-buster
#FROM python:3.8.0-alpine

FROM alpine:3.11

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev postgresql-client gcc musl-dev python3-dev

RUN python3 -m pip install pip

#RUN pip install --upgrade pip
RUN python3 -m pip install --no-cache-dir setuptools pyyaml schedule

# install dependencies
RUN pip3 install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
#RUN pip install -r requirements.txt
RUN pip3 install psycopg2

# copy project
COPY . /usr/src/app/
VOLUME /usr/src/app/data

# ENTRYPOINT ["python3", "main.py"]
RUN chmod +x dbentry.sh
ENTRYPOINT ["/bin/sh", "./dbentry.sh"]
CMD [""]