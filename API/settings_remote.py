"""
Django settings for API project.
Specific settings are imported other setting libraries for better
control.
"""
import dj_database_url
import os

print("Imported Remote Settings......")

# Root Project Directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(PROJECT_ROOT)

# SECURITY WARNING: keep the secret key used in production secret!
# To add secret key variable to Heroku Deployment use "heroku
# config:add DJANGO_SECRET_KEY=<your secret key>"
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Ensures all API requests are directed through HTTPS
SECURE_SSL_REDIRECT = True

# # Using white noise to collect static files on production
# STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

# # Static asset configuration
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# STATIC_URL = '/static/'
# # Extra places for collectstatic to find static files.
# STATICFILES_DIRS = (
#     os.path.join(BASE_DIR, 'API/static/api-view'),
#     os.path.join(BASE_DIR, 'API/static'),
# )
# WHITENOISE_ROOT = os.path.join(BASE_DIR, 'staticfiles', 'root')

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
STATIC_URL = '/static/'
# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'API/static/api-view'),
)
# https://warehouse.python.org/project/whitenoise/
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

# Ensures all API requests are directed through HTTPS
# SECURE_SSL_REDIRECT = True

# Get geoDjango GEOS and GDAL library paths from Heroku environment variables
GEOS_LIBRARY_PATH = os.environ.get('GEOS_LIBRARY_PATH')
GDAL_LIBRARY_PATH = os.environ.get('GDAL_LIBRARY_PATH')



#For Travis Testing DataBase
if 'TRAVIS' in os.environ:
	print("Import TRAVIS Setting")
	DATABASES = {
    	'default': {
    	    'ENGINE': 'django.contrib.gis.db.backends.postgis',
    	    'NAME': 'cam2api',
    	    'USER': 'cam2api',
    	    'PASSWORD': '123456',
    	    'HOST': 'localhost',
    	    'PORT': '',
    	}
	}
	STATIC_DIRS = (os.path.join(BASE_DIR, 'static'),)
	SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
	BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	STATIC_ROOT = 'staticfiles'
	STATIC_URL = '/static/'
	SECURE_SSL_REDIRECT = False
else:
	# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
	# Heroku Database
	DATABASES = {
    'default': dj_database_url.config(default=os.environ['DATABASE_URL'])
}
	# Add PostGIS engine
	DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'


ALLOWED_HOSTS = ["*"]

# Default Set of DEBUG is False
DEBUG = True
