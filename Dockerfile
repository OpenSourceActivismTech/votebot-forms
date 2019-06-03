# base image
FROM python:2.7-alpine3.6

# set working directory
RUN mkdir -p /app
WORKDIR /app

# add a compiler
RUN apk add --no-cache --virtual .pynacl_deps build-base python2-dev libffi-dev linux-headers postgresql-dev bash curl

# add the code 
ADD . /app

# add the env vars
ENV FLASK_APP=app/wsgi.py \
    EASYPOST_API_KEY= \
    LOB_API_KEY= \
    AWS_ACCESS_KEY= \
    AWS_SECRET_KEY= \
    SENTRY_DSN= \
    SMARTY_STREETS_AUTH_ID= \
    SMARTY_STREETS_AUTH_TOKEN=

# expose the port
EXPOSE 5000:5000

# install requirements
#RUN pip install -r /app/requirements/development.txt
RUN pip install -r /app/requirements/heroku.txt

# start the server
CMD flask run --host 0.0.0.0
