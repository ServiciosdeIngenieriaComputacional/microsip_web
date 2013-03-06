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
from django.db.models import Sum, Max

from django.core.exceptions import ObjectDoesNotExist

##########################################
## 										##
##               LOGIN     			    ##
##										##
##########################################
def ingresar(request):
	# if not request.user.is_anonymous():
	# 	return HttpResponseRedirect('/')
	if request.method == 'POST':
		formulario = AuthenticationForm(request.POST)
		if formulario.is_valid:
			usuario = request.POST['username']
			clave = request.POST['password']
			acceso = authenticate(username=usuario, password=clave)
			if acceso is not None:
				if acceso.is_active:
					login(request, acceso)
					return HttpResponseRedirect('/InventariosFisicos/')
				else:
					return render_to_response('noactivo.html', context_instance=RequestContext(request))
			else:
				return render_to_response('login.html',{'form':formulario, 'message':'Nombre de usaurio o password no validos',}, context_instance=RequestContext(request))
	else:
		formulario = AuthenticationForm()
	return render_to_response('login.html',{'form':formulario, 'message':'',}, context_instance=RequestContext(request))

def logoutUser(request):
    logout(request)
    return HttpResponseRedirect('/')

@login_required(login_url='/login/')
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

@login_required(login_url='/login/')
def invetariosFisicos_View(request, template_name='Inventarios Fisicos/inventarios_fisicos.html'):
	inventarios_fisicos_list = DoctosInvfis.objects.all().order_by('-fecha') 

	paginator = Paginator(inventarios_fisicos_list, 15) # Muestra 5 inventarios por pagina
	page = request.GET.get('page')

	#####PARA PAGINACION##############
	try:
		inventarios_fisicos = paginator.page(page)
	except PageNotAnInteger:
	    # If page is not an integer, deliver first page.
	    inventarios_fisicos = paginator.page(1)
	except EmptyPage:
	    # If page is out of range (e.g. 9999), deliver last page of results.
	    inventarios_fisicos = paginator.page(paginator.num_pages)

	c = {'inventarios_fisicos':inventarios_fisicos}
	return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def invetarioFisico_manageView(request, id = None, template_name='Inventarios Fisicos/inventario_fisico.html'):
	message = ''
	hay_repetido = False
	if id:
		InventarioFisico = get_object_or_404(DoctosInvfis, pk=id)
	else:
		InventarioFisico = DoctosInvfis()

	if request.method == 'POST':
		InventarioFisico_form = DoctosInvfisManageForm(request.POST, request.FILES, instance=InventarioFisico)

		#PARA CARGAR DATOS DE EXCEL
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
					if clave_articulo.articulo.id in lista_articulos:
						message = 'El Articulo [%s] con clave [%s] esta repetido en el archivo de excel por favor corrigelo para continuar '% (clave_articulo.articulo.nombre, clave_articulo.clave)
						hay_repetido = True
					lista.append({'articulo': clave_articulo.articulo, 'unidades':int(sheet.cell_value(i,1)),})
					lista_articulos.append(clave_articulo.articulo.id)

			
			articulos_enceros = Articulos.objects.exclude(pk__in=lista_articulos).filter(es_almacenable='S')
			
			for i in articulos_enceros:
				
				#clave_articulo = ClavesArticulos.objects.filter(articulo__id=i.id)
				articulosclav = ClavesArticulos.objects.filter(articulo__id=i.id)
				if articulosclav:
					lista.append({'articulo': i, 'clave':articulosclav[0].clave , 'unidades':0,})	
				else:
					lista.append({'articulo': i, 'clave':'', 'unidades':0,})	

			InventarioFisicoItems_formset = inventarioFisico_items(initial=lista)
		#GUARDA CAMBIOS EN INVENTARIO FISICO
		else:
			inventarioFisico_items = inventarioFisico_items_formset(DoctosInvfisDetManageForm, extra=1, can_delete=True)
			InventarioFisicoItems_formset = inventarioFisico_items(request.POST, request.FILES, instance=InventarioFisico)
			
			if InventarioFisico_form.is_valid() and InventarioFisicoItems_formset.is_valid():
				inventarioFisico = InventarioFisico_form.save(commit = False)

				#CARGA NUEVO ID
				if not inventarioFisico.id:
					inventarioFisico.id = c_get_next_key('ID_DOCTOS')
				
				inventarioFisico.save()

				#GUARDA ARTICULOS DE INVENTARIO FISICO
				for articulo_form in InventarioFisicoItems_formset:
					DetalleInventarioFisico = articulo_form.save(commit = False)
					#PARA CREAR UNO NUEVO
					if not DetalleInventarioFisico.id:
						DetalleInventarioFisico.id = -1
						DetalleInventarioFisico.docto_invfis = inventarioFisico
				
				InventarioFisicoItems_formset.save()
				return HttpResponseRedirect('/InventariosFisicos/')
	else:
		inventarioFisico_items = inventarioFisico_items_formset(DoctosInvfisDetManageForm, extra=1, can_delete=True)
		InventarioFisico_form= DoctosInvfisManageForm(instance=InventarioFisico)
	 	InventarioFisicoItems_formset = inventarioFisico_items(instance=InventarioFisico)
	
	c = {'InventarioFisico_form': InventarioFisico_form, 'formset': InventarioFisicoItems_formset, 'message':message,}

	return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def invetarioFisico_delete(request, id = None):
	inventario_fisico = get_object_or_404(DoctosInvfis, pk=id)
	inventario_fisico.delete()

	return HttpResponseRedirect('/InventariosFisicos/')

