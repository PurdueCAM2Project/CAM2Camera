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
from queue import PriorityQueue
import datetime

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

	def convert_data(self,data):
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

class CameraByID(APIView):
	lookup_field = ['camera_id']
	lookup_url_kwargs = ['cd']

	def get_camera_by_id(self):
		lookup_url_kwargs_value = [self.kwargs[item] for item in self.lookup_url_kwargs]
		filter_kwargs = dict(zip(self.lookup_field, lookup_url_kwargs_value))
		camera = get_object_or_404(Camera, **filter_kwargs)
		return camera

	def get(self, request, cd, format=None):
		camera = self.get_camera_by_id()
		serializer = CameraSerializer(camera)
		return(Response(serializer.data))

	def put(self, request, cd, format=None):
		camera = self.get_camera_by_id()
		data = self.convert_data(request.data)
		print(data)
		serializer = CameraSerializer(camera, data=data)
		if serializer.is_valid():
			serializer.save()
			return(Response(serializer.data))
		return(Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST))

	def delete(self, request, cd, format=None):
		camera = self.get_camera_by_id()
		retrieval_model_delete = camera.retrieval_model
		retrieval_model_delete.delete()
		camera.delete()
		return(Response(status=status.HTTP_204_NO_CONTENT))

	def convert_data(self,data):
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

class CameraQuery(APIView):

	def get(self, request, lat, lon, query_type, value):
		filtered_cameras = filter_cameras(self.request.query_params)
		lat_lng = '{{ "type": "Point", "coordinates": [ {}, {} ] }}'.format(lat, lon)
		location = GEOSGeometry(lat_lng)
		if query_type == "radius":
			result = self.radius_query(filtered_cameras, location, float(value))
		else:
			result = self.count_query(filtered_cameras, location, int(value))
		result = CameraSerializer(result, many=True)
		return Response(result.data)

	def radius_query(self, cameras, location, radius):
		result = []
		for camera in cameras:
			if location.distance(camera.lat_lng)*100 <= radius:
				result.append(camera)
		return result

	def count_query(self, cameras, location, count):
		result = PriorityQueue()
		for camera in cameras:
			result.put((location.distance(camera.lat_lng), camera))
		result_list = []
		for i in range(count):
			if not result.empty():
				distance, camera = result.get()
				result_list.append(camera)
			else:
				break
		return result_list

def filter_cameras(query_params):
	cameras = Camera.objects.all()
	for param in query_params:
		if param == "city":
			cameras = cameras.filter(city=query_params[param])
		elif param == "state":
			cameras = cameras.filter(state=query_params[param])
		elif param == "country":
			cameras = cameras.filter(country=query_params[param])
		elif param == "camera_type":
			cameras = cameras.filter(camera_type=query_params[param])
		elif param == "lat":
			cameras = cameras.filter(lat=float(query_params[param]))
		elif param == "lat_min":
			cameras = cameras.filter(lat__gte=float(query_params[param]))
		elif param == "lat_max":
			cameras = cameras.filter(lat__lte=float(query_params[param]))
		elif param == "lng":
			cameras = cameras.filter(lng=float(query_params[param]))
		elif param == "lng_min":
			cameras = cameras.filter(lng__gte=float(query_params[param]))
		elif param == "lng_max":
			cameras = cameras.filter(lng__lte=float(query_params[param]))
		elif param == "framerate":
			cameras = cameras.filter(framerate=float(query_params[param]))
		elif param == "framerate_min":
			cameras = cameras.filter(framerate__gte=float(query_params[param]))
		elif param == "framerate_max":
			cameras = cameras.filter(framerate__lte=float(query_params[param]))
		elif param == "source":
			cameras = cameras.filter(source=query_params[param])
		elif param == "resolution_w":
			cameras = cameras.filter(resolution_w=int(query_params[param]))
		elif param == "resolution_w_min":
			cameras = cameras.filter(resolution_w__gte=int(query_params[param]))
		elif param == "resolution_w_max":
			cameras = cameras.filter(resolution_w__lte=int(query_params[param]))
		elif param == "resolution_h":
			cameras = cameras.filter(resolution_h=int(query_params[param]))
		elif param == "resolution_h_min":
			cameras = cameras.filter(resolution_h__gte=int(query_params[param]))
		elif param == "resolution_h_max":
			cameras = cameras.filter(resolution_h__lte=int(query_params[param]))
		elif param == "id":
			cameras = cameras.filter(camera_id=int(query_params[param]))
		elif param == "video":
			if query_params[param] in ['True', 'true', 't']:
				cameras = cameras.filter(is_video=True)
			elif query_params[param] in ['False', 'false', 'f']:
				cameras = cameras.filter(is_video=False)
		elif param == "outdoors":
			if query_params[param] in ['True', 'true', 't']:
				cameras = cameras.filter(outdoors=True)
			elif query_params[param] in ['False', 'false', 'f']:
				cameras = cameras.filter(outdoors=False)
		elif param == "traffic":
			if query_params[param] in ['True', 'true', 't']:
				cameras = cameras.filter(traffic=True)
			elif query_params[param] in ['False', 'false', 'f']:
				cameras = cameras.filter(traffic=False)
		elif param == "inactive":
			if query_params[param] in ['True', 'true', 't']:
				cameras = cameras.filter(inactive=True)
			elif query_params[param] in ['False', 'false', 'f']:
				cameras = cameras.filter(inactive=False)
		elif param == "added_before":
			time_format = "%m/%d/%Y"
			limit = datetime.datetime.strptime(query_params[param],time_format)
			cameras = cameras.filter(date_added__lte = limit)
		elif param == "added_after":
			time_format = "%m/%d/%Y"
			limit = datetime.datetime.strptime(query_params[param],time_format)
			cameras = cameras.filter(date_added__gte = limit)
		elif param == "updated_before":
			time_format = "%m/%d/%Y"
			limit = datetime.datetime.strptime(query_params[param],time_format)
			cameras = cameras.filter(last_updated__lte = limit)
		elif param == "updated_after":
			time_format = "%m/%d/%Y"
			limit = datetime.datetime.strptime(query_params[param],time_format)
			cameras = cameras.filter(last_updated__gte = limit)
	return cameras 
