from pathlib import Path

import environ


PROJECT_ROOT = Path(__file__).parent.absolute()

root = environ.Path(PROJECT_ROOT)
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(root('.env'))


SECRET_KEY = env('SECRET_KEY', default='j&h=$-wbo%)5=(v!tmriwnin*(#95ho_erlkmi5$vjc)9d(7*$')

DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django_extensions',
    'rest_framework',
    'wallet',
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

ROOT_URLCONF = 'urls'

REST_FRAMEWORK = {'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',)}

WSGI_APPLICATION = 'wsgi.application'

DATABASES = {'default': env.db()}

# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False
