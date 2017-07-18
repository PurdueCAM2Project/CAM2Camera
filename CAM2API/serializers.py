from rest_framework import serializers
from CAM2API.models import Camera, IP, Non_IP, Application
from django.core.exceptions import ValidationError
from django.contrib.gis.geos import GEOSGeometry
from CAM2API.utils import (jwt_decode_handler, jwt_app_payload_handler, jwt_encode_handler, )
from CAM2API.signals import auto_refresh
from calendar import timegm
import re
import geocoder
import jwt
import datetime
import uuid
import hashlib
import os
import binascii

class IPSerializer(serializers.ModelSerializer):
	"""Serializer for the instances of IP."""

	class Meta:
		model = IP
		fields = ('ip','port')

	def create(self, validated_data):
		"""Creating an instance of the IP object from the validated data."""
		return IP.objects.create(**validated_data)

	def to_internal_value(self, data):
		"""Parsing information from data into a dictionary."""
		deserialized_data = {}
		for field in self.fields:
			deserialized_data[field] = data.get(field,None)
		return deserialized_data

	def to_representation(self, instance):
		"""Serializing data for creating IP object."""
		ret = {}
		for f in self.fields.values():
			value = getattr(instance, f.field_name)
			ret[f.field_name] = f.to_representation(value)
		return ret

class NonIPSerializer(serializers.ModelSerializer):
	"""Serializer for the instances of Non_IP."""

	class Meta:
		model = Non_IP
		fields = ('url',)

class CameraSerializer(serializers.ModelSerializer):
	"""Serializer for the instances of Non_IP."""

	retrieval_model = serializers.SerializerMethodField()

	class Meta:
		model = Camera
		fields = ('pk', 'camera_id', 'city' ,'state', 'country',
				  'retrieval_model','lat','lng','lat_lng','source',
				  'source_url','date_added','last_updated','camera_type',
				  'description','is_video','framerate','outdoors','traffic',
				  'inactive','resolution_w','resolution_h')
		extra_kwargs = {'lat_lng':{'write_only':True}}

	def create(self, validated_data):
		"""Creating new Camera object from the validated data."""
		retrieval_data = validated_data.pop('retrieval_model')
		if 'url' in retrieval_data.keys():
			retrieval_model = Non_IP.objects.create(url=retrieval_data['url'])
		else:
			retrieval_model = IP.objects.create(**retrieval_data)
		camera = Camera.objects.create(retrieval_model=retrieval_model,
									   **validated_data)
		return camera

	def update(self, camera, validated_data):
		"""Updates an existing Camera object with the validated_data."""
		Camera.objects.filter(pk=camera.pk).update(**validated_data)
		return camera

	def to_internal_value(self, data):
		"""Parsing information from data into a dictionary."""
		deserialized_data = {}
		for field in self.fields:
			if field == "retrieval_model" and 'retrieval_model' in data.keys():
				retrieval = data.get('retrieval_model', None)
				if 'ip' in retrieval.keys():
					retrieval_model = IPSerializer(data=retrieval)
					deserialized_data["camera_type"] = "IP"
				elif 'url' in retrieval.keys():
					retrieval_model = NonIPSerializer(data=retrieval)
					deserialized_data["camera_type"] = "Non_IP"
				deserialized_data[field] = retrieval_model.to_internal_value(
					retrieval)
			elif field == "lat_lng" and 'lat' in data.keys() \
								and 'lng' in data.keys():
				deserialized_data[field] = self.set_lat_lng(data)
			elif field != "camera_type" and field in data.keys():
				deserialized_data[field] = data.get(field, None)
		return deserialized_data

	def to_representation(self,instance):
		"""Serializes instance into a dictionary."""
		ret = {}
		fields = self._readable_fields
		for field in fields:
			value = getattr(instance, field.field_name)
			try:
				ret[field.field_name] = field.to_representation(value)
			except:
				pass
		return ret

	def get_retrieval_model(self,instance):
		"""Takes retrieval_model instance and returns data from it."""
		if isinstance(instance,IP):
			return IPSerializer(instance).data
		else:
			return NonIPSerializer(instance).data

	def set_lat_lng(self, data):
		"""Takes lat and lon from data, and creates a geographical location."""
		lat_lng = '{{ "type": "Point", "coordinates": [ {}, {} ] }}'.format(
			data.get('lat',None), data.get('lng',None))
		lat_lng = GEOSGeometry(lat_lng)
		return lat_lng

	def validate(self, data):
		"""Validating data passed to the Camera serializer."""
		errors = []
		for field in self.fields:
			try:
				validate_method = getattr(self, 'validate_'+field)
				validate_method(data.get(field))
			except AttributeError:
				pass
			except ValidationError as exc:
				errors.append(exc) 
		if any(errors):
			raise ValidationError(errors)
		if 'lat' in data.keys() and 'lng' in data.keys():
			data = self.validate_geo_location(data)
		return data

	def validate_framerate(self, framerate):
		"""Checking if framerate value is in the appropriate range."""
		if framerate != None and framerate < 0 and framerate > 60:
			raise ValidationError('Cameras with framerates higher than 60 are \
										not supported.')

	def validate_lat(self, latitude):
		"""Checking if the latitude value is in the appropriate range."""
		if latitude and (float(latitude) < -90 or float(latitude) > 90):
			raise ValidationError('Latitude out of the range [-90, 90]')

	def validate_lng(self, longitude):
		"""Checking if the longitude value is in the appropriate range."""
		if longitude and (float(longitude) < -180 or float(longitude) > 180):
			raise ValidationError('Longitude out of the range [-180, 180]')

	def validate_retrieval_model(self, retrieval_model):
		"""Checking if ip or url was provided by the user"""
		if not retrieval_model:
			raise ValidationError('Retrieval model for the camera not provided')

	def validate_geo_location(self, data):
		"""Retrieving geographical data from the lat and lon, if possible."""
		geo_checker = geocoder.google([data["lat"], data["lng"]],
									  method="reverse").json
		if geo_checker["status"] == "OK":
			if("city" in geo_checker.keys()):
				data["city"] = geo_checker["city"]
			data["country"] = self.get_country(geo_checker["address"])
			if data["country"] == "USA":
				data["state"] = geo_checker["state"]
			else:
				data["state"] = None
		return data

	def get_country(self, address):
		"""Parsing the country from the address string."""
		regex = r", ([a-zA-Z\s]+)$"
		country = re.findall(regex, address)[0]
		return country

