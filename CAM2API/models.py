from __future__ import unicode_literals
from django.contrib.gis.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, \
GenericRelation
from django.contrib.contenttypes.models import ContentType

class Non_IP(models.Model):
    url = models.URLField(unique=True)  #URL to the image data

class IP(models.Model):
    ip = models.GenericIPAddressField(unique=True) #IP to the image data
    port = models.PositiveIntegerField(default=80)

class Camera(models.Model):
	camera_id = models.PositiveIntegerField(unique=True)
	# Geography:
	city = models.CharField(max_length=100, null=True, blank=True)
	state = models.CharField(max_length=12, null=True, blank=True)
	country = models.CharField(max_length=100, null=True, blank=True)
	lat = models.FloatField()
	lng = models.FloatField()
    #geographical location of the Camera
	lat_lng = models.GeometryField(geography=True, null=False, blank=True)
	# Source Information:
	source = models.CharField(max_length=100, null=True, blank=True)
	source_url = models.URLField(null=True, blank=True) # URL of the provider
	# Time Information:
	date_added = models.DateTimeField(auto_now_add=True)
	last_updated = models.DateTimeField(auto_now_add=True)
	# Camera Types (Non_ip or IP)
	CAMERA_TYPES = enumerate(['Non_IP', 'IP'])
	camera_type = models.CharField(max_length=10, null=False, blank=True,
                                   choices=CAMERA_TYPES, default='Non_IP')
	# More Info:
	description = models.CharField(max_length=100, null=True, blank=True)
	is_video = models.NullBooleanField() #camera is a video stream
	framerate = models.FloatField(null=True, blank=True)
	outdoors = models.NullBooleanField()
	traffic = models.NullBooleanField()
	inactive = models.NullBooleanField()
	resolution_w = models.PositiveIntegerField(null=True, blank=True)
	resolution_h = models.PositiveIntegerField(null=True, blank=True)
	# Image Retrieval objects:
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     null=True, blank=True, related_name=
                                     "retrieval_model")
	object_id = models.PositiveIntegerField(null=True)
	retrieval_model = GenericForeignKey('content_type', 'object_id')
