from django.test import TestCase
from django.db import IntegrityError
from django.db import transaction
from django.contrib.gis.gdal.error import GDALException
from django.core.management.base import BaseCommand
from CAM2API.models import Camera,  Non_IP,  IP, Application
from django.contrib.gis.geos import GEOSGeometry
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.reverse import reverse
from psycopg2 import DataError
from django.db.utils import DataError
from django.core.exceptions import ValidationError
from random import randint
from CAM2API.utils import jwt_app_payload_handler, jwt_encode_handler
from django.utils import timezone
import random
import string
import json
import os
import requests
import datetime


class CAM2APITest(APITestCase):
    '''Class containing general functions used in other test classes'''

    def setUp(self):
        self.ip_camera = {'lat': 35.6895, 'lng': 139.6917, 'ip': '10.0.0.1',
                          'camera_id': 1}
        self.non_ip_camera = {'lat': 35.6895 , 'lng': 139.6917,
                              'url': 'https://www.google.com/', 'camera_id': 2}
        self.client = APIClient()
        Application.objects.create_app({"app_name":'ImageCore', 
            "permission_level":'Admin'})
        app = Application.objects.get(app_name='ImageCore')
        payload = jwt_app_payload_handler(app)
        token = jwt_encode_handler(payload)
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + token)

    def send_post_request(self, url, data):
        response = self.client.post(url, data, format='json')
        return response

    def send_get_request(self, url):
        response = self.client.get(url)
        return response

    def send_delete_request(self, url):
        response = self.client.delete(url)
        return response

class AddingNewCameraTests(CAM2APITest):
    '''Tests of adding new camera'''

    def test_post_IPCamera_Accepted(self):
        response = self.send_post_request('/cameras/', self.ip_camera)
        self.assertEqual(response.status_code, requests.codes.created)

    def test_post_NonIPCamera_Accepted(self):
        response = self.send_post_request('/cameras/', self.non_ip_camera)
        self.assertEqual(response.status_code, requests.codes.created)

    def test_post_IPCameraMissingIP_Rejected(self):
        del self.ip_camera['ip']
        response = self.send_post_request('/cameras/', self.ip_camera)
        self.assertEqual(response.status_code, requests.codes.bad_request)

    def test_post_NonIPCameraMissingURL_Rejected(self):
        del self.non_ip_camera['url']
        response = self.send_post_request('/cameras/', self.non_ip_camera)
        self.assertEqual(response.status_code, requests.codes.bad_request)

    def test_post_IPCameraMissingID_Rejected(self):
        del self.ip_camera['camera_id']
        response = self.send_post_request('/cameras/', self.ip_camera)
        self.assertEqual(response.status_code, requests.codes.bad_request)

    def test_post_MissingLatitude_Rejected(self):
        del self.ip_camera['lat']
        response = self.send_post_request('/cameras/', self.ip_camera)
        self.assertEqual(response.status_code, requests.codes.bad_request)

    def test_post_MissingLongitude_Rejected(self):
        del self.ip_camera['lng']
        response = self.send_post_request('/cameras/', self.ip_camera)
        self.assertEqual(response.status_code, requests.codes.bad_request)

    def test_post_WrongCityCorrection_Accepted(self):
        self.ip_camera['city'] = 'IncorrectCity'
        response = self.send_post_request('/cameras/', self.ip_camera)
        self.assertEqual(response.status_code, requests.codes.created)
        added_camera = Camera.objects.get(camera_id=self.ip_camera['camera_id'])
        self.assertEqual(added_camera.city, 'Shinjuku-ku')

    def test_post_MissingCityCantBeDetected_Accepted(self):
        self.ip_camera['lat'] = 30.0443
        self.ip_camera['lng'] = 31.34
        response = self.send_post_request('/cameras/', self.ip_camera)
        self.assertEqual(response.status_code, requests.codes.created)
        city = Camera.objects.get(camera_id=self.ip_camera['camera_id']).city
        self.assertEqual(city, None)

    def test_post_CountryDetection_Accepted(self):
        self.ip_camera['lat'] = 30.0443
        self.ip_camera['lng'] = 31.34
        response = self.send_post_request('/cameras/', self.ip_camera)
        country = Camera.objects.get(lat=self.ip_camera['lat']).country
        self.assertEqual(country, 'Egypt')

    def test_post_StateDetection_Accepted(self):
        self.ip_camera['lat'] = 40.4259
        self.ip_camera['lng'] = -86.9081
        response = self.send_post_request('/cameras/', self.ip_camera)
        state = Camera.objects.get(lat=self.ip_camera['lat']).state
        self.assertEqual(state, 'IN')

    def test_post_DuplicateCameraID_Rejected(self):
        response = self.send_post_request('/cameras/', self.ip_camera)
        self.ip_camera['ip'] = '10.0.0.2'
        response = self.send_post_request('/cameras/', self.ip_camera)
        self.assertEqual(response.status_code, requests.codes.bad_request)

    def test_post_DuplicateIP_Rejected(self):
        response = self.send_post_request('/cameras/', self.ip_camera)
        self.ip_camera['camera_id'] = 11
        response = self.send_post_request('/cameras/', self.ip_camera)
        self.assertEqual(response.status_code, requests.codes.bad_request)

    def test_post_DuplicateURL_Rejected(self):
        response = self.send_post_request('/cameras/', self.ip_camera)
        self.non_ip_camera['camera_id'] = 11
        response = self.send_post_request('/cameras/', self.ip_camera)
        self.assertEqual(response.status_code, requests.codes.bad_request)

    def test_post_DefaultPort80_Accepted(self):
        response = self.send_post_request('/cameras/', self.ip_camera)
        port = Camera.objects.get(
            camera_id=self.ip_camera['camera_id']).retrieval_model.port
        self.assertEqual(port, 80)