##########################################
## 										##
##        		  ENTRADAS       	    ##
##										##
##########################################

@login_required(login_url='/login/')
def entradas_View(request, template_name='Entradas/entradas.html'):
	entradas_list = DoctosIn.objects.filter(naturaleza_concepto='E').order_by('-fecha') 

	paginator = Paginator(entradas_list, 15) # Muestra 5 inventarios por pagina
	page = request.GET.get('page')

	#####PARA PAGINACION##############
	try:
		entradas = paginator.page(page)
	except PageNotAnInteger:
	    # If page is not an integer, deliver first page.
	    entradas = paginator.page(1)
	except EmptyPage:
	    # If page is out of range (e.g. 9999), deliver last page of results.
	    entradas = paginator.page(paginator.num_pages)

	c = {'entradas':entradas}
	return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def entrada_manageView(request, id = None, template_name='Entradas/entrada.html'):
	message = ''
	hay_repetido = False
	if id:
		Entrada = get_object_or_404(DoctosIn, pk=id)
	else:
		Entrada = DoctosIn()

	if request.method == 'POST':
		Entrada_form = DoctosInManageForm(request.POST, request.FILES, instance=Entrada)

		#PARA CARGAR DATOS DE EXCEL
		if 'excel' in request.POST:
			input_excel = request.FILES['file_inventario']
			book = xlrd.open_workbook(file_contents=input_excel.read())
			sheet = book.sheet_by_index(0)
			articulos = Articulos.objects.filter(es_almacenable='S')

			Entrada_items = doctoIn_items_formset(DoctosInDetManageForm, extra=articulos.count(), can_delete=True)
			
			lista = []
			lista_articulos = []		

			for i in range(sheet.nrows):
				clave_articulo = get_object_or_404(ClavesArticulos, clave=sheet.cell_value(i,0))
				if clave_articulo and clave_articulo.articulo.es_almacenable=='S':
					if clave_articulo.articulo.id in lista_articulos:
						message = 'El Articulo [%s] esta repetido en el archivo de excel por favor corrigelo para continuar '% clave_articulo.articulo.nombre
						hay_repetido = True
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

			EntradaItems_formset = Entrada_items(initial=lista)
		#GUARDA CAMBIOS EN INVENTARIO FISICO
		else:
			Entrada_items = doctoIn_items_formset(DoctosInDetManageForm, extra=1, can_delete=True)
			EntradaItems_formset = Entrada_items(request.POST, request.FILES, instance=Entrada)
			
			if Entrada_form.is_valid() and EntradaItems_formset.is_valid():
				Entrada = Entrada_form.save(commit = False)

				#CARGA NUEVO ID
				if not Entrada.id:
					Entrada.id = c_get_next_key('ID_DOCTOS')
					Entrada.naturaleza_concepto = 'E'
				
				Entrada.save()

				#GUARDA ARTICULOS DE INVENTARIO FISICO
				for articulo_form in EntradaItems_formset:
					DetalleEntrada = articulo_form.save(commit = False)
					#PARA CREAR UNO NUEVO
					if not DetalleEntrada.id:
						DetalleEntrada.id = -1
						DetalleEntrada.almacen = Entrada.almacen
						DetalleEntrada.concepto = Entrada.concepto
						DetalleEntrada.docto_invfis = Entrada
				
				EntradaItems_formset.save()
				return HttpResponseRedirect('/Entradas/')
	else:
		Entrada_items = doctoIn_items_formset(DoctosInDetManageForm, extra=1, can_delete=True)
		Entrada_form= DoctosInManageForm(instance=Entrada)
	 	EntradaItems_formset = Entrada_items(instance=Entrada)
	
	c = {'Entrada_form': Entrada_form, 'formset': EntradaItems_formset, 'message':message,}

	return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def entrada_delete(request, id = None):
	entrada = get_object_or_404(DoctosIn, pk=id)
	entrada.delete()

	return HttpResponseRedirect('/Entradas/')

