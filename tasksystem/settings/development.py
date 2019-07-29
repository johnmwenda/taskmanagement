from .base import * 

DEBUG = True

INTERNAL_IPS = [
    '127.0.0.1',
]

INSTALLED_APPS.extend(['debug_toolbar', 'django_extensions'])
MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware', )