class ValidatingDatainNewCameraTests(CAM2APITest):
    '''Testing validation of the data in new cameras'''

    def test_validate_CameraIDStringNotInt_Rejected(self):
        self.ip_camera['camera_id'] = 'incorrect_id'
        response = self.send_post_request('/cameras/', self.ip_camera)
        self.assertEqual(response.status_code, requests.codes.bad_request)

    def test_validate_SourceExceedsMaxLength_Rejected(self):
        self.ip_camera['source'] = ''.join(['a'] * 101)
        response = self.send_post_request('/cameras/', self.ip_camera)
        self.assertEqual(response.status_code, requests.codes.bad_request)

    def test_validate_IsVideoNotBoolean_Rejected(self):
        self.ip_camera['is_video'] = 'NotBooleanValue'
        response = self.send_post_request('/cameras/', self.ip_camera)
        self.assertEqual(response.status_code, requests.codes.bad_request)

    def test_validate_LatitudeExceedsLimits_Rejected(self):
        self.ip_camera['lat'] = 91
        response = self.send_post_request('/cameras/', self.ip_camera)
        self.assertEqual(response.status_code, requests.codes.bad_request)

    def test_validate_LongitudeExceedsLimits_Rejected(self):
        self.ip_camera['lng'] = -181
        response = self.send_post_request('/cameras/', self.ip_camera)
        self.assertEqual(response.status_code, requests.codes.bad_request)

    def test_validate_NegativeResolutionField_Rejected(self):
        self.ip_camera['resolution_w'] = -1
        response = self.send_post_request('/cameras/', self.ip_camera)
        self.assertEqual(response.status_code, requests.codes.bad_request)

    def test_validate_IncorrectIP_Rejected(self):
        self.ip_camera['ip'] = 'incorrect_ip'
        response = self.send_post_request('/cameras/', self.ip_camera)
        self.assertEqual(response.status_code, requests.codes.bad_request)

    def test_validate_IncorrectURL_Rejected(self):
        self.non_ip_camera['url'] = 'incorrect_url'
        response = self.send_post_request('/cameras/', self.non_ip_camera)
        self.assertEqual(response.status_code, requests.codes.bad_request)

    def test_validate_IPCameraAllFieldsCorrectlySpecified_Accepted(self):
        perfect_ip_camera = {'lat':40.4259 ,'lng':-86.9081,
                             'city':'West Lafayette','country': 'USA',
                             'source':'google','source_url':'www.google.com',
                             'description':'This is a test camera',
                             'is_video': True,'framerate': 0.3,
                             'outdoors': True,'indoors': False,'traffic': False,
                             'inactive': False,'resolution_w': 1920,
                             'resolution_h': 1080,'ip':"192.168.1.1",'port':22,
                             'camera_id':8000}
        response = self.send_post_request('/cameras/', perfect_ip_camera)
        self.assertEqual(response.status_code, requests.codes.created)

    def test_validate_NonIPCameraAllFieldsCorrectlySpecified_Accepted(self):
        perfect_non_ip_camera = {'lat':40.4259 ,'lng':-86.9081,
                             'city':'West Lafayette','country': 'USA',
                             'source':'google','source_url':'www.google.com',
                             'description':'This is a test camera',
                             'is_video': True,'framerate': 0.3,
                             'outdoors': True,'indoors': False,'traffic': False,
                             'inactive': False,'resolution_w': 1920,
                             'resolution_h': 1080,'url':"https://www.url.com",
                             'camera_id':8000}
        response = self.send_post_request('/cameras/', perfect_non_ip_camera)
        self.assertEqual(response.status_code, requests.codes.created)

