import jwt
import uuid 
import datetime 

from calendar import timegm
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.models import User
from django.utils import timezone 
from django.conf import settings
from CAM2API.models import Application



def jwt_payload_handler(user):
	username = user.username
	if isinstance(user.pk, uuid.UUID):
		user.pk = str(user.pk)
	payload = {
			'user_id' : user.pk,
			'username' : user.username,
			'exp' : timezone.now() + datetime.timedelta(seconds=3000) 
	}
	if hasattr(user, 'email'):
		payload['email'] = user.email
	
	payload['admin'] = user.is_superuser

	payload['aud'] = 'CAM2Web'
	payload['iss'] = 'CAM2API'

	return payload

def jwt_app_payload_handler(app):
	"""
	Create the payload of the JSON Web Token including:
		client_id,
		client_secret,
		expiration time,
		permission level,
		audience,
		issuer
	input app: application object
	return: dict of payload 
	"""
	client_id = app.client_id
	client_secret = app.client_secret
	permission_level = app.permission_level
	orig_iat = timegm(datetime.datetime.utcnow().utctimetuple())

	payload = {
		'id': client_id,
		'secret': client_secret,
		'exp': timezone.now() + datetime.timedelta(seconds=3600),
		'level': permission_level,
		'aud': 'CAM2Web',
		'iss': 'localhost',
		'orig_iat': orig_iat
	}
	print(orig_iat)
	return payload

def jwt_encode_handler(payload):
	"""
	Encode the payload with SECRET_KEY
	input payload: payload of the JSON Web Token
	return: byte of token
	"""
	key = settings.SECRET_KEY
	return jwt.encode(
			payload,
			key,
			api_settings.JWT_ALGORITHM,
		).decode('utf-8')

def jwt_decode_handler(token, verify_exp):
	"""
	Decode the payload with SECRET_KEY
	input token: byte of JSON Web Token
	return: payload
	"""

	key = settings.SECRET_KEY
	options = {"verify_exp": verify_exp, "verify_aud": True, "verify_iss": True}
	return jwt.decode(token, key, True, options=options, audience='CAM2Web', issuer='localhost', algorithms='HS256')