##########################################
## 										##
##        		  SALIDAS               ##
##										##
##########################################

@login_required(login_url='/login/')
def salidas_View(request, template_name='Salidas/salidas.html'):
	salidas_list = DoctosIn.objects.filter(naturaleza_concepto='S').order_by('-fecha') 

	paginator = Paginator(salidas_list, 15) # Muestra 5 inventarios por pagina
	page = request.GET.get('page')

	#####PARA PAGINACION##############
	try:
		salidas = paginator.page(page)
	except PageNotAnInteger:
	    # If page is not an integer, deliver first page.
	    salidas = paginator.page(1)
	except EmptyPage:
	    # If page is out of range (e.g. 9999), deliver last page of results.
	    salidas = paginator.page(paginator.num_pages)

	c = {'salidas':salidas}
	return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def salida_manageView(request, id = None, template_name='Salidas/salida.html'):
	message = ''
	hay_repetido = False
	if id:
		Salida = get_object_or_404(DoctosIn, pk=id)
	else:
		Salida = DoctosIn()

	if request.method == 'POST':
		Salida_form = DoctosInManageForm(request.POST, request.FILES, instance=Salida)

		#PARA CARGAR DATOS DE EXCEL
		if 'excel' in request.POST:
			input_excel = request.FILES['file_inventario']
			book = xlrd.open_workbook(file_contents=input_excel.read())
			sheet = book.sheet_by_index(0)
			articulos = Articulos.objects.filter(es_almacenable='S')

			Salida_items = doctoIn_items_formset(DoctosInDetManageForm, extra=articulos.count(), can_delete=True)
			
			lista = []
			lista_articulos = []		

			for i in range(sheet.nrows):
				clave_articulo = get_object_or_404(ClavesArticulos, clave=sheet.cell_value(i,0))
				if clave_articulo and clave_articulo.articulo.es_almacenable=='S':
					if clave_articulo.articulo.id in lista_articulos:
						message = 'El Articulo [%s] esta repetido en el archivo de excel por favor corrigelo para continuar '% clave_articulo.articulo.nombre
						hay_repetido = True
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

			SalidaItems_formset = Salida_items(initial=lista)
		#GUARDA CAMBIOS EN INVENTARIO FISICO
		else:
			Salida_items = doctoIn_items_formset(DoctosInDetManageForm, extra=1, can_delete=True)
			SalidaItems_formset = Salida_items(request.POST, request.FILES, instance=Salida)
			
			if Salida_form.is_valid() and SalidaItems_formset.is_valid():
				Salida = Salida_form.save(commit = False)

				#CARGA NUEVO ID
				if not Salida.id:
					Salida.id = c_get_next_key('ID_DOCTOS')
				
				Salida.save()

				#GUARDA ARTICULOS DE INVENTARIO FISICO
				for articulo_form in SalidaItems_formset:
					DetalleSalida = articulo_form.save(commit = False)
					#PARA CREAR UNO NUEVO
					if not DetalleSalida.id:
						DetalleSalida.id = -1
						DetalleSalida.almacen = Salida.almacen
						DetalleSalida.concepto = Salida.concepto
						DetalleSalida.docto_invfis = Salida
				
				SalidaItems_formset.save()
				return HttpResponseRedirect('/Salidas/')
	else:
		Salida_items = doctoIn_items_formset(DoctosInDetManageForm, extra=1, can_delete=True)
		Salida_form= DoctosInManageForm(instance=Salida)
	 	SalidaItems_formset = Salida_items(instance=Salida)
	
	c = {'Salida_form': Salida_form, 'formset': SalidaItems_formset, 'message':message,}

	return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def salida_delete(request, id = None):
	salida = get_object_or_404(DoctosIn, pk=id)
	salida.delete()

	return HttpResponseRedirect('/Salidas/')


													##########################################
													## 										##
													##              POLIZAS           	    ##
													##										##
													##########################################

