from django.test import TestCase
from django.db import IntegrityError
from django.db import transaction
from django.contrib.gis.gdal.error import GDALException
from django.core.management.base import BaseCommand
from CAM2API.models import Camera,  Non_IP,  IP
from django.contrib.gis.geos import GEOSGeometry
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.reverse import reverse
from psycopg2 import DataError
from django.db.utils import DataError
from django.core.exceptions import ValidationError
import random
import string
import json
import os
'''
Fixed Test Cases Index

POST TEST

    Basic Correctness Test
        Data for Test Case C1 - Correct IP Camera Test
        Data for Test Case C2 - Correct Non IP Camera Test

    Missing Information Test
        Data for Test Case E1 - Wrong IP Camera Without IP Test
        Data for Test Case E2 - Correct IP Camera Without PORT Test
        Data for Test Case E3 - Wrong Non IP Camera Without URL Test
        Data for Test Case E4 - Wrong Camera With URL and IP Test
        Data for Test Case E5 - Wrong Camera Without URL and IP Test
        Data for Test Case E6 - Wrong Non IP Camera With URL and PORT Test
        Data for Test Case E7 - Wrong Camera With URL,  IP and PORT Test
        Data for Test Case E8 - Wrong Camera Without ID Test
        Data for Test Case E9 - Wrong Camera Without city Test
        Data for Test Case E10 - Correct Camera Without state Test
        Data for Test Case E11 - Wrong Camera Without Lag Test
        Data for Test Case E12 - Wrong Camera Without lng Test
        Data for Test Case E13 - Wrong Camera Without source Test
        Data for Test Case E14 - Wrong Camera Without source_url Test


    Uniqueness Test
        Data for Test Case U1 - Wrong duplicated Camera ID Test
        Data for Test Case U2 - Wrong duplicated URL Test
        Data for Test Case U3 - Wrong duplicated IP Test
        Data for Test Case U4 - Wrong duplicated URL but different IP Test
        Data for Test Case U5 - Wrong duplicated IP but different URL Test

    Non Exist Camera Test
        Data for Test Case N1 - Wrong Camera ID to get Test
    
    HTTP Status Code Test
        Data for Test Case H1 - 200
        Data for Test Case H2 - 201
        Data for Test Case H3 - 404
        Data for Test Case H4 - 404
        Data for Test Case H5 - 404
        Data for Test Case H6 - 404
        Data for Test Case H7 - 500

    Information Syntex Test
        Data for Test Case I1 - Wrong 'lat' and 'lng' contains punctuation
        Data for Test Case I2 - Wrong 'lat' exceed limitation
        Data for Test Case I3 - Wrong 'lng' exceed limitation
        Data for Test Case I4 - Wrong city contains number
        Data for Test Case I5 - Wrong source_url wrong form
        Data for Test Case I6 - Wrong source_url wrong form
        Data for Test Case I7 - Wrong source_url wrong form
        Data for Test Case I8 - Wrong is_video true/false
        Data for Test Case I9 - Wrong is_video not 1 or 0
        Data for Test Case I10 - Wrong frame_rate not number
        Data for Test Case I11 - Wrong frame_rate not number 2
        Data for Test Case I12 - Wrong Indoor is 1 or 0
        Data for Test Case I13 - Wrong Indoor is char
        Data for Test Case I14 - Wrong Traffic
        Data for Test Case I15 - Wrong inactivite
        Data for Test Case I16 - Wrong resolution 
        Data for Test Case I17 - Wrong resolution
        Data for Test Case I18 - Wrong IP form
        Data for Test Case I19 - Wrong IP form
        Data for Test Case I20 - Wrong IP form
        Data for Test Case I21 - Wrong IP form
        Data for Test Case I22 - Wrong IP form
        Data for Test Case I23 - Wrong PORT 
        Data for Test Case I23 - Wrong PORT 
        Data for Test Case I24 - Wrong PORT
        Data for Test Case I25 - Wrong ID
        Data for Test Case I26 - Wrong ID
        Data for Test Case I27 - Wrong URL
        Data for Test Case I28 - Wrong URL
        Data for Test Case I29 - Wrong URL

    Advanced Information Conflict Test
        Data for Test Case NL1 - Wrong location of 'lag' and 'lng'(In the Sea) Test
        Data for Test Case NL2 - Wrong location of 'lag' and 'lng'(In the Sea) Test
        Data for Test Case NL3 - Wrong Country mismatch with 'lag' and 'lng' Test
        Data for Test Case NL4 - Wrong Country mismatch with 'lag' and 'lng' Test
        Data for Test Case NL5 - Wrong City mismatch with 'lag' and 'lng' Test
        Data for Test Case NL6 - Wrong City mismatch with 'lag' and 'lng' Test
        Data for Test Case NL7 - Wrong unknown City with another same but wrong named City Test

GET TEST


PUT TEST


DELETE TEST
'''

