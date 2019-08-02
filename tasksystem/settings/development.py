from .base import * 

DEBUG = True

# ALLOWED_HOSTS = ['0.0.0.0','127.0.0.1']
INTERNAL_IPS = [
    '127.0.0.1',
]

INSTALLED_APPS.extend(['silk', 'django_extensions'])
MIDDLEWARE.insert(0, 'silk.middleware.SilkyMiddleware')