def get_folio_poliza(tipo_poliza):
	""" folio de una poliza """
	fecha_actual = datetime.date.today()

	try:
		if tipo_poliza.tipo_consec == 'M':		
			tipo_poliza_det = TipoPolizaDet.objects.get(tipo_poliza = tipo_poliza, mes=fecha_actual.month, ano = fecha_actual.year)
		elif tipo_poliza.tipo_consec == 'E':
			tipo_poliza_det = TipoPolizaDet.objects.get(tipo_poliza = tipo_poliza, ano=fecha_actual.year, mes=0)
		elif tipo_poliza.tipo_consec == 'P':
			tipo_poliza_det = TipoPolizaDet.objects.get(tipo_poliza = tipo_poliza, mes=0, ano =0)
	except ObjectDoesNotExist:
		consecutivo = TipoPolizaDet.objects.all().aggregate(max = Sum('consecutivo'))
		consecutivo = consecutivo['max']

		if consecutivo == None:
			consecutivo = 1

		if tipo_poliza.tipo_consec == 'M':		
			tipo_poliza_det = TipoPolizaDet.objects.create(id=c_get_next_key('ID_CATALOGOS'), tipo_poliza=tipo_poliza, ano=fecha_actual.year, mes=fecha_actual.month, consecutivo = 1,)
		elif tipo_poliza.tipo_consec == 'E':
			#Si existe permanente toma su consecutivo para crear uno nuevo si no existe inicia en 1
			consecutivo = TipoPolizaDet.objects.filter(tipo_poliza = tipo_poliza, mes=0, ano =0).aggregate(max = Sum('consecutivo'))
			consecutivo = consecutivo['max']

			if consecutivo == None:
				consecutivo = 1

			tipo_poliza_det = TipoPolizaDet.objects.create(id=c_get_next_key('ID_CATALOGOS'), tipo_poliza=tipo_poliza, ano=fecha_actual.year, mes=0, consecutivo=consecutivo,)
		elif tipo_poliza.tipo_consec == 'P':
			tipo_poliza_det = TipoPolizaDet.objects.create(id=c_get_next_key('ID_CATALOGOS'), tipo_poliza=tipo_poliza, ano=0, mes=0, consecutivo = consecutivo,)								
		
	return tipo_poliza_det