class API_View_Tests(APITestCase): 
    def randomUrl(self):
        return 'http://www.test.com/' + ''.join(random.choice(string.ascii_lowercase) for i in range(6))

    def randomIp(self):
        return str(random.randint(100,199)) + '.' + str(random.randint(100,199)) + '.' + str(random.randint(0,5)) + '.' + str(random.randint(0,5))

    def randomPort(self):
        return random.randint(999,9999)

    def randomID(self):
        return random.randint(99,9999)

    print('Test Start...')
    def setUp(self): 

#Basic Correctness Test
        self.answerDict_C = {}

        #Data for Test Case C1 - Correct IP Camera Test
        self.C1 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'ip': self.randomIp(), 'port': self.randomPort(),  'camera_id': 1}
        self.answerDict_C['C1'] = 200
        #Data for Test Case C2 - Correct Non IP Camera Test
        self.C2 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'url': self.randomUrl() , 'camera_id': self.randomID()}
        self.answerDict_C['C2'] = 200

#Missing Information Test
        self.answerDict_E = {}

        #Data for Test Case E1 - Wrong IP Camera Without IP Test
        self.E1 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'port': self.randomPort(),  'camera_id': self.randomID()}
        self.answerDict_E['E1'] = [ 404, AttributeError]

        #Data for Test Case E2 - Correct IP Camera Without PORT Test
        self.E2 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'ip': self.randomIp(), 'camera_id': self.randomID()}
        self.answerDict_E['E2'] = [ 200, 'None']

        #Data for Test Case E3 - Wrong Non IP Camera Without URL Test
        self.E3 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080,  'camera_id': self.randomID()}
        self.answerDict_E['E3'] = [ 404, AttributeError]

        #Data for Test Case E4 - Wrong Camera With URL and IP Test
        self.E4 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'url': self.randomUrl(), 'ip': self.randomIp(),  'camera_id': self.randomID()}
        self.answerDict_E['E4'] = [ 200, 'None']

        #Data for Test Case E5 - Wrong Camera Without URL and IP Test
        self.E5 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080,  'camera_id': self.randomID()}
        self.answerDict_E['E5'] = [ 404, AttributeError]

        #Data for Test Case E6 - Wrong Non IP Camera With URL and PORT Test
        self.E6 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'url': self.randomUrl(), 'port': self.randomPort(),  'camera_id': self.randomID()}
        self.answerDict_E['E6'] = [ 200, 'None']

        #Data for Test Case E7 - Wrong Camera With URL,  IP and PORT Test
        self.E7 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'url': self.randomUrl(), 'ip': self.randomIp(), 'port': self.randomPort(),  'camera_id': self.randomID()}
        self.answerDict_E['E7'] = [ 200, 'None']

        #Data for Test Case E8 - Wrong Camera Without ID Test
        self.E8 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'ip': self.randomIp(), 'port': self.randomPort()}
        self.answerDict_E['E8'] = [ 404, IntegrityError]

        #Data for Test Case E9 - Correct Camera Without city Test
        self.E9 = {'lat': 35.6895 , 'lng': 139.6917, 'country': 'JP', 'source': 'google', 'source_url': 'www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'ip': self.randomIp(), 'port': self.randomPort(),  'camera_id': self.randomID()}
        self.answerDict_E['E9'] = [ 200, 'None']

        #Data for Test Case E10 - Correct Camera Without state Test(Not US)
        self.E10 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'ip': self.randomIp(), 'port': self.randomPort(),  'camera_id': self.randomID()}
        self.answerDict_E['E10'] = [ 200, 'None']

        #Data for Test Case E11 - Wrong Camera Without Lag Test
        self.E11 = {'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'ip': self.randomIp(), 'port': self.randomPort(),  'camera_id': self.randomID()}
        self.answerDict_E['E11'] = [ 404, GDALException]

        #Data for Test Case E12 - Wrong Camera Without lng Test
        self.E12 = {'lat': 35.6895 , 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'ip': self.randomIp(), 'port': self.randomPort(),  'camera_id': self.randomID()}
        self.answerDict_E['E12'] = [ 404, GDALException]

        #Data for Test Case E13 - Wrong Camera Without source Test
        self.E13 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source_url': 'www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'ip': self.randomIp(), 'port': self.randomPort(),  'camera_id': self.randomID()}
        self.answerDict_E['E13'] = [ 404, IntegrityError]

        #Data for Test Case E14 - Wrong Camera Without source_url Test
        self.E14 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'ip': self.randomIp(), 'port': self.randomPort(),  'camera_id': self.randomID()}
        self.answerDict_E['E14'] = [ 404, IntegrityError]

