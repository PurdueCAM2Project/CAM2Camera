from rest_framework import serializers
from CAM2API.models import Camera, IP, Non_IP
from django.core.exceptions import ValidationError
from django.contrib.gis.geos import GEOSGeometry
import re
import geocoder


class IPSerializer(serializers.ModelSerializer):

    class Meta:
        model = IP
        fields = ('ip','port')

    def create(self, validated_data):
        return IP.objects.create(**validated_data)

    def to_internal_value(self, data):
        deserialized_data = {}
        for field in self.fields:
            deserialized_data[field] = data.get(field,None)
        return deserialized_data

    def to_representation(self, instance):
        ret = {}
        for f in self.fields.values():
            value = getattr(instance, f.field_name)  # f.field_name returns 'ip','port',
            ret[f.field_name] = f.to_representation(value)
        return ret

class NonIPSerializer(serializers.ModelSerializer):
    class Meta:
        model = Non_IP
        fields = ('url',)

class CameraSerializer(serializers.ModelSerializer):
	retrieval_model = serializers.SerializerMethodField()

	class Meta:
		model = Camera
		fields = ('pk', 'camera_id', 'city' ,'state', 'country', 'retrieval_model','lat','lng','lat_lng','source','source_url',
			'date_added','last_updated','camera_type','description','is_video','framerate',
			'outdoors','indoors','traffic','inactive','resolution_w','resolution_h')
		extra_kwargs = {'lat_lng':{'write_only':True}}

	def create(self, validated_data):
		retrieval_data = validated_data.pop('retrieval_model')
		if 'url' in retrieval_data.keys():
			retrieval_model = Non_IP.objects.create(url=retrieval_data['url'])
		else:
			retrieval_model = IP.objects.create(**retrieval_data)
		camera = Camera.objects.create(retrieval_model=retrieval_model, **validated_data)
		return camera

	def update(self, instance, validated_data):  #Deserialize
		print("Update")
		retrieval_data = validated_data.pop('retrieval_model')
		retrieval_instance = instance.retrieval_model
		for key, value in validated_data.items():
			if value is not None:
				setattr(instance,key,value)
		setattr(instance,'lat_lng', self.set_lat_lng(validated_data))
		for key, value in retrieval_data.items():
			setattr(retrieval_instance, key, value)
		retrieval_instance.save()
		instance.save()
		return instance

	def to_internal_value(self, data):
		deserialized_data = {}
		for field in self.fields:
			if field == "retrieval_model":
				retrieval_model_data = data.get('retrieval_model', None)
				if 'ip' in retrieval_model_data.keys():
					retrieval_model = IPSerializer(data=retrieval_model_data)
					deserialized_data["camera_type"] = "IP"
				elif 'url' in retrieval_model_data.keys():
					retrieval_model = NonIPSerializer(data=retrieval_model_data)
					deserialized_data["camera_type"] = "Non_IP"
				deserialized_data[field] = retrieval_model.to_internal_value(retrieval_model_data)
			elif field == "lat_lng":
				deserialized_data[field] = self.set_lat_lng(data)
			elif field != "camera_type":
				deserialized_data[field] = data.get(field, None)
		return deserialized_data

	def to_representation(self,instance):   #Serialize
		ret = {}
		fields = self._readable_fields
		for field in fields:
			value = getattr(instance, field.field_name)
			try:
				ret[field.field_name] = field.to_representation(value)
			except:
				pass
		return ret

	def get_retrieval_model(self,instance):  #Serialize
		if isinstance(instance,IP):
			return IPSerializer(instance).data   		#Use IPSerializer if retrieval_model object is a IP object()
		else:
			return NonIPSerializer(instance).data 		#Use NonIPSerializer if retrieval_model object is Non_IP object
	
	def set_lat_lng(self, data):
		lat_lng = '{{ "type": "Point", "coordinates": [ {}, {} ] }}'.format(data.get('lat',None), data.get('lng',None))
		lat_lng = GEOSGeometry(lat_lng)
		return lat_lng

	def validate(self, data):
		errors = []
		for field in self.fields:
			try:
				validate_method = getattr(self, 'validate_'+field)
				validate_method(data.get(field))
			except AttributeError:
				pass
			except ValidationError as exc:
				errors.append(exc) 
		data = self.validate_geo_location(data)
		if any(errors):
			raise ValidationError(errors)
		return data

	def validate_framerate(self, framerate):
		if framerate != None and framerate < 0 and framerate > 60:
			raise ValidationError('Cameras with framerates higher than 60 are not supported.')

	def validate_geo_location(self, data):
		geo_checker = geocoder.google([data["lat"], data["lng"]], method="reverse").json
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
		regex = r", ([a-zA-Z\s]+)$"
		country = re.findall(regex, address)[0]
		return country