def generar_polizas(fecha_ini=None, fecha_fin=None):
	fecha_actual 			= datetime.date.today()
	depto_co 				= get_object_or_404(DeptoCo, pk=2090) 
	error = 0 
	informacion_contable = []
	
	try:
		informacion_contable = InformacionContable.objects.all()[:1]
		informacion_contable = informacion_contable[0]
	except ObjectDoesNotExist:
		error = 1
	
	facturas 				= DoctoVe.objects.filter(tipo='F', contabilizado ='N', estado ='N', fecha__gt=fecha_ini, fecha__lte=fecha_fin)[:90]
	facturasData 			= []
	msg 					= ''
	
	if error == 0:
		#PREFIJO
		prefijo = informacion_contable.tipo_poliza_ve.prefijo
		if not informacion_contable.tipo_poliza_ve.prefijo:
			prefijo = ''

		#CONSECUTIVO FOLIOS
		tipo_poliza_det = get_folio_poliza(informacion_contable.tipo_poliza_ve)

		for factura in facturas:
			impuestos = factura.total_impuestos
			#SI EL CLIENTE NO TIENE NO TIENE CUENTA SE VA A PUBLICO EN GENERAL
			if not factura.cliente.cuenta_xcobrar == None:
				cuentaxcobrar =  get_object_or_404(CuentaCo, cuenta = factura.cliente.cuenta_xcobrar)
			else:
				cuentaxcobrar = informacion_contable.cuantaxcobrar

			tipo_cambio = factura.tipo_cambio
			total = factura.total_impuestos + factura.importe_neto
			total_ventas_0 = DoctoVeDet.objects.filter(docto_ve= factura).extra(
				tables =['impuestos_articulos', 'impuestos'],
				where =
				[
					"impuestos_articulos.ARTICULO_ID = doctos_ve_det.ARTICULO_ID",
					"impuestos.IMPUESTO_ID = impuestos_articulos.IMPUESTO_ID",
					"impuestos.PCTJE_IMPUESTO = 0 ",
				],
			).aggregate(ventas_0 = Sum('precio_total_neto'))

			if total_ventas_0['ventas_0'] == None:
				ventas_0 = 0 
			else:
				ventas_0 = total_ventas_0['ventas_0']

			ventas_16 = total - ventas_0 - impuestos 

			if ventas_16 < 0:
				msg = 'Existe al menos una factura del cluiente %s el cual [no tiene indicado cobrar inpuestos] por favor corrije esto para poder crear las polizas de este ciente '% factura.cliente.nombre
			else:
				id_poli = c_get_next_key('ID_DOCTOS')
				folio = '%s%s'% (prefijo,("%09d" % tipo_poliza_det.consecutivo)[len(prefijo):])

				poliza = DoctoCo(
					id                    	= id_poli,
					tipo_poliza				= informacion_contable.tipo_poliza_ve,
					poliza					= folio,
					fecha 					= datetime.date.today(),
					moneda 					= factura.moneda, 
					tipo_cambio 			= tipo_cambio,
					estatus 				= 'P', cancelado= 'N', aplicado = 'N', ajuste = 'N', integ_co = 'S',
					descripcion 			= informacion_contable.descripcion_polizas_ve,
					forma_emitida 			= 'N', sistema_origen = 'CO',
					nombre 					= '',
					grupo_poliza_periodo 	= None,
					integ_ba 				= 'N',
					usuario_creador			= 'SYSDBA',
					fechahora_creacion		= datetime.datetime.now(), usuario_aut_creacion = None, 
					usuario_ult_modif 		= 'SYSDBA', fechahora_ult_modif = datetime.datetime.now(), usuario_aut_modif 	= None,
					usuario_cancelacion 	= None, fechahora_cancelacion 	=  None, usuario_aut_cancelacion 				= None,
				)

				#GUARDA LA PILIZA
				poliza_o = poliza.save()
				#factura.contabilizado = 'S'
				#factura.save()

				contabilizado ='N'
				tipo_poliza_det.consecutivo += 1 
				
				#DEBE
				DoctosCoDet.objects.create(
						id				= -1,
						docto_co		= poliza,
						cuenta			= cuentaxcobrar,
						depto_co		=  depto_co,
						tipo_asiento	= 'C',
						importe			= total,
						importe_mn		= 0,#PENDIENTE
						ref				= factura.folio,
						descripcion		= '',
						posicion		= 1,
						recordatorio	= None,
						fecha			= datetime.date.today(),
						cancelado		= 'N', aplicado = 'N', ajuste = 'N', 
						moneda			= factura.moneda,
					)

				if not ventas_0 == 0:
					#HABER 0% en este caso el lade el id: 3414
					DoctosCoDet.objects.create(
							id				= -1,
							docto_co		= poliza,
							cuenta			= get_object_or_404(CuentaCo, pk=3414),
							depto_co		= depto_co,
							tipo_asiento	= 'A',
							importe			= ventas_0,
							importe_mn		= 0,
							ref				= factura.folio,
							descripcion		= '',
							posicion		= 2,
							recordatorio	= None,
							fecha			= datetime.date.today(),
							cancelado		= 'N', aplicado = 'N', ajuste = 'N', 
							moneda			= factura.moneda,
						)

				if not impuestos == 0:
					DoctosCoDet.objects.bulk_create([
						#HABER 16% en este caso el lade el id: 3415
						DoctosCoDet(
							id				= -1,
							docto_co		= poliza,
							cuenta			= get_object_or_404(CuentaCo, pk=3415),
							depto_co		= depto_co,
							tipo_asiento	= 'A',
							importe			= ventas_16,
							importe_mn		= 0,
							ref				= factura.folio,
							descripcion		= '',
							posicion		= 3,
							recordatorio	= None,
							fecha			= datetime.date.today(),
							cancelado		= 'N', aplicado = 'N', ajuste = 'N', 
							moneda			= factura.moneda,
						),
						#HABER IMPUESTOS en este caso el lade el id: 2178
						DoctosCoDet(
							id				= -1,
							docto_co		= poliza,
							cuenta			= get_object_or_404(CuentaCo, pk=2178),
							depto_co		= depto_co,
							tipo_asiento	= 'A',
							importe			= impuestos,
							importe_mn		= 0,
							ref				= factura.folio,
							descripcion		= '',
							posicion		= 4,
							recordatorio	= None,
							fecha			= datetime.date.today(),
							cancelado		= 'N', aplicado = 'N', ajuste = 'N', 
							moneda			= factura.moneda,
						),
					])

			
			facturasData.append ({
				'folio'		:factura.folio,
				'total'		:total,
				'ventas_0'	:ventas_0,
				'ventas_16'	:ventas_16,
				'impuesos'	:impuestos,
				'tipo_cambio':tipo_cambio,
				})

		tipo_poliza_det.save()
	elif error == 1:
		msg = 'No se han derfinido las preferencias de la empresa para generar polizas [Por favor definelas primero en Configuracion > Preferencias de la empresa]'

	return facturasData, msg

