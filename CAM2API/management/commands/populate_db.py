from django.core.management.base import BaseCommand
from CAM2API.models import Camera, Non_IP, IP
from django.contrib.gis.geos import GEOSGeometry
from django.utils import timezone
from django.core import management

class Command(BaseCommand):
	help = 'This script populates database with some fake data'

	def _create_data(self):
		im_uri = Non_IP(url="www.example.com/image")
		im_uri.save()
		lat_lng = GEOSGeometry('{ "type": "Point", "coordinates": [ 35.6895, 139.6917 ] }')
		non_ip_cam = Camera(camera_id='52', lat_lng=lat_lng, lat=35.6895, lng=139.6917, city='Tokyo', state='', country='Japan', source='google', source_url='www.google.com', last_updated=timezone.now(), description='This is a non-ip camera', is_video=True, framerate=0.3, outdoors=True, indoors=False, traffic=False, inactive=False, resolution_w=1920, resolution_h=1080, camera_type="Non_ip", retrieval_model=im_uri)
		non_ip_cam.save()

		im_ip = IP(ip='10.0.0.1', port=80)
		lat_lng = GEOSGeometry('{ "type": "Point", "coordinates": [ 40.4259, 86.9081 ] }')
		ip_cam = Camera(camera_id='16', lat_lng=lat_lng, lat=40.4259, lng=86.9081, city='West Lafayette', state='Indiana', country='United States', source='google', source_url='www.google.com', last_updated=timezone.now(), description='This is an ip camera', is_video=False, outdoors=False, indoors=True, traffic=True, inactive=True, resolution_w=1024, resolution_h=768, camera_type="IP", retrieval_model=im_ip)
		ip_cam.save()

	def handle(self, *args, **options):
		#WARNING!!! Erases all data from the database!!
		print("Deleting all database entries")
		management.call_command('flush', verbosity=0, interactive=False)
		print("Creating new database entries")
		self._create_data()
		print("Database successfully populated")
