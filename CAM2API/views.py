# Import Models and Serializer
from CAM2API.models import Camera, Non_IP, IP, Application
from CAM2API.serializers import (CameraSerializer, IPSerializer, 
								NonIPSerializer, RegisterAppSerializer, 
								ObtainAppTokenSerializer, )
from CAM2API.authentication import CAM2JsonWebTokenAuthentication, CAM2HommieAuthentication
from CAM2API.utils import ( jwt_encode_handler, jwt_decode_handler, jwt_app_payload_handler, )

from django.contrib.gis.geos import GEOSGeometry

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404

class CameraList(APIView):
	"""
	Returns:
		GET - JSON response containing all the camera data in the database
		POST - Creates new camera objects in the database
	"""
	def get(self, request, format=None):
		"""
		Returns JSON response containing all the camera data in the database
		input request: HTTP GET request
		input format: optional format string included in HTTP request
		return: JSON String
		"""
		cameras = Camera.objects.all()
		serializer = CameraSerializer(cameras, many=True)
		return Response(serializer.data)

	def post(self, request, format=None):
		data = self.convert_data(request.data)
		serializer = CameraSerializer(data=data)

		if serializer.is_valid():
			serializer.save()
			print("Data added")
			return Response(serializer.data)
		else:	
			print("Data not added")
			return Response(serializer.errors)

	def convert_data(self,data):     #needs further modification to make it more explicit
		if "url" in data.keys():
			url = data.pop("url")
			data["retrieval_model"] = {"url":url}
		elif "ip" in data.keys():
			ip = data.pop("ip")
			if "port" in data.keys():
				port = data.pop("port")
			else:
				port = 80
			data["retrieval_model"] = {"ip":ip, "port":port}
		return data

class CameraDetail(APIView):
	"""
	Retrieve, update or delete a specific camera in the database biased on camera ID 
		from the original database
	"""

	lookup_field = ['camera_id']
	lookup_url_kwargs = ['cd']

	def get_object(self):
		lookup_url_kwargs = self.lookup_url_kwargs
		lookup_url_kwargs_value = [self.kwargs[item] for item in lookup_url_kwargs]
		filter_kwargs = dict(zip(self.lookup_field, lookup_url_kwargs_value))
		instance = get_object_or_404(Camera, **filter_kwargs) #the same as instance = get_object_or_404(Camera, camera_id=cd)
		return instance

	def get(self, request, cd, format=None):
		"""
		Handles HTTP GET requests to a specific camera in the database
		input request: the HTTP GET request sent to the API
		input pk: primary key of the camera in question.
		input format: optional format string included in HTTP request
		return: JSON/API response containing the relevant camera data or a HTTP 404 error
				if there is no camera that matches the pk 
		"""
		camera = self.get_object()
		serializer = CameraSerializer(camera)
		return(Response(serializer.data))


	def put(self, request, cd, format=None):
		"""
		Handles HTTP PUT requests to a specific camera in the database and modifies the 
			given camera object in the database
		input request: the HTTP PUT request sent to the API
		input pk: primary key of the camera in question.
		input format: optional format string included in HTTP request
		return: Response containing the relevant camera data if the request is successful 
				or a HTTP 400 error if the camera cannot be edited to the database
		"""
		camera = self.get_object()
		data = self.convert_data(request.data)
		print(data)
		serializer = CameraSerializer(camera, data=data)
		if serializer.is_valid():
			serializer.save()
			return(Response(serializer.data))
		return(Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST))


	def delete(self, request, cd, format=None):
		"""
		Handles HTTP DELETE requests to a specific camera in the database
		input request: the HTTP DELETE request sent to the API
		input pk: primary key of the camera in question.
		input format: optional format string included in HTTP request
		return: Response containing the relevant camera data if the request is successful 
				or a HTTP 204 error if the camera is deleted from the database
		"""
		camera = self.get_object()
		retrieval_model_delete = camera.retrieval_model
		retrieval_model_delete.delete()
		camera.delete()
		return(Response(status=status.HTTP_204_NO_CONTENT))

class RegisterAppView(APIView):
	"""
	Returns:
	POST -- Create a new application object in the database with provided app_name and permission_level
	"""
	authentication_classes = (CAM2HommieAuthentication, )

	def post(self, request, format=None):
		"""
		Create a new application object in the databse and returns the correspondent client_id and client_secret.
		input request: HTTP request
		return: client_id and client_secret with HTTP_201_CREATED / HTTP_400_BAD_REQUEST
		"""
		print(request.user, request.auth)
		data = request.data
		serializer = RegisterAppSerializer(data=data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors)

class ObtainAppTokenView(APIView):
	"""
	Returns:
	POST -- Dynamically generate the JSON Web Token encrypting the client_id and client_secret
	"""
	def post(self, request, format=None):
		"""
		Validate the client_id and client_secret and Response with the JSON Web Token
		input request: HTTP request
		return: JSON Web Token with HTTP_201_CREATED
				/ HTTP_400_BAD_REQUEST
		"""
		data = request.data
		serializer = ObtainAppTokenSerializer(data=data)
		if serializer.is_valid():
			token = self.generate_token(serializer.validated_data)
			return Response({"token": token}, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def generate_token(self, validated_data):
		"""
		Generate the JSON Web Token with the validated client_id and client_secret
		input reqeust: dict of validated client_id and client_secret
		return: JSON Web Token
		"""
		app = Application.objects.get(client_id=validated_data["client_id"])
		payload = jwt_app_payload_handler(app)
		token = jwt_encode_handler(payload)
		return token