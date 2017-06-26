from __future__ import unicode_literals

# from django.db import models
from django.contrib.gis.db import models # contrib.gis.db ensures the PostGis models are included

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
import datetime

# Camera Model
class Non_IP(models.Model):
	url = models.URLField(unique=True) # URL to the image data

class IP(models.Model):
	ip = models.GenericIPAddressField(unique=True)
	port = models.PositiveIntegerField(default=80)

class Camera(models.Model):
	camera_id = models.PositiveIntegerField(unique=True) # id from old database
	# Geography: 
	city = models.CharField(max_length=30, null=True, blank=True)
	state = models.CharField(max_length=12, null=True, blank=True)
	country = models.CharField(max_length=50, null=True, blank=True)
	lat = models.FloatField(max_length=100)
	lng = models.FloatField(max_length=100)
	lat_lng = models.GeometryField(geography=True, null=False, blank=True) # Sets geometry field points to geography in postgis

	# Source Information:
	source = models.CharField(max_length=100)
	source_url = models.URLField() # URL of the provider of the source (NOT for image data!)
	# Time Information:
	date_added = models.DateTimeField(auto_now_add=True)
	last_updated = models.DateTimeField(auto_now_add=True) # Last known time a snapshot was downloaded30
	# Camera Types (Non_ip or IP)
	CAMERA_TYPES = enumerate(['Non_IP', 'IP'])
	camera_type = models.CharField(max_length=10, null=False, blank=True, choices=CAMERA_TYPES, default='Non_IP')
	# More Info:
	description = models.CharField(max_length=100, null=True, blank=True) # Description of the camera
	is_video = models.BooleanField(default=False) # True if camera is a video stream
	framerate = models.FloatField(null=True, blank=True) # Frame rate of the camera if known
	outdoors = models.NullBooleanField() # True if camera is outdoors Null if unknown.
	indoors = models.NullBooleanField() # True if the camera is indoors Null if unknown.
	traffic = models.NullBooleanField() # True if the camera is a traffic camera Null if unknown.
	inactive = models.NullBooleanField() # True if data cannot be accessed from the camera Null if unknown.
	resolution_w = models.PositiveIntegerField(null=True, blank=True) # Resolution width determined automatically 
	resolution_h = models.PositiveIntegerField(null=True, blank=True) # Resolution height determined automatically 
	# Image Retrieval objects:
	# For more information see https://docs.djangoproject.com/en/1.10/ref/contrib/contenttypes/#generic-relations
	
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=False, blank=True, related_name="retrieval_model") #ContentType table incudes Class<Non_IP> as well as Class<IP>
	object_id = models.PositiveIntegerField(null=True) #object_id will be automatically generated and represents the sepecfic primary key for each object in the queryset 
	retrieval_model = GenericForeignKey('content_type', 'object_id')