class RegisterAppSerializer(serializers.ModelSerializer):
	class Meta:
		model = Application
		fields = ("app_name", "permission_level", )

	def create(self, validated_data):
		"""
		Create an application object in the database
		input validated_data: dict of data returns from running validator
		returns: an instance of Application
		"""
		app = Application.objects.create_app(validated_data)
		return app


	def validate(self, data):
		permission_level = data.get('permission_level', None)
		if permission_level != 'Basic' and permission_level != 'Admin':
			raise serializers.ValidationError('Permission_level provided is not valid')
		return data

	def to_representation(self, instance):
		"""
		Generate the response of the serializer with client_id and client_secret
		input instance: an instance of the Application 
		return: dict of client_id and client_secret
		"""
		ret = {}
		fields = self._readable_fields
		for field in fields:
			ret[field.field_name] = getattr(instance, field.field_name, None)
		ret['client_id'] = getattr(instance, 'client_id', None)
		ret['client_secret'] = getattr(instance, 'client_secret', None)
		return ret

class ObtainAppTokenSerializer(serializers.ModelSerializer):
	class Meta:
		model = Application
		fields = ('client_id', 'client_secret', )
	
	def validate(self, data):
		"""
		Validate the client_id and client_secret with the record stored in the database
		input data: client_id and client_secret sent in the HTTP request
		return: validated_data 
		"""
		client_id = data.get('client_id',None)
		client_secret = data.get('client_secret', None)
		if client_id and client_secret:
			try:
				app = Application.objects.get(client_id=client_id)
			except Application.DoesNotExist:
				raise serializers.ValidationError("Client_id cannnot be found")

			try:
				assert client_secret == app.client_secret
			except AssertionError:
				raise serializers.ValidationError("client id and secret does not match.")
			return data
		else:
			serializers.ValidationError("Please provide both client id and secret")


class RefreshAppTokenSerializer(serializers.Serializer):
	token = serializers.CharField()

	def _check_payload(self, token):
		try:
			payload = jwt_decode_handler(token, False)
		except jwt.ExpiredSignature:
			#raise serializers.ValidationError("Signature has been expired")
			#auto_refresh.send(sender=None, token=token)
			pass
		except jwt.DecodeError:
			raise serializers.ValidationError("Decode Error")
		except jwt.InvalidTokenError:
			raise serializers.ValidationError("Invalid Token")
		return payload

	def _check_app(self, payload):
		client_id = payload.get("id")
		#print(client_id)
		#print(payload)
		try:
			app = Application.objects.get(client_id=client_id)
		except Application.DoesNotExist:
			return serializers.ValidationError("App does not exist")

		return app

	def validate(self, data):
		token = data["token"]
		payload = self._check_payload(token)
		app = self._check_app(payload)
		orig_iat = payload.get("orig_iat", None)

		if not orig_iat:
			raise serializers.ValidationError("This is not an refreshable token")
		else:
			refresh_limit = datetime.timedelta(days=1)
			expired_time = orig_iat + int(refresh_limit.days*24*3600 + refresh_limit.seconds)
			current_time = timegm(datetime.datetime.utcnow().utctimetuple())
			if expired_time < current_time:
				raise serializers.ValidationError("Refresh token has been expired")
			new_payload = jwt_app_payload_handler(app)
			new_payload["orig_iat"] = orig_iat
			new_token = jwt_encode_handler(new_payload)
			return{
				"token": new_token
			}

