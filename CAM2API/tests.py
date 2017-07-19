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

class API_View_Tests(APITestCase):

    def setUp(self):

        self.ip_camera = {'lat': 35.6895, 'lng': 139.6917, 'ip': '10.0.0.1',
                          'camera_id': 1}
        self.non_ip_camera = {'lat': 35.6895 , 'lng': 139.6917,
                              'url': 'https://www.google.com/', 'camera_id': 2}

    def test_post_IPCamera_Accepted(self):
        response = self.client.post('/cameras/', self.ip_camera, format='json')
        self.assertEqual(response.status_code, requests.codes.created)

    def test_post_NonIPCamera_Accepted(self):
        response = self.client.post('/cameras/', self.non_ip_camera,
                                    format='json')
        self.assertEqual(response.status_code, requests.codes.created)

    def test_post_IPCameraMissingIP_Rejected(self):
        del self.ip_camera['ip']
        response = self.client.post('/cameras/', self.ip_camera, format='json')
        self.assertEqual(response.status_code, requests.codes.bad_request)

    def test_post_NonIPCameraMissingURL_Rejected(self):
        del self.non_ip_camera['url']
        response = self.client.post('/cameras/', self.non_ip_camera,
                                    format='json')
        self.assertEqual(response.status_code, requests.codes.bad_request)

    def test_post_IPCameraMissingID_Rejected(self):
        del self.ip_camera['camera_id']
        response = self.client.post('/cameras/', self.ip_camera, format='json')
        self.assertEqual(response.status_code, requests.codes.bad_request)

    def test_post_MissingLatitude_Rejected(self):
        del self.ip_camera['lat']
        response = self.client.post('/cameras/', self.ip_camera, format='json')
        self.assertEqual(response.status_code, requests.codes.bad_request)

    def test_post_MissingLongitude_Rejected(self):
        del self.ip_camera['lng']
        response = self.client.post('/cameras/', self.ip_camera, format='json')
        self.assertEqual(response.status_code, requests.codes.bad_request)

    def test_post_WrongCityCorrection_Accepted(self):
        self.ip_camera['city'] = 'IncorrectCity'
        response = self.client.post('/cameras/', self.ip_camera, format='json')
        self.assertEqual(response.status_code, requests.codes.created)
        added_camera = Camera.objects.get(camera_id=self.ip_camera['camera_id'])
        self.assertEqual(added_camera.city, 'Shinjuku-ku')

    def test_post_MissingCityCantBeDetected_Accepted(self):
        self.ip_camera['lat'] = 30.0443
        self.ip_camera['lng'] = 31.34
        response = self.client.post('/cameras/', self.ip_camera, format='json')
        self.assertEqual(response.status_code, requests.codes.created)
        city = Camera.objects.get(camera_id=self.ip_camera['camera_id']).city
        self.assertEqual(city, None)

    def test_post_CountryDetection_Accepted(self):
        self.ip_camera['lat'] = 30.0443
        self.ip_camera['lng'] = 31.34
        response = self.client.post('/cameras/', self.ip_camera, format='json')
        country = Camera.objects.get(lat=self.ip_camera['lat']).country
        self.assertEqual(country, 'Egypt')

    def test_post_StateDetection_Accepted(self):
        self.ip_camera['lat'] = 40.4259
        self.ip_camera['lng'] = -86.9081
        response = self.client.post('/cameras/', self.ip_camera, format='json')
        state = Camera.objects.get(lat=self.ip_camera['lat']).state
        self.assertEqual(state, 'IN')

    def test_post_DuplicateCameraID_Rejected(self):
        response = self.client.post('/cameras/', self.ip_camera, format='json')
        self.ip_camera['ip'] = '10.0.0.2'
        response = self.client.post('/cameras/', self.ip_camera, format='json')
        self.assertEqual(response.status_code, requests.codes.bad_request)

    def test_post_DuplicateIP_Rejected(self):
        response = self.client.post('/cameras/', self.ip_camera, format='json')
        self.ip_camera['camera_id'] = 11
        response = self.client.post('/cameras/', self.ip_camera, format='json')
        self.assertEqual(response.status_code, requests.codes.bad_request)

    def test_post_DuplicateURL_Rejected(self):
        response = self.client.post('/cameras/', self.ip_camera, format='json')
        self.non_ip_camera['camera_id'] = 11
        response = self.client.post('/cameras/', self.ip_camera, format='json')
        self.assertEqual(response.status_code, requests.codes.bad_request)

    def test_post_LatitudeExceedsLimits_Rejected(self):
        self.ip_camera['lat'] = 91
        response = self.client.post('/cameras/', self.ip_camera, format='json')
        self.assertEqual(response.status_code, requests.codes.bad_request)

    def test_post_LongitudeExceedsLimits_Rejected(self):
        self.ip_camera['lng'] = -181
        response = self.client.post('/cameras/', self.ip_camera, format='json')
        self.assertEqual(response.status_code, requests.codes.bad_request)
