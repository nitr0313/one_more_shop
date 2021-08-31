from pathlib import Path
import json
import os
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent.parent


# EMAIL SETTINGS
EMAIL_HOST = 'smtp.mail.ru'
EMAIL_PORT = 2525
EMAIL_USE_TLS = True

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


def get_secret(setting, secret):
    try:
        return secret[setting]
    except KeyError:
        raise ImproperlyConfigured(
            f'Set the {setting} environment, variable'
        )

try:
    with open('secret.json', 'r') as fl:
        secret = json.load(fl)
except Exception as e:
    print(f'Неудачная попытка импорта настроек email, ведите собственные настроки, {e}')

EMAIL_HOST_USER = get_secret("EMAIL_HOST_USER", secret)
EMAIL_HOST_PASSWORD = get_secret("EMAIL_HOST_PASSWORD", secret)
SECRET_KEY = get_secret("SECRET_KEY", secret)


SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'l*b7w)uvn(12kfajjk8ii^pv*j149-@vjwqfca18*l4761f1&r'

ALLOWED_HOSTS = []

# Application definition
CART_SESSION_ID = 'cart'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mptt',
    'account.apps.AccountConfig',
    'shop.apps.ShopConfig',
    'order',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates',]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'shop.context_processor.cart'
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

MPTT_ADMIN_LEVEL_INDENT = 20

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases




# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Moscow' #'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/assets/'
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_DIRS = [
    BASE_DIR / 'assets',
]





MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
TEMP_ROOT = BASE_DIR / 'tmp'