#same ip and port
#Uniqueness Test
        self.answerDict_U = {}

    #Data for Test Case U1 - Wrong duplicated Camera ID Test
        self.U1 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'ip': self.randomIp(), 'port': self.randomPort(),  'camera_id': 8016}
        self.DU1 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'ip': self.randomIp(), 'port': self.randomPort(),  'camera_id': 8016}
        self.answerDict_U['U1'] = [200, 404, IntegrityError]

    #Data for Test Case U2 - Wrong duplicated URL Test
        self.U2 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'url': self.randomUrl(),  'camera_id': self.randomID()}
        self.DU2 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'url': self.randomUrl(),'camera_id': self.randomID()}
        self.answerDict_U['U2'] = [200, 404, IntegrityError]

    #Data for Test Case U3 - Wrong duplicated IP Test
        self.U3 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'ip': "192.168.1.3", 'port': self.randomPort(),  'camera_id': self.randomID()}
        self.DU3 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'ip': "192.168.1.3", 'port': self.randomPort(),  'camera_id': self.randomID()}
        self.answerDict_U['U3'] = [200, 404, IntegrityError]

    #Data for Test Case U4 - Wrong duplicated URL but different IP Test
        self.U4 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'ip': self.randomIp(), 'port': self.randomPort(), 'url': 'http://www.test456.com', 'camera_id': self.randomID()}
        self.DU4 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'ip': self.randomIp(), 'port': self.randomPort(), 'url': 'http://www.test456.com', 'camera_id': self.randomID()}
        self.answerDict_U['U4'] = [200, 404, IntegrityError]

    #Data for Test Case U5 - Wrong duplicated IP but different URL Test
        self.U5 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'ip': "192.168.1.7", 'port': self.randomPort(),  'url': self.randomUrl(), 'camera_id': self.randomID()}
        self.DU5 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'ip': "192.168.1.7", 'port': self.randomPort(), 'url': self.randomUrl(),  'camera_id': self.randomID()}
        self.answerDict_U['U5'] = [200, 404, IntegrityError]

         
#HTTP Status Code Test
    #Data for Test Case H1 - 200

    #Data for Test Case H2 - 201

    #Data for Test Case H3 - 404

    #Data for Test Case H4 - 404

    #Data for Test Case H5 - 404

    #Data for Test Case H6 - 404

    #Data for Test Case H7 - 500


