FROM python:3.6
MAINTAINER johnmwenda@localhost

COPY ./tasksystem /tasksystem
COPY ./requirements /requirements

WORKDIR /requirements

RUN pip install -r requirements/prod.txt

WORKDIR /tasksystem

EXPOSE 8000


CMD ["gunicorn", "tasksystem.wsgi", "-b 0.0.0.0:8000"]