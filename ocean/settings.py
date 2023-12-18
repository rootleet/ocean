"""
Django settings for ocean project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-q^#wfi0xy1z-7nv9vj9r^137i=j@zzij8na9q4zr!dsg$-&q!b'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

LOGIN_URL = '/login/'

# Application definition

INSTALLED_APPS = [

    'stream.apps.StreamConfig',
    'blog.apps.BlogConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'admin_panel.apps.AdminPanelConfig',
    'community.apps.CommunityConfig',
    'api.apps.ApiConfig',
    'meeting.apps.MeetingConfig',
    'appconfig.apps.AppconfigConfig',
    'inventory.apps.InventoryConfig',
    'dolphine.apps.DolphineConfig',
    'cmms.apps.CmmsConfig',
    'apiv2.apps.Apiv2Config',
    'appscenter.apps.AppscenterConfig',
    'reports.apps.ReportsConfig',
    'taskmanager.apps.TaskmanagerConfig',
    'retail.apps.RetailConfig',
    'crm.apps.CrmConfig',
    'servicing.apps.ServicingConfig'
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

ROOT_URLCONF = 'ocean.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'ocean.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'ex': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ocean',
        'USER': 'root',
        'PASSWORD': 'Sunderland@411',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            "init_command": "SET foreign_key_checks = 0;",
        },
    },
    'online': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'u560949065_ocean',
        'USER': 'u560949065_ocean',
        'PASSWORD': 'Sunderland@411',
        'HOST': 'snedasmartmeter.com',
        'PORT': '3306',
        'OPTIONS': {
            "init_command": "SET foreign_key_checks = 0;",
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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

APPEND_SLASH = False

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

# STATIC_ROOT = ''
STATIC_URL = '/static/'
# Add these new lines
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
APP_VERSION = 0.1

# email config

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'henrychase411@gmail.com'
# EMAIL_HOST_PASSWORD = 'ldthggpiaisgfwdg'
# EMAIL_PORT = 587

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.snedamotors.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587  # I use this for SSL
EMAIL_HOST_USER = "no-reply@snedamotors.com"
EMAIL_HOST_PASSWORD = "Sunderland@411"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# email config


# session setting
SESSION_COOKIE_AGE = 1800  # 3 minutes. "1209600(2 weeks)" by default

SESSION_SAVE_EVERY_REQUEST = True  # "False" by default
# session settings


AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'ocean.auth.EmailBackend',
]

# CMMS DATA PARAMETERS
DB_SERVER = '192.168.2.4'
DB_PORT = '1237'
DB_USER = 'sa'
DB_PASSWORD = 'sa@123456'
DB_NAME = 'CMMS'

OLD_DB_SERVER = '192.168.2.4'
OLD_DB_PORT = '1433'
# DB_USER = 'sa'
# DB_PASSWORD = 'sa@123456'
OLD_DB_NAME = 'PROC_CMMS_V1'
# DB_SERVER = '127.0.0.1'
# #DB_PORT = '1237'
# DB_PORT = '1433'
# DB_NAME = 'PROC_CMMS_V1'

RET_DB_HOST = '192.168.2.4'
RET_DB_NAME = 'SMSEXPV17'
RET_DB_USER = 'sa'
RET_DB_PASS = 'sa@123456'
RET_DB_PORT = ''
