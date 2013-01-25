#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from inventarios.models import *
from inventarios.forms import *
import datetime, time
from django.db.models import Q

from django.forms.formsets import formset_factory, BaseFormSet
from django.forms.models import inlineformset_factory

#Paginacion
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# user autentication
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, AdminPasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, permission_required

from django.db import connection
import xlrd
from django.utils.encoding import smart_str, smart_unicode

def index(request):
	articulos = Articulos.objects.all()
	c = {'articulos':articulos}
  	return render_to_response('index.html', c, context_instance=RequestContext(request))

##########################################
## 										##
##        INVENTARIOS FISICOS     	    ##
##										##
##########################################
def DoctosInDet_manage_inlineView(request, id = None, template_name='DoctosIn_manage.html'):
	doctosInDet_formset = get_DoctosIn_items_formset(DoctosInDetManageForm, extra=1, can_delete=True)

	if id:
		doctosInI = get_object_or_404(DoctosIn, pk=id)
	else:
		doctosInI = DoctosIn()

	if request.method == 'POST':

		doctosInForm = DoctosInManageForm(request.POST, request.FILES, instance=doctosInI)
		formset = doctosInDet_formset(request.POST, request.FILES, instance=doctosInI)
		if doctosInForm.is_valid() and formset.is_valid():
			DI = doctosInForm.save(commit = False)
			if DI.id > 0:
				DI.save()
			else:
				DI.id = c_get_next_key('ID_DOCTOS')
				DI.save()
			
			for form in formset:
				did = form.save(commit = False)
				if did.id > 0:
					did.almacen = DI.almacen
					did.conceptoIn = DI.conceptoIn
					did.usuario_creador = 'JESUS'
					did.save()
				else:
					did.id = c_get_next_key('ID_DOCTOS')
					did.almacen = DI.almacen
					did.conceptoIn = DI.conceptoIn
					did.usuario_creador = 'JESUS'
					did.usuario_ult_modif = 'JESUS'
					did.save()

			return HttpResponseRedirect('/Inventarios/')
	else:
	 	doctosInForm= DoctosInManageForm(instance=doctosInI)
	 	formset = doctosInDet_formset(instance=doctosInI)
	
	return render_to_response(template_name,{'doctosInForm': doctosInForm, 'formset': formset,}, context_instance=RequestContext(request))
	
def invetarioFisico_manageView(request, id = None, template_name='inventario_fisico.html'):
	inventarioFisico_items = inventarioFisico_items_formset(DoctosInvfisDetManageForm, extra=1, can_delete=True)

	if id:
		InventarioFisico = get_object_or_404(DoctosInvfis, pk=id)
	else:
		InventarioFisico = DoctosInvfis()

	if request.method == 'POST':
		InventarioFisico_form = DoctosInvfisManageForm(request.POST, request.FILES, instance=InventarioFisico)
		InventarioFisicoItems_formset = inventarioFisico_items(request.POST, request.FILES, instance=InventarioFisico)
		if InventarioFisico_form.is_valid() and InventarioFisicoItems_formset.is_valid():
			inventarioFisico = InventarioFisico_form.save(commit = False)		
			
			#GUARDA INVENTARIO FISICO
			if inventarioFisico.id > 0:
				inventarioFisico.save()
			else:
				inventarioFisico.id = -1
				inventarioFisico.save()

			#GUARDA ARTICULOS DE INVENTARIO FISICO
			for articulo_form in InventarioFisicoItems_formset:
				
				DetalleInventarioFisico = articulo_form.save(commit = False)
				#PARA ACTUALIZAR
				if DetalleInventarioFisico.id > 0:
					DetalleInventarioFisico.save()
				#PARA CREAR UNO NUEVO
				else:
					DetalleInventarioFisico.id = -1
					DetalleInventarioFisico.docto_invfis = inventarioFisico
					DetalleInventarioFisico.save()

			return HttpResponseRedirect('/')
	else:
		InventarioFisico_form = DoctosInvfisManageForm(instance=InventarioFisico)
		InventarioFisicoItems_formset = inventarioFisico_items(instance=InventarioFisico)
	
	c = {
	'InventarioFisico_form': InventarioFisico_form, 
	'InventarioFisicoItems_formset': inventarioFisico_items,
	}

	return render_to_response(template_name, c, context_instance=RequestContext(request))