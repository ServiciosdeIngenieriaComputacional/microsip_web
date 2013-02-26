#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from ventas.models import *
from ventas.forms import *
import datetime, time
from django.db.models import Q
#Paginacion

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# user autentication
from django.contrib.auth.decorators import login_required, permission_required

##########################################
## 										##
##              FACTURAS           	    ##
##										##
##########################################

@login_required(login_url='/login/')
def facturas_View(request, template_name='ventas/ventas.html'):
	# inventarios_fisicos_list = DoctosInvfis.objects.all().order_by('-fecha') 

	# paginator = Paginator(inventarios_fisicos_list, 15) # Muestra 5 inventarios por pagina
	# page = request.GET.get('page')

	# #####PARA PAGINACION##############
	# try:
	# 	inventarios_fisicos = paginator.page(page)
	# except PageNotAnInteger:
	#     # If page is not an integer, deliver first page.
	#     inventarios_fisicos = paginator.page(1)
	# except EmptyPage:
	#     # If page is out of range (e.g. 9999), deliver last page of results.
	#     inventarios_fisicos = paginator.page(paginator.num_pages)

#	c = {'inventarios_fisicos':inventarios_fisicos}
	return render_to_response(template_name, {}, context_instance=RequestContext(request))
