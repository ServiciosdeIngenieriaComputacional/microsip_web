
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.views import generic
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

dajaxice_autodiscover()
import autocomplete_light
autocomplete_light.autodiscover()

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
	(r'^$', 'main.views.index'),
    #Descomentar esta linea para habilitar inventarios
    #url(r'^inventarios/', include('inventarios.urls', namespace='Inventarios')),
    #url(r'^inventarios/', 'inventarios.views.index'),
    #Descomentar esta linea para habilitar ventas
    #url(r'^ventas/', include('ventas.urls', namespace='ventas')),
    #url(r'^ventas/', 'inventarios.views.index'),
    
    url(r'^cuentas_por_pagar/', include('cuentas_por_pagar.urls', namespace='cuentas_por_pagar')),
    #url(r'^cuentas_por_cobrar/', include('cuentas_por_cobrar.urls', namespace='cuentas_por_cobrar')),
    #url(r'^contabilidad/', include('contabilidad.urls', namespace='contabilidad')),
    
    url(r'autocomplete/', include('autocomplete_light.urls')),
    #url(r'^admin/', include(admin.site.urls)),
    #LOGIN
    url(r'^login/$','inventarios.views.ingresar'),
    url(r'^logout/$', 'inventarios.views.logoutUser'),
)

urlpatterns += staticfiles_urlpatterns()