class QueryingCameras(CAM2APITest):
    '''Test all possible ways of querying the data'''

    def setUp(self):
        super().setUp()
        camera_wl = {'lat': 40.4259, 'lng': -86.9081, 'ip': '10.0.0.2',
                          'camera_id': 2}
        camera_chi = {'lat': 41.8781, 'lng': -87.6298, 'ip': '10.0.0.3',
                          'camera_id': 3}
        camera_lnd = {'lat': 51.5085 , 'lng': -0.0761,
                              'url': 'https://www.google.com/4', 'camera_id': 4}
        camera_ist = {'lat': 41.0514 , 'lng': 28.9795, 'city': 'Istanbul',
                              'url': 'https://www.google.com/5', 'camera_id': 5}
        cameras = [camera_wl, camera_chi, camera_lnd, camera_ist]
        for camera in cameras:
            self.send_post_request('/cameras/', camera)

    def test_get_HomePage_Responds(self):
        response = self.send_get_request('/')
        self.assertEqual(response.status_code, requests.codes.ok)

    def test_get_QueryCameraByID_Queries(self):
        response = self.send_get_request('/2/')
        self.assertEqual(response.status_code, requests.codes.ok)
        self.assertEqual(response.data.get('city'), 'West Lafayette')

    def test_get_AllCamerasInDb_Queries(self):
        response = self.send_get_request('/cameras/')
        self.assertEqual(response.status_code, requests.codes.ok)
        self.assertEqual(len(response.data), 4)

    def test_get_AllCamerasInDbFilteredByCountry_Queries(self):
        response = self.send_get_request('/cameras/?country=USA')
        self.assertEqual(len(response.data), 2)

    def test_get_AllCamerasInDbFilteredByLatitudeRange_Queries(self):
        response = self.send_get_request('/cameras/?lat_min=40.9&lat_max=90')
        self.assertEqual(len(response.data), 3)

    def test_get_QueryByRadius_Queries(self):
        response = self.send_get_request('/query/lat=40.42,lng=-86,radius=600/')
        self.assertEqual(response.status_code, requests.codes.ok)
        self.assertEqual(len(response.data), 2)
        cities = [response.data[i]['city'] for i in range(len(response.data))]
        self.assertTrue('West Lafayette' in cities and 'Chicago' in cities)

    def test_get_QueryByCount_Queries(self):
        response = self.send_get_request('/query/lat=41,lng=28,count=2/')
        self.assertEqual(response.status_code, requests.codes.ok)
        self.assertEqual(len(response.data), 2)
        cities = [response.data[i]['city'] for i in range(len(response.data))]
        self.assertTrue('Istanbul' in cities and 'London' in cities)

    def test_get_QueryByCountWhichExceedsNumberOfResults_Queries(self):
        response = self.send_get_request('/query/lat=41,lng=28,count=100/')
        self.assertEqual(response.status_code, requests.codes.ok)
        self.assertEqual(len(response.data), 4)

class DeletingCameras(CAM2APITest):
    '''Testing deleting camera by its camera_id'''

    def test_delete_DeletingExistingCamera_Successful(self):
        response = self.send_post_request('/cameras/', self.non_ip_camera)
        response = self.send_delete_request('/2/')
        self.assertEqual(response.status_code, requests.codes.ok)
        self.assertEqual(len(Camera.objects.all()), 0)

    def test_delete_DeletingNonExistingCamera_Unsuccessful(self):
        response = self.send_delete_request('/100/')
        self.assertEqual(response.status_code, requests.codes.not_found)



class AuthTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        Application.objects.create_app({'app_name': 'ImageCore', 
                                     'permission_level': 'Basic'})

    def test_register_app(self):
        self.client.credentials(HTTP_AUTHORIZATION='Basic ' + 'CAM2API')
        response = self.client.post('/register_app/', {'app_name': 'ImageCore' + str(randint(0,100)), 'permission_level':'Basic'}, format='json')
        self.assertEqual(response.status_code, requests.codes.created)

    def test_register_app_with_wrong_permission_level(self):
        self.client.credentials(HTTP_AUTHORIZATION='Basic ' + 'CAM2API')
        response = self.client.post('/register_app/', {'app_name': 'ImageCore' + str(randint(0,100)), 'permission_level':'Basics'}, format='json')
        self.assertEqual(response.status_code, requests.codes.bad_request)

    def test_register_app_without_basic_auth(self):
        response = self.client.post('/register_app/', {'app_name': 'ImageCore' + str(randint(0,100)), 'permission_level':'Basic'}, format='json')
        self.assertEqual(response.status_code, requests.codes.forbidden)        

    def test_obtain_token(self):
        app = Application.objects.get(app_name='ImageCore')
        client_id = app.client_id
        client_secret = app.client_secret
        response = self.client.post('/token/', {'client_id': client_id, 'client_secret': client_secret}, format='json')
        self.assertEqual(response.status_code, requests.codes.created)

    def test_obtain_token_with_wrong_client_secret(self):
        app = Application.objects.get(app_name='ImageCore')
        client_id = app.client_id
        client_secret = 'wrong'
        response = self.client.post('/token/', {'client_id': client_id, 'client_secret': client_secret}, format='json')
        self.assertEqual(response.status_code, requests.codes.bad_request)        

    def test_auth_view(self):
        app = Application.objects.get(app_name='ImageCore')
        payload = jwt_app_payload_handler(app)
        token = jwt_encode_handler(payload)
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        response = self.client.get('/cameras/', format='json')
        self.assertEqual(response.status_code, requests.codes.ok) 

    def test_signature_expire(self):
        app = Application.objects.get(app_name='ImageCore')
        payload = jwt_app_payload_handler(app)
        payload['exp'] = timezone.now() - datetime.timedelta(seconds=6000)
        token = jwt_encode_handler(payload)        
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        response = self.client.get('/cameras/', format='json')
        self.assertEqual(response.status_code, requests.codes.forbidden)
