from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from CAM2API import views

urlpatterns = [
    url(r'^$', views.CameraList.as_view()),
    url(r'^cameras/$', views.CameraList.as_view()),
    url(r'^cameras/(?P<cd>[0-9]+)/$', views.CameraDetail.as_view()),
]

# Adds format patterns to the API
urlpatterns = format_suffix_patterns(urlpatterns)