#Information Syntex Test
        self.answerDict_I = {}

    #Data for Test Case I1 - Wrong 'lat' and 'lng' contains punctuation
        self.I1 = {'lat': '35.6895' , 'lng': 19.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'url': self.randomUrl(), 'camera_id': self.randomID()}
        self.answerDict_I['I1'] = [404, ValueError]
    #Data for Test Case I2 - Wrong 'lat' exceed limitation
        self.I2 = {'lat': 95.5837 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'url': self.randomUrl(), 'camera_id': self.randomID()}
        self.answerDict_I['I2'] = [404, ValueError]

    #Data for Test Case I3 - Wrong 'lng' exceed limitation
        self.I3 = {'lat': 35.6895 , 'lng': 190.3892, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'url': self.randomUrl(), 'camera_id': self.randomID()}
        self.answerDict_I['I3'] = [404, ValueError]

    #Data for Test Case I4 - Wrong city contains number
        self.I4 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku3', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'url': self.randomUrl(), 'camera_id': self.randomID()}
        self.answerDict_I['I4'] = [404, IntegrityError]

    #Data for Test Case I5 - Wrong source_url wrong form
        self.I5 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'url': self.randomUrl(), 'camera_id': self.randomID()}
        self.answerDict_I['I5'] = [404, IntegrityError]

    #Data for Test Case I6 - Wrong source_url wrong form
        self.I6 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com.cn', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'url': self.randomUrl(), 'camera_id': self.randomID()}
        self.answerDict_I['I6'] = [404, IntegrityError]

    #Data for Test Case I7 - Wrong source_url wrong form
        self.I7 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com/.cn/', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'url': self.randomUrl(), 'camera_id': self.randomID()}
        self.answerDict_I['I7'] = [404, IntegrityError]


    #Data for Test Case I8 - Correct is_video true/false
        self.I8 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': True, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'url': self.randomUrl(), 'camera_id': self.randomID()}
        self.answerDict_I['I8'] = [200, 'None']

    #Data for Test Case I9 - Correct is_video not 1 or 0
        self.I9 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 3, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'url': self.randomUrl(), 'camera_id': self.randomID()}
        self.answerDict_I['I9'] = [200, ValidationError]

    #Data for Test Case I10 - Wrong frame_rate not number
        self.I10 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': True, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'url': self.randomUrl(), 'camera_id': self.randomID()}
        self.answerDict_I['I10'] = [404, ValidationError]

    #Data for Test Case I11 - Wrong frame_rate not number 2
        self.I11 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 'c', 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'url': self.randomUrl(), 'camera_id': self.randomID()}
        self.answerDict_I['I11'] = [404, ValidationError]

    #Data for Test Case I12 - Wrong Indoor is 1 or 0
        self.I12 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': 1, 'indoors': 0, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'url': self.randomUrl(), 'camera_id': self.randomID()}
        self.answerDict_I['I12'] = [200, 'None']

    #Data for Test Case I13 - Wrong Indoor is char
        self.I13 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': 'Test', 'indoors': 'Test', 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'url': self.randomUrl(), 'camera_id': self.randomID()}
        self.answerDict_I['I13'] = [404, ValidationError]

    #Data for Test Case I14 - Correct Traffic
        self.I14 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': 0, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'url': self.randomUrl(), 'camera_id': self.randomID()}
        self.answerDict_I['I14'] = [200, 'None']

    #Data for Test Case I15 - Correct inactivite
        self.I15 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': 0, 'resolution_w': 1920, 'resolution_h': 1080, 'url': self.randomUrl(), 'camera_id': self.randomID()}
        self.answerDict_I['I15'] = [200, 'None']

    #Data for Test Case I16 - Wrong resolution 
        self.I16 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1000000, 'resolution_h': 10000000, 'ip': self.randomIp(), 'port': self.randomPort(),  'camera_id': self.randomID()}
        self.answerDict_I['I16'] = [404, IntegrityError]

    #Data for Test Case I17 - Wrong resolution
        self.I17 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 5, 'resolution_h': 5, 'ip': self.randomIp(), 'port': self.randomPort(),  'camera_id': self.randomID()}
        self.answerDict_I['I17'] = [404, IntegrityError]

    #Data for Test Case I18 - Wrong IP form
        self.I18 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'ip': "999.999.1.1", 'port': self.randomPort(),  'camera_id': self.randomID()}
        self.answerDict_I['I18'] = [404, DataError]

    #Data for Test Case I19 - Wrong IP form
        self.I19 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'ip': "1..", 'port': self.randomPort(),  'camera_id': self.randomID()}
        self.answerDict_I['I19'] = [404, DataError]

    #Data for Test Case I20 - Wrong IP form
        self.I20 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'ip': "192.c.1.1", 'port': self.randomPort(),  'camera_id': self.randomID()}
        self.answerDict_I['I20'] = [404, DataError]

    #Data for Test Case I21 - Wrong IP form
        self.I21 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'ip': "192.168.1", 'port': self.randomPort(),  'camera_id': self.randomID()}
        self.answerDict_I['I21'] = [404, DataError]

    #Data for Test Case I22 - Wrong IP form
        self.I22 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'ip': "192", 'port': self.randomPort(),  'camera_id': self.randomID()}
        self.answerDict_I['I22'] = [404, DataError]

    #Data for Test Case I23 - Wrong PORT 
        self.I23 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'ip': self.randomIp(), 'port': 800000,  'camera_id': self.randomID()}
        self.answerDict_I['I23'] = [404, IntegrityError]

    #Data for Test Case I24 - Wrong PORT
        self.I24 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'ip': self.randomIp(), 'port': 'c',  'camera_id': self.randomID()}
        self.answerDict_I['I24'] = [404, ValueError]

    #Data for Test Case I25 - Wrong ID
        self.I25 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'ip': self.randomIp(), 'port': self.randomPort(),  'camera_id': 'c'}
        self.answerDict_I['I25'] = [404, ValueError]

    #Data for Test Case I26 - Wrong ID
        self.I26 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'ip': self.randomIp(), 'port': self.randomPort(),  'camera_id': '.'}
        self.answerDict_I['I26'] = [404, ValueError]

    #Data for Test Case I27 - Wrong URL
        self.I27 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'url': 'http://www.test.com.cn', 'camera_id': self.randomID()}
        self.answerDict_I['I27'] = [404, IntegrityError]

    #Data for Test Case I28 - Wrong URL
        self.I28 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'url': 'http://www.test', 'camera_id': self.randomID()}
        self.answerDict_I['I28'] = [404, IntegrityError]

    #Data for Test Case I29 - Wrong URL
        self.I29 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'http://www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'url': 'www.test.com', 'camera_id': self.randomID()}
        self.answerDict_I['I29'] = [404, IntegrityError]


