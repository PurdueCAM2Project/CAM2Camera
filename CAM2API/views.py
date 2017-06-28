# Import Models and Serializer
from CAM2API.models import Camera, Non_IP, IP
from CAM2API.serializers import CameraSerializer, IPSerializer, NonIPSerializer

from django.contrib.gis.geos import GEOSGeometry

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404

class CameraList(APIView):

	def get(self, request):
		filtered_cameras = filter_cameras(self.request.query_params)
		serializer = CameraSerializer(filtered_cameras, many=True)
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

def filter_cameras(query_params):
	result = Camera.objects.all()
	for param in query_params:
		if param == "city":
			result = result.filter(city=query_params[param])
		elif param == "state":
			result = result.filter(state=query_params[param])
		elif param == "country":
			result = result.filter(country=query_params[param])
		elif param == "camera_type":
			result = result.filter(camera_type=query_params[param])
	return result 
