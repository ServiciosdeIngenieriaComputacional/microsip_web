from django.conf.urls import patterns, url
from django.views import generic
from contabilidad import views

urlpatterns = patterns('',
	 (r'^polizas/$', views.polizas_View),
	 (r'^polizas_pendientes/$', views.polizas_pendientesView),
)