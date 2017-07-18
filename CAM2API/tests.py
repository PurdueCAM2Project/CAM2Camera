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
import requests

class CAM2APITest(APITestCase):
    '''Class containing general functions used in other test classes'''

    def setUp(self):
        self.ip_camera = {'lat': 35.6895, 'lng': 139.6917, 'ip': '10.0.0.1',
                          'camera_id': 1}
        self.non_ip_camera = {'lat': 35.6895 , 'lng': 139.6917,
                              'url': 'https://www.google.com/', 'camera_id': 2}

    def send_post_request(self, url, data):
        response = self.client.post(url, data, format='json')
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


