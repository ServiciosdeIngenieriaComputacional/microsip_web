from django.conf.urls import patterns, url
from django.views import generic
from cuentas_por_pagar import views

urlpatterns = patterns('',
	(r'^GenerarPolizas/$', views.generar_polizas_View),
	(r'^PreferenciasEmpresa/$', views.preferenciasEmpresa_View),
)