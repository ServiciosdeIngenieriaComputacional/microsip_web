from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from inventarios import views
# Uncomment the next two lines to enable the admin:

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	(r'^$', views.index),
    # Examples:
    # url(r'^$', 'microsip_web.views.home', name='home'),
    # url(r'^microsip_web/', include('microsip_web.foo.urls')),
    #INVENTARIOS FISICOS
    (r'^InventarioFisico/$', views.DoctosInDet_manage_inlineView),
    (r'^InventarioFisico/(?P<id>\d+)/', views.DoctosInDet_manage_inlineView),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
