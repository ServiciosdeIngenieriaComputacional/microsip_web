from django.conf.urls import patterns, url
from django.views import generic
from ventas import views

urlpatterns = patterns('',
    #FACTURAS
    (r'^Facturas/$', views.facturas_View),
)