@login_required(login_url='/login/')
def facturas_View(request, template_name='facturas/facturas.html'):
	facturasData 	= []
	msg 			= ''
	if request.method == 'POST':
		form = GenerarPolizasManageForm(request.POST)
		if form.is_valid():
			fecha_ini = form.cleaned_data['fecha_ini']
			fecha_fin = form.cleaned_data['fecha_fin']
			msg = 'es valido'
			facturasData, msg  = generar_polizas(fecha_ini, fecha_fin)		
	else:
		form = GenerarPolizasManageForm()

	
	#facturasData, msg  = generar_polizas()

	c = {'facturas':facturasData,'msg':msg,'form':form,}
	return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def preferenciasEmpresa_View(request, template_name='configuracion/preferencias_empresa.html'):
	try:
		informacion_contable = InformacionContable.objects.all()[:1]
		informacion_contable = informacion_contable[0]
	except:
		informacion_contable = InformacionContable()

	msg = ''
	if request.method == 'POST':
		form = InformacionContableManageForm(request.POST, instance=informacion_contable)
		if form.is_valid():
			form.save()
			msg = 'Datos Guardados Exitosamente'
	else:
		form = InformacionContableManageForm(instance=informacion_contable)

	c= {'form':form,'msg':msg,}
	return render_to_response(template_name, c, context_instance=RequestContext(request))
