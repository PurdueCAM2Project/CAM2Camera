<a name="SetUp"></a> 
## Setting Up git and Downloading Repository
Install git:

     sudo apt-get install git 

Download Repository:

     git clone https://github.com/PurdueCam2Project/CAM2API

## Creating Local Settings
Create Local Settings settings_local.py:

```python
# Django settings for NetworkCamerasAPI project.
import os
print("Imported Local Settings......")
SECRET_KEY = <Replace With Secret Key>
ALLOWED_HOSTS = ['*']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'
STATIC_DIRS = (
    os.path.join(BASE_DIR, 'static'),
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
DEBUG = True
```

## Installing Dependencies: 
`sudo apt-get install`
* python-dev 
* libpq-dev 
* postgresql 
* postgresql-contrib 
* postgis
* python3-pip 
* python3-venv

## Configuring Postgreql database
Switch to postgresql user:

     sudo su – postgres

Start postgresql shell:

     psql

Create API Database:

     postgres=# CREATE DATABASE cam2api;

Create Database User:

     postgres=# CREATE USER cam2api WITH PASSWORD ‘123456';

Give user access:

     postgres=# GRANT ALL PRIVILEGES ON DATABASE cam2api TO cam2api;

Switch to cam2api database:

     postgres=# \connect cam2api;

Add Postgis addon:

     postgres-# CREATE EXTENSION postgis;

Exit psql shell:

     postgres-# \q

Exit postgres user:

     exit

## Creating Virtual Environment 
Create venv:

     python3 –m venv venv

Start virtualenv

     source venv/bin/activate

Upgrade pip:

     (venv)$ pip install --upgrade pip

Install packages:

     (venv)$ pip install –r requirements.txt

Check Django Version:

     (venv)$ which django-admin.py

## Starting Django Server
Create Database Migrations biased on models:

     python manage.py makemigrations

Migrate Models to Database:

     python manage.py migrate

Start Server

     python manage.py runserver