#Get Test
    #Data for Test Case N1 - Wrong Camera ID to get Test
        self.N1 = {'lat': 35.6895 , 'lng': 139.6917, 'city': 'Shinjuku-ku', 'country': 'JP', 'source': 'google', 'source_url': 'www.google.com', 'last_updated': '2016-04-15 07: 41: 52', 'description': 'This is a test camera', 'is_video': 1, 'framerate': 0.3, 'outdoors': True, 'indoors': False, 'traffic': False, 'inactive': False, 'resolution_w': 1920, 'resolution_h': 1080, 'ip': "192.168.1.1", 'port': self.randomPort(),  'camera_id': self.randomID()}


#Put Test


#Delete Test




#Advanced Information Conflict Test
    #Data for Test Case NL1 - Wrong location of 'lag' and 'lng'(In the Sea) Test

    #Data for Test Case NL2 - Wrong location of 'lag' and 'lng'(In the Sea) Test

    #Data for Test Case NL3 - Wrong Country mismatch with 'lag' and 'lng' Test

    #Data for Test Case NL4 - Wrong Country mismatch with 'lag' and 'lng' Test

    #Data for Test Case NL5 - Wrong City mismatch with 'lag' and 'lng' Test

    #Data for Test Case NL6 - Wrong City mismatch with 'lag' and 'lng' Test

    #Data for Test Case NL7 - Wrong unknown City with another same but wrong named City Test







