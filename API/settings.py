"""
This file holds all the general setting information for the
CAM2API
"""

import os

# Root Project Directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR =  os.path.dirname(PROJECT_ROOT)

# Default Set of DEBUG is False
DEBUG = False

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'django.contrib.gis',
	'rest_framework',
	'rest_framework.authtoken',
	'CAM2API',
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

ROOT_URLCONF = 'API.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		#'DIRS': ['API/staticfiles/','API/templates/'],
		'DIRS': [os.path.join(BASE_DIR, '/CAM2API/templates')],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				"django.template.context_processors.i18n",
				"django.template.context_processors.static",
				'django.contrib.messages.context_processors.messages',
			],
		},
	},
]

WSGI_APPLICATION = 'API.wsgi.application'

#AUTH_USER_MODEL = 'CAM2API.Account'


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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

# REST_framework libraries
REST_FRAMEWORK = {
	'DEFAULT_AUTHENTICATION_CLASSES': (
		#'rest_framework.authentication.BasicAuthentication',
		#'rest_framework.authentication.SessionAuthentication',
	),
	'DEFAULT_RENDERER_CLASSES': (
		'rest_framework.renderers.JSONRenderer',
	),
	'DEFAULT_PARSER_CLASSES': (
		'rest_framework.parsers.JSONParser',
	),
	'DEFAULT_PERMISSION_CLASSES': (
		#'rest_framework.permissions.IsAuthenticated',
		#'CAM2API.permissions.CAM2APIPermission', 
	)
}

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_REDIRECT_URL = '/cameras'

LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'handlers': {
		'file': {
			'level': 'DEBUG',
			'class': 'logging.FileHandler',
			'filename': 'debug.log',
		},
	},
	'loggers': {
		'django': {
			'handlers': ['file'],
			'level': 'DEBUG',
			'propagate': True,
		},
	},
}

ADMINS = [('Ryan', "dailey1@purdue.edu")]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'wang50278668@gmail.com'
EMAIL_HOST_PASSWORD = 'Wjc50278668'
EMAIL_USE_TLS = True

# Import settings specific to deployment
try:
	from .settings_local import *
except ImportError:
	try:
		from .settings_remote import *
	except ImportError:
		pass

