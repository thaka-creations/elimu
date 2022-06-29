"""
Django settings for Elimu project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")
TOKEN_SECRET_KEY = os.environ.get('TOKEN_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

CORS_ORIGIN_ALLOW_ALL = True

OAUTH2_PROVIDER = {
    'ACCESS_TOKEN_EXPIRE_SECONDS': int(os.environ.get('ACCESS_TOKEN_EXPIRY')),
    'OAUTH_SINGLE_ACCESS_TOKEN': True,
    'OAUTH_DELETE_EXPIRED': True,
    'ROTATE_REFRESH_TOKEN': True,
}

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'oauth2_provider',
    'corsheaders',
    'school',
    'mfa',
    'users',
    'payments',
    'video',
    'staff'
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'users.utils.auth.SystemAuthentication',
    ],
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Elimu.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media'
            ],
            'libraries':
                {
                    'tags': 'school.templatetags.tags',
                }
        },
    },
]

WSGI_APPLICATION = 'Elimu.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get("DATABASE_NAME"),
        'USER': os.environ.get("DATABASE_USER"),
        'PASSWORD': os.environ.get("DATABASE_PASSWORD"),
        'HOST': os.environ.get("DATABASE_HOST"),
        'PORT': os.environ.get("DATABASE_PORT")
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


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

AUTH_USER_MODEL = 'users.User'

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REGISTRATION_OTP_EXPIRY_TIME = os.environ.get('REGISTRATION_OTP_EXPIRY_TIME')

ACCESS_TOKEN_EXPIRY = os.environ.get('ACCESS_TOKEN_EXPIRY')

SERVICES_URLS = {
    'callback_url': os.environ.get('TRANSFER_PROTOCOL') + '://' + os.environ.get('ACL_SERVICE') +
    os.environ.get('API_VERSION')
}

LOGIN_URL = "/login"
LOGOUT_REDIRECT_URL = "/login"

# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static'),
# ]

# STATICFILES_DIRS = ['/var/www/static/']
STATIC_ROOT = "/var/www/static/"

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

MPESA_CONSUMER_KEY = os.environ.get("MPESA_CONSUMER_KEY")
MPESA_CONSUMER_SECRET = os.environ.get("MPESA_CONSUMER_SECRET")
MPESA_SHORTCODE = os.environ.get("MPESA_SHORTCODE")
MPESA_SHORTCODE_TYPE = os.environ.get("MPESA_SHORTCODE_TYPE")
MPESA_PASSKEY = os.environ.get("MPESA_PASSKEY")
MPESA_CALLBACK_URL = os.environ.get("MPESA_CALLBACK_URL")
VDOCIPHER_SECRET = os.environ.get("VDOCIPHER_SECRET")

# MPESA_CONSUMER_KEY = 'uQH9B9rRvYHvpM2ICYyvBdwR0UE6Pvz4'
# MPESA_CONSUMER_SECRET = 'DurpnNk6Z21uDjaW'
# MPESA_SHORTCODE = '4083027'
# MPESA_SHORTCODE_TYPE = 'paybill'
# MPESA_PASSKEY = '9cd4dd3777a83ffc18c70766a77e1f2077dbaea17188f98235158ed533f3331d'
# MPESA_CALLBACK_URL = 'https://60df-105-166-128-242.eu.ngrok.io/api/v1/payments/callback'
#
# VDOCIPHER_SECRET = 'MPv32VRtyY5lpuT7VFTWNQxLhstDB7XoA5nEMjB501XpZlSjSFx5iYHiij8bnmOr'