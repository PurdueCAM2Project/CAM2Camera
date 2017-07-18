from rest_framework.test import APIClient
from django.test import TestCase
from random import randint
from CAM2API.models import Application
from CAM2API.utils import jwt_app_payload_handler, jwt_encode_handler
from django.utils import timezone 
import datetime

class AuthTest(TestCase):
	def setUp(self):
		self.client = APIClient()
		Application.objects.create_app({'app_name': 'ImageCore', 'permission_level': 'Basic'})

	def test_register_app(self):
		self.client.credentials(HTTP_AUTHORIZATION='Basic ' + 'CAM2API')
		response = self.client.post('/register_app/', {'app_name': 'ImageCore' + str(randint(0,100)), 'permission_level':'Basic'}, format='json')
		self.assertEqual(response.status_code, 201)

	def test_register_app_with_wrong_permission_level(self):
		self.client.credentials(HTTP_AUTHORIZATION='Basic ' + 'CAM2API')
		response = self.client.post('/register_app/', {'app_name': 'ImageCore' + str(randint(0,100)), 'permission_level':'Basics'}, format='json')
		self.assertEqual(response.status_code, 400)

	def test_register_app_without_basic_auth(self):
		response = self.client.post('/register_app/', {'app_name': 'ImageCore' + str(randint(0,100)), 'permission_level':'Basic'}, format='json')
		self.assertEqual(response.status_code, 403)		

	def test_obtain_token(self):
		app = Application.objects.get(app_name='ImageCore')
		client_id = app.client_id
		client_secret = app.client_secret
		response = self.client.post('/token/', {'client_id': client_id, 'client_secret': client_secret}, format='json')
		self.assertEqual(response.status_code, 201)

	def test_obtain_token_with_wrong_client_secret(self):
		app = Application.objects.get(app_name='ImageCore')
		client_id = app.client_id
		client_secret = 'wrong'
		response = self.client.post('/token/', {'client_id': client_id, 'client_secret': client_secret}, format='json')
		self.assertEqual(response.status_code, 400)		

	def test_auth_view(self):
		app = Application.objects.get(app_name='ImageCore')
		payload = jwt_app_payload_handler(app)
		token = jwt_encode_handler(payload)
		self.client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
		response = self.client.get('/cameras/', format='json')
		self.assertEqual(response.status_code, 200) 
		
	def test_signature_expire(self):
		app = Application.objects.get(app_name='ImageCore')
		payload = jwt_app_payload_handler(app)
		payload['exp'] = timezone.now() - datetime.timedelta(seconds=3000)
		token = jwt_encode_handler(payload)		
		self.client.credentials(HTTP_AUTHORIZATION='JWT' + token)
		response = self.client.get('/cameras/', format='json')
		print(response.status_text)
		print(response.data)
		self.assertEqual(response.status_code, 400)