#POST TEST

    #Basic Correctness Test
        #Data for Test Case C1 - Correct IP Camera Test
    def test_correct_IP_Camera(self):
            client = APIClient()
            response = self.client.post('/cameras.json/', self.C1, format = 'json')
            self.assertEqual(response.status_code, self.answerDict_C['C1'])

        #Data for Test Case C2 - Correct Non IP Camera Test
    def test_correct_Non_IP_Camera(self):
            client = APIClient()
            response = self.client.post('/cameras.json/', self.C2, format = 'json')
            self.assertEqual(response.status_code, self.answerDict_C['C2'])

    #Missing Information Test
        #Data for Test Case E1 - Wrong IP Camera Without IP Test
    def test_wrong_IP_Camera(self):
            client = APIClient()
            testName = 'E1'
            data = self.E1
            if self.answerDict_E[testName][1] == 'None':
                    response = self.client.post('/cameras.json/', data, format = 'json')
                    self.assertEqual(response.status_code, self.answerDict_E[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_E[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_E[testName][0])

        #Data for Test Case E2 - Correct IP Camera Without PORT Test
    def test_correct_IP_Camera(self):
            client = APIClient()
            testName = 'E2'
            data = self.E2
            if self.answerDict_E[testName][1] == 'None':
                    response = self.client.post('/cameras.json/', data, format = 'json')
                    self.assertEqual(response.status_code, self.answerDict_E[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_E[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_E[testName][0])

        #Data for Test Case E3 - Wrong Non IP Camera Without URL Test
    def test_wrong_Non_IP_Camera_Without_URL(self):
            client = APIClient()
            testName = 'E3'
            data = self.E3
            if self.answerDict_E[testName][1] == 'None':
                    response = self.client.post('/cameras.json/', data, format = 'json')
                    self.assertEqual(response.status_code, self.answerDict_E[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_E[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_E[testName][0])

        #Data for Test Case E4 - Wrong Camera With URL and IP Test
    def test_wrong_Camera_with_URL_and_IP(self):
            client = APIClient()
            testName = 'E4'
            data = self.E4
            if self.answerDict_E[testName][1] == 'None':
                    response = self.client.post('/cameras.json/', data, format = 'json')
                    self.assertEqual(response.status_code, self.answerDict_E[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_E[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_E[testName][0])

        #Data for Test Case E5 - Wrong Camera Without URL and IP Test
    def test_wrong_Camera_without_URL_and_IP(self):
            client = APIClient()
            testName = 'E5'
            data = self.E5
            if self.answerDict_E[testName][1] == 'None':
                    response = self.client.post('/cameras.json/', data, format = 'json')
                    self.assertEqual(response.status_code, self.answerDict_E[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_E[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_E[testName][0])

        #Data for Test Case E6 - Wrong Non IP Camera With URL and PORT Test
    def test_wrong_Non_IP_Camera_Without_URL_and_Port(self):
            client = APIClient()
            testName = 'E6'
            data = self.E6
            if self.answerDict_E[testName][1] == 'None':
                    response = self.client.post('/cameras.json/', data, format = 'json')
                    self.assertEqual(response.status_code, self.answerDict_E[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_E[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_E[testName][0])

        #Data for Test Case E7 - Wrong Camera With URL,  IP and PORT Test
    def test_wrong_camera_with_URL_IP_and_Port(self):
            client = APIClient()
            testName = 'E7'
            data = self.E7
            if self.answerDict_E[testName][1] == 'None':
                    response = self.client.post('/cameras.json/', data, format = 'json')
                    self.assertEqual(response.status_code, self.answerDict_E[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_E[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_E[testName][0])

        #Data for Test Case E8 - Wrong Camera Without ID Test
    def test_wrong_camera_without_ID(self):
            client = APIClient()
            testName = 'E8'
            data = self.E8
            if self.answerDict_E[testName][1] == 'None':
                    response = self.client.post('/cameras.json/', data, format = 'json')
                    self.assertEqual(response.status_code, self.answerDict_E[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_E[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_E[testName][0])

        #Data for Test Case E9 - Wrong Camera Without city Test
    def test_wrong_camera_without_city(self):
            client = APIClient()
            testName = 'E9'
            data = self.E9
            if self.answerDict_E[testName][1] == 'None':
                    response = self.client.post('/cameras.json/', data, format = 'json')
                    self.assertEqual(response.status_code, self.answerDict_E[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_E[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_E[testName][0])

        #Data for Test Case E10 - Correct Camera Without state Test
    def test_correct_camera_without_state(self):
            client = APIClient()
            testName = 'E10'
            data = self.E10
            if self.answerDict_E[testName][1] == 'None':
                    response = self.client.post('/cameras.json/', data, format = 'json')
                    self.assertEqual(response.status_code, self.answerDict_E[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_E[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_E[testName][0])

        #Data for Test Case E11 - Wrong Camera Without Lag Test
    def test_wrong_camera_without_Lag(self):
            client = APIClient()
            testName = 'E11'
            data = self.E11
            if self.answerDict_E[testName][1] == 'None':
                    response = self.client.post('/cameras.json/', data, format = 'json')
                    self.assertEqual(response.status_code, self.answerDict_E[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_E[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_E[testName][0])

        #Data for Test Case E12 - Wrong Camera Without lng Test
    def test_wrong_camera_without_lng(self):
            client = APIClient()
            testName = 'E12'
            data = self.E12
            if self.answerDict_E[testName][1] == 'None':
                    response = self.client.post('/cameras.json/', data, format = 'json')
                    self.assertEqual(response.status_code, self.answerDict_E[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_E[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_E[testName][0])

        #Data for Test Case E13 - Wrong Camera Without source Test
    def test_wrong_camera_without_source(self):
            client = APIClient()
            testName = 'E13'
            data = self.E13
            if self.answerDict_E[testName][1] == 'None':
                    response = self.client.post('/cameras.json/', data, format = 'json')
                    self.assertEqual(response.status_code, self.answerDict_E[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_E[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_E[testName][0])

        #Data for Test Case E14 - Wrong Camera Without source_url Test
    def test_wrong_camera_without_source_url(self):
            client = APIClient()
            testName = 'E14'
            data = self.E14
            if self.answerDict_E[testName][1] == 'None':
                    response = self.client.post('/cameras.json/', data, format = 'json')
                    self.assertEqual(response.status_code, self.answerDict_E[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_E[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_E[testName][0])


    #Uniqueness Test
        #Data for Test Case U1 - Wrong duplicated Camera ID Test
    def test_wrong_duplicate_camera_ID(self):
            client = APIClient()
            testName = 'U1'
            cmpName = 'DU1'
            testdata = self.U1
            cmpdata = self.DU1
            with transaction.atomic():
                response = self.client.post('/cameras.json/', testdata, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_U[testName][0])
                with self.assertRaises(self.answerDict_U[testName][2]):
                    response = self.client.post('/cameras.json/', cmpdata, format = 'json')
                    self.assertEqual(response.status_code, self.answerDict_U[testName][1])

        #Data for Test Case U2 - Wrong duplicated URL Test
    def test_wrong_duplicated_URL(self):
            client = APIClient()
            testName = 'U2'
            cmpName = 'DU2'
            testdata = self.U2
            cmpdata = self.DU2
            with transaction.atomic():
                response = self.client.post('/cameras.json/', testdata, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_U[testName][0])
                with self.assertRaises(self.answerDict_U[testName][2]):
                    response = self.client.post('/cameras.json/', cmpdata, format = 'json')
                    self.assertEqual(response.status_code, self.answerDict_U[testName][1])

        #Data for Test Case U3 - Wrong duplicated IP Test
    def test_wrong_duplicated_IP(self):
            client = APIClient()
            testName = 'U3'
            cmpName = 'DU3'
            testdata = self.U3
            cmpdata = self.DU3
            with transaction.atomic():
                response = self.client.post('/cameras.json/', testdata, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_U[testName][0])
                with self.assertRaises(self.answerDict_U[testName][2]):
                    response = self.client.post('/cameras.json/', cmpdata, format = 'json')
                    self.assertEqual(response.status_code, self.answerDict_U[testName][1])

        #Data for Test Case U4 - Wrong duplicated URL but different IP Test
    def test_wrong_duplicated_URL_but_different_IP(self):
            client = APIClient()
            testName = 'U3'
            cmpName = 'DU3'
            testdata = self.U3
            cmpdata = self.DU3
            with transaction.atomic():
                response = self.client.post('/cameras.json/', testdata, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_U[testName][0])
                with self.assertRaises(self.answerDict_U[testName][2]):
                    response = self.client.post('/cameras.json/', cmpdata, format = 'json')
                    self.assertEqual(response.status_code, self.answerDict_U[testName][1])

        #Data for Test Case U5 - Wrong duplicated IP but different URL Test
    def test_wrong_duplicated_IP_but_different_URL_test(self):
            client = APIClient()
            testName = 'U3'
            cmpName = 'DU3'
            testdata = self.U3
            cmpdata = self.DU3
            with transaction.atomic():
                response = self.client.post('/cameras.json/', testdata, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_U[testName][0])
                with self.assertRaises(self.answerDict_U[testName][2]):
                    response = self.client.post('/cameras.json/', cmpdata, format = 'json')
                    self.assertEqual(response.status_code, self.answerDict_U[testName][1])


    # Non Exist Camera Test
    #     Data for Test Case N1 - Wrong Camera ID to get Test
    def test_wrong_duplicated_IP_but_different_URL_test(self):
            client = APIClient()
            testName = 'U3'
            cmpName = 'DU3'
            testdata = self.U3
            cmpdata = self.DU3
            with transaction.atomic():
                response = self.client.post('/cameras.json/', testdata, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_U[testName][0])
                with self.assertRaises(self.answerDict_U[testName][2]):
                    response = self.client.post('/cameras.json/', cmpdata, format = 'json')
                    self.assertEqual(response.status_code, self.answerDict_U[testName][1])


    
    # HTTP Status Code Test
    #     Data for Test Case H1 - 200
    #     Data for Test Case H2 - 201
    #     Data for Test Case H3 - 404
    #     Data for Test Case H4 - 404
    #     Data for Test Case H5 - 404
    #     Data for Test Case H6 - 404
    #     Data for Test Case H7 - 500

    # Information Syntex Test
    #     Data for Test Case I1 - Wrong 'lat' and 'lng' contains punctuation
    def test_wrong_lat_and_lng_punctuation(self):
            client = APIClient()
            testName = 'I1'
            data = self.I1
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0])

    #     Data for Test Case I2 - Wrong 'lng' exceed lmites
    def test_wrong_lng_exceed_limites(self):
            client = APIClient()
            testName = 'I2'
            data = self.I2
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0])

    #     Data for Test Case I3 - Wrong 'lat' exceed limites
    def test_wrong_lat_exceed_limites(self):
            client = APIClient()
            testName = 'I3'
            data = self.I3
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0])


    #     Data for Test Case I4 - Wrong city contains number
    def test_wrong_city_number(self):
            client = APIClient()
            testName = 'I4'
            data = self.I4
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0])

    #     Data for Test Case I5 - Wrong source_url wrong form
    def test_wrong_source_url_wrong_form1(self):
            client = APIClient()
            testName = 'I5'
            data = self.I5
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0])

    #     Data for Test Case I6 - Wrong source_url wrong form
    def test_wrong_source_url_wrong_form2(self):
            client = APIClient()
            testName = 'I6'
            data = self.I6
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0])

    #     Data for Test Case I7 - Wrong source_url wrong form
    def test_wrong_source_url_wrong_form3(self):
            client = APIClient()
            testName = 'I7'
            data = self.I7
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0])

    #     Data for Test Case I8 - Wrong is_video true/false
    def test_wrong_is_video_true_false(self):
            client = APIClient()
            testName = 'I8'
            data = self.I8
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0])

    #     Data for Test Case I9 - Wrong is_video not 1 or 0
    def test_wrong_is_video_not_1_or_0(self):
            client = APIClient()
            testName = 'I9'
            data = self.I9
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0])

    #     Data for Test Case I10 - Wrong frame_rate not number
    def test_wrong_frame_rate_not_number(self):
            client = APIClient()
            testName = 'I10'
            data = self.I10
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0])

    #     Data for Test Case I11 - Wrong frame_rate not number 2
    def test_wrong_frame_rate_not_number_2(self):
            client = APIClient()
            testName = 'I11'
            data = self.I11
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0])

    #     Data for Test Case I12 - Wrong Indoor is 1 or 0
    def test_wrong_indoor_is_1_or_0(self):
            client = APIClient()
            testName = 'I12'
            data = self.I12
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0])

    #     Data for Test Case I13 - Wrong Indoor is char
    def test_wrong_Indoor_is_char(self):
            client = APIClient()
            testName = 'I13'
            data = self.I13
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0])

    #     Data for Test Case I14 - Wrong Traffic
    def test_wrong_traffic(self):
            client = APIClient()
            testName = 'I14'
            data = self.I14
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0])

    #     Data for Test Case I15 - Wrong inactivite
    def test_wrong_inactivite(self):
            client = APIClient()
            testName = 'I15'
            data = self.I15
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0])

    #     Data for Test Case I16 - Wrong resolution
    def test_wrong_resolution(self):
            client = APIClient()
            testName = 'I16'
            data = self.I16
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0])

    #     Data for Test Case I17 - Wrong resolution
    def test_wrong_resolution(self):
            client = APIClient()
            testName = 'I17'
            data = self.I17
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0])

    #     Data for Test Case I18 - Wrong IP form
    def test_wrong_IP_form1(self):
            client = APIClient()
            testName = 'I18'
            data = self.I18
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0])

    #     Data for Test Case I19 - Wrong IP form
    def test_wrong_IP_form3(self):
            client = APIClient()
            testName = 'I19'
            data = self.I19
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0])

    #     Data for Test Case I20 - Wrong IP form
    def test_wrong_IP_form3(self):
            client = APIClient()
            testName = 'I20'
            data = self.I20
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0])

    #     Data for Test Case I21 - Wrong IP form
    def test_wrong_IP_form4(self):
            client = APIClient()
            testName = 'I21'
            data = self.I21
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0])

    #     Data for Test Case I22 - Wrong IP form
    def test_wrong_IP_form5(self):
            client = APIClient()
            testName = 'I22'
            data = self.I22
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0])

    #     Data for Test Case I23 - Wrong PORT
    def test_wrong_port1(self):
            client = APIClient()
            testName = 'I23'
            data = self.I23
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0]) 


    #     Data for Test Case I24 - Wrong PORT
    def test_wrong_port2(self):
            client = APIClient()
            testName = 'I24'
            data = self.I24
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0]) 

    #     Data for Test Case I25 - Wrong ID
    def test_wrong_ID1(self):
            client = APIClient()
            testName = 'I25'
            data = self.I25
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0]) 

    #     Data for Test Case I26 - Wrong ID
    def test_wrong_ID2(self):
            client = APIClient()
            testName = 'I26'
            data = self.I26
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0]) 

    #     Data for Test Case I27 - Wrong URL
    def test_wrong_URL1(self):
            client = APIClient()
            testName = 'I27'
            data = self.I27
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0]) 


    #     Data for Test Case I28 - Wrong URL
    def test_wrong_URL2(self):
            client = APIClient()
            testName = 'I28'
            data = self.I28
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0]) 

    #     Data for Test Case I29 - Wrong URL
    def test_wrong_URL3(self):
            client = APIClient()
            testName = 'I29'
            data = self.I29
            if self.answerDict_I[testName][1] == 'None':
                response = self.client.post('/cameras.json/', data, format = 'json')
                self.assertEqual(response.status_code, self.answerDict_I[testName][0])
            else:
                with transaction.atomic():
                    with self.assertRaises(self.answerDict_I[testName][1]):
                        response = self.client.post('/cameras.json/', data, format = 'json')
                        self.assertEqual(response.status_code, self.answerDict_I[testName][0]) 

    # Advanced Information Conflict Test
    #     Data for Test Case NL1 - Wrong location of 'lag' and 'lng'(In the Sea) Test
    #     Data for Test Case NL2 - Wrong location of 'lag' and 'lng'(In the Sea) Test
    #     Data for Test Case NL3 - Wrong Country mismatch with 'lag' and 'lng' Test
    #     Data for Test Case NL4 - Wrong Country mismatch with 'lag' and 'lng' Test
    #     Data for Test Case NL5 - Wrong City mismatch with 'lag' and 'lng' Test
    #     Data for Test Case NL6 - Wrong City mismatch with 'lag' and 'lng' Test
    #     Data for Test Case NL7 - Wrong unknown City with another same but wrong named City Test

