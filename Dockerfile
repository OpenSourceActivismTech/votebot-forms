# base image
FROM python:2.7.14-alpine

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# add a compiler
RUN apk add --no-cache --virtual .pynacl_deps build-base python3-dev libffi-dev postgresql-dev bash curl

# add the code 
ADD . /usr/src/app

# expose port 5000
EXPOSE 5000

# install requirements
RUN pip install -r /usr/src/app/requirements/development.txt
