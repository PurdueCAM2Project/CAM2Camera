import os
print("Imported Local Settings......")
SECRET_KEY = '7t@@r3(twocu_9j+hawhl+m3#1$n9thgs7=jb%m!=w-ig!315*'
ALLOWED_HOSTS = ['*']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'
STATIC_DIRS = (
   os.path.join(BASE_DIR, '/API/staticfile/'),
)
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
DEBUG = False