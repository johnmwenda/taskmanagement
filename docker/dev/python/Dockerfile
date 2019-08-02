FROM python:3.6
MAINTAINER johnmwenda@localhost

COPY ./app /app

WORKDIR /app

RUN pip install -r requirements/local.txt


COPY ./docker/dev/python/entrypoint.sh /entrypoint.sh