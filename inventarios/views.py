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
	#= ClavesArticulos.objects.all()
	articulos = ClavesArticulos.objects.filter(articulo__id=219)
	c = {'articulos':articulos}
  	return render_to_response('index.html', c, context_instance=RequestContext(request))

def c_get_next_key(seq_name):
    """ return next value of sequence """
    c = connection.cursor()
    c.execute("SELECT GEN_ID( ID_DOCTOS , 1 ) FROM RDB$DATABASE;")
    row = c.fetchone()
    return int(row[0])

##########################################
## 										##
##        INVENTARIOS FISICOS     	    ##
##										##
##########################################

def invetariosFisicos_View(request):
	inventarios_fisicos = DoctosInvfis.objects.all()
	c = {'inventarios_fisicos':inventarios_fisicos}
	return render_to_response('inventarios_fisicos.html', c, context_instance=RequestContext(request))

def invetarioFisico_manageView(request, id = None, template_name='inventario_fisico.html'):
	msg = "nunca"
	if id:
		InventarioFisico = get_object_or_404(DoctosInvfis, pk=id)
	else:
		InventarioFisico = DoctosInvfis()
	ids=0
	if request.method == 'POST':
		InventarioFisico_form = DoctosInvfisManageForm(request.POST, request.FILES, instance=InventarioFisico)

		if 'excel' in request.POST:
			input_excel = request.FILES['file_inventario']
			book = xlrd.open_workbook(file_contents=input_excel.read())
			sheet = book.sheet_by_index(0)
			articulos = Articulos.objects.filter(es_almacenable='S')

			inventarioFisico_items = inventarioFisico_items_formset(DoctosInvfisDetManageForm, extra=articulos.count(), can_delete=True)
			
			lista = []
			lista_articulos = []		

			for i in range(sheet.nrows):
				clave_articulo = get_object_or_404(ClavesArticulos, clave=sheet.cell_value(i,0))
				if clave_articulo and clave_articulo.articulo.es_almacenable=='S':
					lista.append({'articulo': clave_articulo.articulo, 'clave':clave_articulo.clave, 'unidades':int(sheet.cell_value(i,1)),})
					lista_articulos.append(clave_articulo.articulo.id)
			
			articulos_enceros = Articulos.objects.exclude(pk__in=lista_articulos).filter(es_almacenable='S')
			
			for i in articulos_enceros:
				
				#clave_articulo = ClavesArticulos.objects.filter(articulo__id=i.id)
				articulosclav = ClavesArticulos.objects.filter(articulo__id=i.id)
				if articulosclav:
					lista.append({'articulo': i, 'clave':articulosclav[0].clave , 'unidades':0,})	
				else:
					lista.append({'articulo': i, 'clave':'', 'unidades':0,})	

			InventarioFisicoItems_formset = inventarioFisico_items(
				initial=lista
				)

		else:
			inventarioFisico_items = inventarioFisico_items_formset(DoctosInvfisDetManageForm, extra=1, can_delete=True)
			InventarioFisicoItems_formset = inventarioFisico_items(request.POST, request.FILES, instance=InventarioFisico)
			if InventarioFisico_form.is_valid() and InventarioFisicoItems_formset.is_valid():
				inventarioFisico = InventarioFisico_form.save(commit = False)
				
				#GUARDA INVENTARIO FISICO
				if inventarioFisico.id > 0:
					inventarioFisico.save()
				else:
					inventarioFisico.id = c_get_next_key('ID_DOCTOS')
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

				return HttpResponseRedirect('/InventariosFisicos/')
	else:
		inventarioFisico_items = inventarioFisico_items_formset(DoctosInvfisDetManageForm, extra=1, can_delete=True)
		InventarioFisico_form= DoctosInvfisManageForm(instance=InventarioFisico)
	 	InventarioFisicoItems_formset = inventarioFisico_items(instance=InventarioFisico)
	
	c = {'InventarioFisico_form': InventarioFisico_form, 'formset': InventarioFisicoItems_formset, 'msg':msg,}

	return render_to_response(template_name, c, context_instance=RequestContext(request))

def invetarioFisico_delete(request, id = None):
	inventario_fisico = get_object_or_404(DoctosInvfis, pk=id)
	inventario_fisico.delete()

	return HttpResponseRedirect('/InventariosFisicos/')

def articulos_invetarioFisico_delete(request, id = None):
	articulo_inventarioFisico = get_object_or_404(DoctosInvfisDet, pk=id)
	articulo_inventarioFisico.delete()

	return HttpResponseRedirect('/InventariosFisicos/')