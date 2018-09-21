"""
Django settings for SkriptNet project.

Generated by 'django-admin startproject' using Django 2.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import json

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Config Datei lesen
config_file = os.path.join(BASE_DIR, 'SkriptNet/config.json')
with open(config_file, 'r') as f:
    config = json.load(f)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config["SECRET_KEY"]


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*",]

# Application definition

INSTALLED_APPS = [
    # Django Apps
    'django.contrib.admin',
    # https://docs.djangoproject.com/en/dev/ref/contrib/admin/admindocs/
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third Party Apps
    # Google reCAPTCHA: https://github.com/praekelt/django-recaptcha
    'captcha',
    'crispy_forms',
    # http://django-extensions.readthedocs.io/en/latest/graph_models.html
    'django_extensions',

    # My Apps
    'skripten_shop'
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

ROOT_URLCONF = 'SkriptNet.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'SkriptNet.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/
LANGUAGE_CODE = 'de-DE'
TIME_ZONE = 'Europe/Berlin'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')




STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

FIXTURE_DIRS = (
    os.path.join(BASE_DIR, 'fixtures'),
)

LOGIN_URL = '/'

# https://docs.djangoproject.com/en/dev/topics/logging/#topic-logging-parts-filters
# TODO: Logger für verschiedene Level erstellen
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logfiles/skripten_shop.log'),
            'maxBytes': 300 * 1024 * 1,  #Byte = 0,3MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },

    'formatters': {
        'simple': {
            'format': '%(levelname)s|%(message)s'
        },

        'verbose': {
            'format': '%(levelname)s|%(asctime)s|%(module)s|%(funcName)s|%(message)s',
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },

    'loggers': {
        'skripten_shop': {
            'level': 'DEBUG',
            'handlers': ['default', ],
        }
    },
}

# My Settings
#############################################################
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# Django reCAPTCHA
# https://github.com/praekelt/django-recaptcha
RECAPTCHA_PUBLIC_KEY = config["RECAPTCHA_PUBLIC_KEY"]
RECAPTCHA_PRIVATE_KEY = config["RECAPTCHA_PRIVATE_KEY"]
NOCAPTCHA = True

# Mail Setting
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'ldap.fs04.ee.hm.edu'
EMAIL_HOST_PORT = '587'
EMAIL_PORT = '587'
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config["EMAIL_USER"]  # 'skriptnet@fs04.ee.hm.edu'
EMAIL_HOST_PASSWORD = config["EMAIL_PW"]
DEFAULT_FROM_EMAIL = 'skriptnet@fs04.ee.hm.edu'
