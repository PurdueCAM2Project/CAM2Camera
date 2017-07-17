from rest_framework import serializers
from CAM2API.models import Camera, IP, Non_IP
from django.core.exceptions import ValidationError
from django.contrib.gis.geos import GEOSGeometry
import re
import geocoder


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
