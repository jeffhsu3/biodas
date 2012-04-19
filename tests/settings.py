"""
A copy of django-tastypie's settings.py
"""

import os

ADMINS = (
    ('test@test.com', 'django-das'),
)

BASE_PATH = os.path.abspath(os.path.dirname(__file__))

MEDIA_ROOT = os.path.normpath(os.path.join(BASE_PATH, 'media'))

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'django-das.db'
TEST_DATABASE_NAME = 'django-das.db'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.%s' % DATABASE_ENGINE,
        'NAME': DATABASE_NAME,
        'TEST_NAME': TEST_DATABASE_NAME,
    }
}

BIODAS = os.path.abspath(os.path.join(BASE_PATH, '..'))

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'biodas',
    ]

DEBUG = True
TEMPLATE_DEBUG = DEBUG

#CACHES

USE_TZ = True

SECRET_KEY = 'djangodas_tests'

