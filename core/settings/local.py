from .base import *

DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1',
    '192.168.0.2'
]

INTERNAL_IPS = [
    '127.0.0.1',
    '192.168.0.2',
]

INSTALLED_APPS.extend([
    'debug_toolbar',
    'django_extensions',
])

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(BASE_DIR / 'db.sqlite3'),
    }
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #     'NAME': 'django_test',
    #     'USER': 'test_user',
    #     'PASSWORD': 'qwerty',
    #     'HOST': '192.168.0.2',
    #     'PORT': '',
    # }
}

print("Local settings loaded")