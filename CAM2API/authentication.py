
from rest_framework import exceptions, HTTP_HEADER_ENCODING
from django.utils.six import text_type
from rest_framework.authentication import TokenAuthentication, BaseAuthentication
from django.contrib.auth.models import User 
from CAM2API.models import RegisterUser, Application

import datetime 
from django.utils import timezone

from rest_framework_jwt.settings import api_settings
from CAM2API.utils import jwt_decode_handler
import jwt


def get_authorization_header(request):
	auth = request.META.get('HTTP_AUTHORIZATION',None)
	if auth:
		if isinstance(auth, text_type):
			auth = auth.encode(HTTP_HEADER_ENCODING)
	return auth


class AccountTokenAuthentication(TokenAuthentication):
	def get_model(self):
		if self.model is not None:
			return self.model
		else:
			from CAM2API.token import Token
			return Token 

	'''
	Request.auth -> self._authenticate() -> authenticator(CAM2APIAccountTokenAuthentication) -> authenticate -> authenticate_credentials -> return(Nonn/user, object/token)
	'''

	def authenticate_credentials(self, key):
		print("Authenticating")
		model = self.get_model()

		try:
			token = model.objects.get(key=key)
		except model.DoesNotExist:
			raise exceptions.AuthenticationFailed('Invalid Token')

		#counter feature(potentially could be used later as seesion token)


		token_access_times = token.access_times + 1
		token.access_times = token_access_times
		token.save()

		if token_access_times > 10000:
			token.delete()
			raise exceptions.AuthenticationFailed('Token has hit its limit')
		
		#expiring feature(potentially could be used later as session token)

		current_time = timezone.now()
		timespan = datetime.timedelta(days=3000)

		if token.created < (current_time - timespan):
				print('Delete')
				token.delete()
				raise exceptions.AuthenticationFailed('Token has expired please request for a new one')

		return (None, token)  #Our token model does not associate with user


class CAM2JsonWebTokenAuthentication(BaseAuthentication):
	def get_jwt_value(self, request):
		"""
		Parse the JSON Web Token from the request header.
		input request: HTTP request
		return: JSON Web Token
		"""
		auth = get_authorization_header(request).split()
		auth_header_prefix = api_settings.JWT_AUTH_HEADER_PREFIX

		if not auth:
			if api_settings.JWT_AUTH_COOKIE:
				return request.COOKIES.get(api_settings.JWT_AUTH_COOKIE)
			return None
		if str(auth[0], 'utf-8') != auth_header_prefix:
			return None
		
		if len(auth) == 1:
			raise exceptions.AuthenticationFailed("Invalid Authorization header. No credentials provided.")
		elif len(auth) > 2:
			raise exceptions.AuthenticationFailed("Invalid Authorization header. Credentials string should not contain spaces.")
		else:
			return str(auth[1], 'utf-8')

	def authenticate(self, request):
		"""
		Decrypt the JSON Web Token and verify the payload.
		input request: HTTP request
		return: tuple of request.user & request.auth
		"""
		jwt_value = self.get_jwt_value(request)
		if jwt_value is None:
			return None

		try:
			payload = jwt_decode_handler(jwt_value)
		except jwt.ExpiredSignature:
			raise exceptions.AuthenticationFailed('Signature has expired')
		except jwt.DecodeError:
			raise exceptions.AuthenticationFailed('Decode Error')
		except jwt.InvalidTokenError:
			raise exceptions.AuthenticationFailed('Invalid Token')

		print(payload)
		app = self.authenticate_credentials(payload)
		app.access_times += 1
		app.save()

		return (app, jwt_value)

	# def authenticate_credentials(self, payload):
	# 	username = payload.get('username', None)

	# 	if username is None:
	# 		raise exceptions.AuthenticationFailed("Invalid Payload. Needs to contain username")

	# 	try:
	# 		user = User.objects.get_by_natural_key(username)
	# 	except User.DoesNotExist:
	# 		raise exceptions.AuthenticationFailed("Invalid Signature")

	# 	if not user.is_active:
	# 		raise exceptions.AuthenticationFailed("User is disabled")

	# 	register_user = RegisterUser.objects.get(user=user)

	# 	return register_user

	def authenticate_credentials(self, payload):
		"""
		Authenticate the payload. The client_id and secret must matches the record in the database
		input payload: payload of the JSON Web Token
		return: request.auth

		"""
		client_id = payload.get('id', None)

		if client_id is None:
			raise exceptions.AuthenticationFailed("Invalid Payload. Needs to contain client_id")
		try:
			app = Application.objects.get(client_id=client_id)
		except Application.DoesNotExist:
			raise exceptions.AuthenticationFailed("Invalid Payload. Client_id cannot be found")

		return app

class CAM2HommieAuthentication(BaseAuthentication):
	def authenticate(self, request):
		"""
		Verify the Authorization method  
		input request: HTTP request
		return: tuple of None & request.auth
		"""
		try:
			auth = get_authorization_header(request).split()
		except:
			raise exceptions.AuthenticationFailed('Please provide Authorization Header')
		
		if str(auth[0], 'utf-8') != 'Basic':
			raise exceptions.AuthenticationFailed('Invalid Authorization method')
		elif len(auth) == 1 or len(auth) == 0:
			raise exceptions.AuthenticationFailed('Invalid Authorization Header. No credentials provided')
		elif len(auth) > 2:
			raise exceptions.AuthenticationFailed('Invalid Authorization Header. Credential string should not contain string')
		else:
			token = str(auth[1], 'utf-8')
			app = self.authenticate_credentials(token)
			return (app, token)


	def authenticate_credentials(self, token):
		"""
		Authenticate the credential
		input token: Authorization credential
		return: request.user
		"""
		if token != 'CAM2API':
			raise exceptions.AuthenticationFailed('Invalid Token')
		return None









