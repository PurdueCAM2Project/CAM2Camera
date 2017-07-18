from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from CAM2API import views

float_num = r'\-?\d+\.?\d{0,4}'
urlpatterns = [
	url(r'^$', views.Home.as_view()),
	url(r'^cameras/$', views.CameraList.as_view()),
	url(r'^(?P<cd>\d+)/$', views.CameraByID.as_view()),
	url(r'^query/lat=(?P<lat>{})\,lng=(?P<lon>{}),'
		.format(float_num, float_num) +
		r'(?P<query_type>(radius|count))=(?P<value>\d+)/$'
		, views.CameraQuery.as_view()),
	url(r'^register_app/$', views.RegisterAppView.as_view(), name='register_app'),
	url(r'^token/$', views.ObtainAppTokenView.as_view(), name="obtain_app_token"),
	url(r'^refresh_token/$', views.RefreshAppTokenView.as_view(), name="refresh_token")
]

# Adds format patterns to the API
urlpatterns = format_suffix_patterns(urlpatterns)
