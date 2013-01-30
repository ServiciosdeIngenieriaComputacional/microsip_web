from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from inventarios import views
# Uncomment the next two lines to enable the admin:

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	(r'^$', views.index),
    #INVENTARIOS FISICOS
    (r'^InventariosFisicos/$', views.invetariosFisicos_View),
    (r'^InventarioFisico/$', views.invetarioFisico_manageView),
    (r'^InventarioFisico/(?P<id>\d+)/', views.invetarioFisico_manageView),
    (r'^InventarioFisico/Delete/(?P<id>\d+)/', views.invetarioFisico_delete),
    #ENTRADAS
    (r'^Entradas/$', views.entradas_View),
    (r'^Entrada/$', views.entrada_manageView),
    (r'^Entrada/(?P<id>\d+)/', views.entrada_manageView),
    (r'^Entrada/Delete/(?P<id>\d+)/', views.entrada_delete),
    #SALIDAS
    (r'^Salidas/$', views.salidas_View),
    (r'^Salida/$', views.salida_manageView),
    (r'^Salida/(?P<id>\d+)/', views.salida_manageView),
    (r'^Salida/Delete/(?P<id>\d+)/', views.salida_delete),
    #LOGIN
    url(r'^login/$',views.ingresar),
    url(r'^logout/$', views.logoutUser),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),
)
