
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.views import generic

import autocomplete_light
autocomplete_light.autodiscover()

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	(r'^$', 'inventarios.views.index'),
    url(r'^inventarios/', include('inventarios.urls', namespace='Inventarios')),
    url(r'^ventas/', include('ventas.urls', namespace='ventas')),
    url(r'^cuentas_por_pagar/', include('cuentas_por_pagar.urls', namespace='cuentas_por_pagar')),
    url(r'^contabilidad/', include('contabilidad.urls', namespace='contabilidad')),
    
    url(r'autocomplete/', include('autocomplete_light.urls')),
    url(r'^admin/', include(admin.site.urls)),
    #LOGIN
    url(r'^login/$','inventarios.views.ingresar'),
    url(r'^logout/$', 'inventarios.views.logoutUser'),
)
