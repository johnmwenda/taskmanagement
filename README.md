Task Management System for Company DgO

This API is built using Django and Django Rest Framework

## Prerequisites
[Postgres](https://www.postgresql.org/)
[Redis](https://redis.io/)
[Django-Celery](https://docs.celeryproject.org/en/latest/django/first-steps-with-django.html/)
[Docker](https://www.docker.com/)
[Docker-compose](https://docs.docker.com/compose/)

## Installation and Setup
1. Clone the repo
2. Go to app/tasksystem/ and edit environment.py to select preferred environment
3. cd to root and build docker
```
docker-compose build
```
This will download and install all the required images
3. cd to root and run docker
```
docker-compose up
```
This will download and install all the required images

4. In app/tasksystem/settings/local.py add the defaults you would like configured.

```
export SECRET_KEY='akjshdkqiu3ye723y42i34'
export DEBUG = False
EMAIL_HOST = env.str('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = env.str('EMAIL_PORT', '587')
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER', 'your_email@host.com')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD', 'password')
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
```


For database settings; ensure your host is 'postgres' which is the docker service running the database server

```
export POSTGRES_DB_NAME = 'tasksystem'
export POSTGRES_DB_USER = 'tasksystem'
export POSTGRES_DB_PASSWORD = 'tasksystem'
export POSTGRES_DB_HOST = 'postgres'
export POSTGRES_DB_PORT = 5432
```

Ensure you set the celery broker(redis) url in django settings. Since we are running on docker the address of redis will be the name of the docker service

```
CELERY_BROKER_URL = 'redis://redis'
```