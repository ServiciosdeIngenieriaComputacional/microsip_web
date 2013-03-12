#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from inventarios.models import *
#from contabilidad.forms import *
import datetime, time
from django.db.models import Q
#Paginacion

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# user autentication
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Max

@login_required(login_url='/inventarios/login/')
def polizas_View(request, template_name='polizas/polizas.html'):
	polizas_list = DoctoCo.objects.filter(estatus='N').order_by('-fecha') 

	paginator = Paginator(polizas_list, 15) # Muestra 5 inventarios por pagina
	page = request.GET.get('page')

	#####PARA PAGINACION##############
	try:
		polizas = paginator.page(page)
	except PageNotAnInteger:
	    # If page is not an integer, deliver first page.
	    polizas = paginator.page(1)
	except EmptyPage:
	    # If page is out of range (e.g. 9999), deliver last page of results.
	    polizas = paginator.page(paginator.num_pages)

	c = {'polizas':polizas}
	return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/inventarios/login/')
def polizas_pendientesView(request, template_name='polizas/polizas_pendientes.html'):
	polizas_list = DoctoCo.objects.filter(estatus='P').order_by('-fecha') 

	paginator = Paginator(polizas_list, 15) # Muestra 5 inventarios por pagina
	page = request.GET.get('page')

	#####PARA PAGINACION##############
	try:
		polizas = paginator.page(page)
	except PageNotAnInteger:
	    # If page is not an integer, deliver first page.
	    polizas = paginator.page(1)
	except EmptyPage:
	    # If page is out of range (e.g. 9999), deliver last page of results.
	    polizas = paginator.page(paginator.num_pages)

	c = {'polizas':polizas}
	return render_to_response(template_name, c, context_instance=RequestContext(request))

