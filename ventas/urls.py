from django.conf.urls import patterns, url
from django.views import generic
from ventas import views

urlpatterns = patterns('',
	(r'^Facturas/$', views.facturas_View),
	(r'^PreferenciasEmpresa/$', views.preferenciasEmpresa_View),
    #FACTURAS
)