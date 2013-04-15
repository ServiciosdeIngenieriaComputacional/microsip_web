#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from inventarios.models import *
from models import *
from forms import *
import datetime, time
from django.db.models import Q
from datetime import timedelta

from django.core import serializers
#Paginacion

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# user autentication
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Max
from django.db import connection
from inventarios.views import c_get_next_key


##########################################
## 										##
##              POLIZAS           	    ##
##										##
##########################################

@login_required(login_url='/login/')
def preferenciasEmpresa_View(request, template_name='herramientas/preferencias_empresa.html'):
	try:
		informacion_contable = InformacionContable_V.objects.all()[:1]
		informacion_contable = informacion_contable[0]
	except:
		informacion_contable = InformacionContable_V()

	msg = ''
	if request.method == 'POST':
		form = InformacionContableManageForm(request.POST, instance=informacion_contable)
		if form.is_valid():
			form.save()
			msg = 'Datos Guardados Exitosamente'
	else:
		form = InformacionContableManageForm(instance=informacion_contable)

	plantillas = PlantillaPolizas_V.objects.all()

	c= {'form':form,'msg':msg,'plantillas':plantillas,}
	return render_to_response(template_name, c, context_instance=RequestContext(request))

def get_descuento_total_ve(facturaID):
	c = connection.cursor()
	c.execute("SELECT SUM(A.dscto_arts + A.dscto_extra_importe) AS TOTAL FROM CALC_TOTALES_DOCTO_VE(%s,'S') AS  A;"% facturaID)
	row = c.fetchone()
	return int(row[0])

def get_folio_poliza(tipo_poliza, fecha=None):
	""" folio de una poliza """
	try:
		if tipo_poliza.tipo_consec == 'M':
			tipo_poliza_det = TipoPolizaDet.objects.get(tipo_poliza = tipo_poliza, mes=fecha.month, ano = fecha.year)
		elif tipo_poliza.tipo_consec == 'E':
			tipo_poliza_det = TipoPolizaDet.objects.get(tipo_poliza = tipo_poliza, ano=fecha.year, mes=0)
		elif tipo_poliza.tipo_consec == 'P':
			tipo_poliza_det = TipoPolizaDet.objects.get(tipo_poliza = tipo_poliza, mes=0, ano =0)
	except ObjectDoesNotExist:
		if tipo_poliza.tipo_consec == 'M':		
			tipo_poliza_det = TipoPolizaDet.objects.create(id=c_get_next_key('ID_CATALOGOS'), tipo_poliza=tipo_poliza, ano=fecha.year, mes=fecha.month, consecutivo = 1,)
		elif tipo_poliza.tipo_consec == 'E':
			#Si existe permanente toma su consecutivo para crear uno nuevo si no existe inicia en 1
			consecutivo = TipoPolizaDet.objects.filter(tipo_poliza = tipo_poliza, mes=0, ano =0).aggregate(max = Sum('consecutivo'))['max']

			if consecutivo == None:
				consecutivo = 1

			tipo_poliza_det = TipoPolizaDet.objects.create(id=c_get_next_key('ID_CATALOGOS'), tipo_poliza=tipo_poliza, ano=fecha.year, mes=0, consecutivo=consecutivo,)
		elif tipo_poliza.tipo_consec == 'P':
			consecutivo = TipoPolizaDet.objects.all().aggregate(max = Sum('consecutivo'))['max']

			if consecutivo == None:
				consecutivo = 1

			tipo_poliza_det = TipoPolizaDet.objects.create(id=c_get_next_key('ID_CATALOGOS'), tipo_poliza=tipo_poliza, ano=0, mes=0, consecutivo = consecutivo,)								

	return tipo_poliza_det

def get_totales_doctos_ve(cuenta_contado= None, documento= None, conceptos_poliza=None, totales_cuentas=None, msg='', error='', depto_co):	
	#Si es una factura
	if documento.tipo = 'F':
		campos_particulares = LibresFacturasV.objects.filter(pk=documento.id)[0]
	#Si es una devolucion
	elif documento.tipo = 'D':
		campos_particulares = LibresDevFacV.objects.filter(pk=documento.id)[0]

	try:
		cuenta_cliente =  CuentaCo.objects.get(cuenta=documento.cliente.cuenta_xcobrar).cuenta
	except ObjectDoesNotExist:
		cuenta_cliente = None
		error = 1
		msg ='no se encontro el cliente'

	#Para saber si es contado o es credito
	es_contado = documento.condicion_pago == cuenta_contado

	impuestos 			= documento.total_impuestos * documento.tipo_cambio
	importe_neto 		= documento.importe_neto * documento.tipo_cambio
	total 				= impuestos + importe_neto
	descuento 			= get_descuento_total_ve(documento.id) * documento.tipo_cambio
	clientes 			= total - descuento
	bancos 				= 0
	ventas_0 			= DoctoVeDet.objects.filter(docto_ve= factura).extra(
			tables =['impuestos_articulos', 'impuestos'],
			where =
			[
				"impuestos_articulos.ARTICULO_ID = doctos_ve_det.ARTICULO_ID",
				"impuestos.IMPUESTO_ID = impuestos_articulos.IMPUESTO_ID",
				"impuestos.PCTJE_IMPUESTO = 0 ",
			],
		).aggregate(ventas_0 = Sum('precio_total_neto'))
	->>>>>>>>>>>>>>>>>>>>aqui me quede
	ventas_16      	= 0
	ventas_16_credito 	= 0
	ventas_0_credito	= 0
	ventas_16_contado 	= 0
	ventas_0_contado	= 0
	iva_pend_pagar 		= 0
	iva_efec_pagado 	= 0

	return totales_cuentas, error, msg

def get_totales_factura(factura, es_contado=None, totales=None, ):
	msg = totales['msg']
	error = totales['error']

	ventas_16_credito = ventas_0_credito = iva_pend_cobrar = clientes = 0
	ventas_16_contado = ventas_0_contado = iva_efec_cobrado = bancos  = 0

	descuento_total 		= get_descuento_total_ve(factura.id) * factura.tipo_cambio
	total 					= (factura.total_impuestos * factura.tipo_cambio) + (factura.importe_neto * factura.tipo_cambio)
	ventas_0 = DoctoVeDet.objects.filter(docto_ve= factura).extra(
			tables =['impuestos_articulos', 'impuestos'],
			where =
			[
				"impuestos_articulos.ARTICULO_ID = doctos_ve_det.ARTICULO_ID",
				"impuestos.IMPUESTO_ID = impuestos_articulos.IMPUESTO_ID",
				"impuestos.PCTJE_IMPUESTO = 0 ",
			],
		).aggregate(ventas_0 = Sum('precio_total_neto'))
	
	if ventas_0['ventas_0'] == None:
		ventas_0 = 0 
	else:
		ventas_0 = ventas_0['ventas_0']* factura.tipo_cambio
		
	ventas_16 = total - ventas_0 - factura.total_impuestos * factura.tipo_cambio

	if ventas_16 < 0:
		ventas_0 += ventas_16
		ventas_16 = 0
		msg = 'Existe al menos una factura donde el cliente [no tiene indicado cobrar inpuestos] POR FAVOR REVISTA ESO!!'
		if crear_polizas_por == 'Dia':
			msg = '%s, REVISA LAS POLIZAS QUE SE CREARON'% msg 

		error = 1

	#SI LA FACTURA ES A CREDITO
	if not es_contado:
		ventas_16_credito 	= ventas_16
		ventas_0_credito 	= ventas_0
		iva_pend_cobrar 	= factura.total_impuestos * factura.tipo_cambio
		clientes 			= total - descuento_total
	elif es_contado:
		ventas_16_contado 	= ventas_16
		ventas_0_contado	= ventas_0
		iva_efec_cobrado 	= factura.total_impuestos * factura.tipo_cambio
		bancos 				= total - descuento_total

	return {
		'descuento_total'	: totales['descuento_total'] + descuento_total,
		'total'				: totales['total']+total,
		'ventas_16_credito' : totales['ventas_16_credito']+ ventas_16_credito,
		'ventas_0_credito' 	: totales['ventas_0_credito'] + ventas_0_credito,
		'iva_pend_cobrar' 	: totales['iva_pend_cobrar'] + iva_pend_cobrar,
		'clientes' 			: totales['clientes']+clientes,
		'ventas_16_contado' : totales['ventas_16_contado'] + ventas_16_contado,
		'ventas_0_contado' 	: totales['ventas_0_contado'] + ventas_0_contado,
		'iva_efec_cobrado' 	: totales['iva_efec_cobrado'] + iva_efec_cobrado,
		'bancos'			: totales['bancos'] + bancos,
		'error'				: error,
		'msg'				: msg,
	}

def crear_polizas(facturas, depto_co, informacion_contable, prefijo, msg, plantilla=None, descripcion = '', crear_polizas_por='',crear_polizas_de=None, tipo_poliza=''):
	facturasData 		= []
	cuenta 				= ''
	conceptos_poliza	= DetallePlantillaPolizas_V.objects.filter(plantilla_poliza_v=plantilla).order_by('id')
	
	totales_factura = {
		'descuento_total'	: 0, 'total'				: 0, 'ventas_16_credito' : 0, 'ventas_0_credito' 	: 0,
		'iva_pend_cobrar' 	: 0, 'clientes' 			: 0, 'ventas_16_contado' : 0, 'ventas_0_contado' 	: 0,
		'iva_efec_cobrado' 	: 0, 'iva_total'			: 0, 'bancos'			 : 0, 'error'				: 0, 'msg'				: msg,
	}

	moneda_local = get_object_or_404(Moneda,es_moneda_local='S')

	factura_numero = 0
	for factura_no, factura in enumerate(facturas):
		es_contado = factura.condicion_pago == informacion_contable.condicion_pago_contado

		siguente_fatura = facturas[(factura_no +1)%len(facturas)]
		factura_numero = factura_no

		totales_factura = get_totales_factura(factura, es_contado, totales_factura)

		if totales_factura['error'] == 0:
			
			#Cuando la fecha de la factura siguiente sea diferente y sea por DIA, o sea la ultima
			if (not factura.fecha == siguente_fatura.fecha and crear_polizas_por == 'Dia') or factura_no +1 == len(facturas) or crear_polizas_por == 'Documento':

				if 	tipo_poliza == 'F':
					tipo_poliza = informacion_contable.tipo_poliza_ve
				elif tipo_poliza == 'D': 
					tipo_poliza = informacion_contable.tipo_poliza_dev

				tipo_poliza_det = get_folio_poliza(tipo_poliza, factura.fecha)

				poliza = DoctoCo(
						id                    	= c_get_next_key('ID_DOCTOS'),
						tipo_poliza				= tipo_poliza,
						poliza					= '%s%s'% (prefijo,("%09d" % tipo_poliza_det.consecutivo)[len(prefijo):]),
						fecha 					= factura.fecha,
						moneda 					= moneda_local, 
						tipo_cambio 			= 1,
						estatus 				= 'P', cancelado= 'N', aplicado = 'N', ajuste = 'N', integ_co = 'S',
						descripcion 			= descripcion,
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
				
				#CONSECUTIVO DE FOLIO DE POLIZA
				tipo_poliza_det.consecutivo += 1 
				tipo_poliza_det.save()

				posicion = 1
				for concepto in conceptos_poliza:
					importe = 0
					cuenta = []

					if concepto.valor_tipo == 'Ventas': 
						if concepto.valor_contado_credito == 'Credito':
							if concepto.valor_iva == '0':
								importe = totales_factura['ventas_0_credito']
							elif concepto.valor_iva == 'I':
								importe = totales_factura['ventas_16_credito']
							elif concepto.valor_iva == 'A':
								importe = totales_factura['ventas_16_credito'] + totales_factura['ventas_0_credito']
						elif concepto.valor_contado_credito == 'Contado':
							if concepto.valor_iva == '0':
								importe = totales_factura['ventas_0_contado']
							elif concepto.valor_iva == 'I':
								importe = totales_factura['ventas_16_contado']
							elif concepto.valor_iva == 'A':
								importe = totales_factura['ventas_16_contado'] + totales_factura['ventas_0_contado']
						elif concepto.valor_contado_credito == 'Ambos':
							if concepto.valor_iva == '0':
								importe = totales_factura['ventas_0_credito'] + totales_factura['ventas_0_contado']
							elif concepto.valor_iva == 'I':
								importe = totales_factura['ventas_16_credito'] + totales_factura['ventas_16_contado']
							elif concepto.valor_iva == 'A':
								importe =totales_factura['ventas_0_credito'] + totales_factura['ventas_0_contado'] + totales_factura['ventas_16_credito'] + totales_factura['ventas_16_contado']

						cuenta = concepto.cuenta_co
					#SI ES A CREDITO y ES CLIENTES
					elif concepto.valor_tipo == 'Clientes': 
						if concepto.valor_iva == '0':
							importe = 0
						elif concepto.valor_iva == 'I':
							importe = 0
						elif concepto.valor_iva == 'A':
							importe = totales_factura['clientes']

						cuenta = concepto.cuenta_co
					#SI ES BANCOS Y ES DE CONTADO
					elif concepto.valor_tipo == 'Bancos':
						if concepto.valor_iva == '0':
							importe = 0
						elif concepto.valor_iva == 'I':
							importe = 0
						elif concepto.valor_iva == 'A':
							importe = totales_factura['bancos']

						cuenta = concepto.cuenta_co

					elif concepto.valor_tipo == 'Descuentos':
						importe = totales_factura['descuento_total']
						cuenta = concepto.cuenta_co

					elif concepto.valor_tipo == 'IVA':
						if concepto.valor_contado_credito == 'Credito':
							importe = totales_factura['iva_pend_cobrar']
						elif concepto.valor_contado_credito == 'Contado':
							importe = totales_factura['iva_efec_cobrado']
						elif concepto.valor_contado_credito == 'Ambos':
							importe = totales_factura['iva_pend_cobrar'] + totales_factura['iva_efec_cobrado']

						cuenta = concepto.cuenta_co
							
					if importe > 0 and not cuenta == []:
						DoctosCoDet.objects.create(
							id				= -1,
							docto_co		= poliza,
							cuenta			= cuenta,
							depto_co		= depto_co,
							tipo_asiento	= concepto.tipo,
							importe			= importe,
							importe_mn		= 0,#PENDIENTE
							ref				= '',
							descripcion		= '',
							posicion		= posicion,
							recordatorio	= None,
							fecha			= factura.fecha,
							cancelado		= 'N', aplicado = 'N', ajuste = 'N', 
							moneda			= moneda_local,
						)
						posicion +=1

				facturasData.append ({
					'folio'		:poliza.poliza,
					'total'		:totales_factura['total'],
					'ventas_0'	:totales_factura['ventas_0_credito'] + totales_factura['ventas_0_contado'],
					'ventas_16'	:totales_factura['ventas_16_credito'] + totales_factura['ventas_16_contado'],
					'impuesos'	:totales_factura['iva_pend_cobrar'] + totales_factura['iva_efec_cobrado'],
					'tipo_cambio':1,
					})
				
				totales_factura = {
					'descuento_total'	: 0,
					'total'				: 0,
					'ventas_16_credito' : 0,
					'ventas_0_credito' 	: 0,
					'iva_pend_cobrar' 	: 0,
					'clientes' 			: 0,
					'ventas_16_contado' : 0,
					'ventas_0_contado' 	: 0,
					'iva_efec_cobrado' 	: 0,
					'iva_total'			: 0,
					'bancos'			: 0,
					'error'				: 0,
					'msg'				: msg,
				}

			factura.contabilizado = 'S'
			factura.save()
	return totales_factura['msg'], facturasData

def generar_polizas(fecha_ini=None, fecha_fin=None, ignorar_facturas_cont=True, crear_polizas_por='Documento', crear_polizas_de='', plantilla='', plantilla_devoluciones='', descripcion= ''):
	error 	= 0
	msg		= ''
	facturasData = []
	
	try:
		informacion_contable = InformacionContable_V.objects.all()[:1]
		informacion_contable = informacion_contable[0]
	except ObjectDoesNotExist:
		error = 1
	
	#Si estadefinida la informacion contable no hay error!!!
	if error == 0:

		facturas = []
		if ignorar_facturas_cont:
			if crear_polizas_de 	== 'F' or crear_polizas_de 	== 'FD':
				facturas 			= DoctoVe.objects.filter(Q(estado='N')|Q(estado='D'), tipo ='F', contabilizado ='N',  fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
			elif crear_polizas_de 	== 'D' or crear_polizas_de 	== 'FD':
				devoluciones 		= DoctoVe.objects.filter(estado = 'N').filter(tipo 	='D', contabilizado ='N',  fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
		else:
			if crear_polizas_de 	== 'F' or crear_polizas_de 	== 'FD':
				facturas 			= DoctoVe.objects.filter(Q(estado='N')|Q(estado='D'), tipo ='F', fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
			elif crear_polizas_de 	== 'D' or crear_polizas_de 	== 'FD':
				devoluciones 		= DoctoVe.objects.filter(estado = 'N').filter(tipo 	= 'D', fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
			
		#PREFIJO
		prefijo = informacion_contable.tipo_poliza_ve.prefijo
		if not informacion_contable.tipo_poliza_ve.prefijo:
			prefijo = ''

		if crear_polizas_por =='Dia' or crear_polizas_por =='Periodo' or crear_polizas_por =='Documento':
			if crear_polizas_de 	== 'F' or crear_polizas_de 	== 'FD':
				msg, facturasData = crear_polizas(facturas, informacion_contable.depto_general_cont, informacion_contable, prefijo, msg , plantilla, descripcion, crear_polizas_por, crear_polizas_de, 'F')
			
			if crear_polizas_de 	== 'D' or crear_polizas_de 	== 'FD':
				msg, devolucionesData = crear_polizas(devoluciones, informacion_contable.depto_general_cont, informacion_contable, prefijo, msg, plantilla_devoluciones, descripcion, crear_polizas_por, crear_polizas_de, 'D')
	
	elif error == 1:
		msg = 'No se han derfinido las preferencias de la empresa para generar polizas [Por favor definelas primero en Configuracion > Preferencias de la empresa]'

	return facturasData, msg

@login_required(login_url='/login/')
def facturas_View(request, template_name='herramientas/generar_polizas.html'):
	facturasData = []
	msg 			= ''
	if request.method == 'POST':
		form = GenerarPolizasManageForm(request.POST)
		if form.is_valid():
			fecha_ini 				= form.cleaned_data['fecha_ini']
			fecha_fin 				= form.cleaned_data['fecha_fin']
			ignorar_facturas_cont 	= form.cleaned_data['ignorar_facturas_cont']
			crear_polizas_por 		= form.cleaned_data['crear_polizas_por']
			crear_polizas_de 		= form.cleaned_data['crear_polizas_de']
			plantilla_facturas 		= form.cleaned_data['plantilla']
			plantilla_devoluciones = form.cleaned_data['plantilla_2']
			descripcion 			= form.cleaned_data['descripcion']

			msg = 'es valido'
			facturasData, msg = generar_polizas(fecha_ini, fecha_fin, ignorar_facturas_cont, crear_polizas_por, crear_polizas_de, plantilla_facturas, plantilla_devoluciones, descripcion)
	else:
		form = GenerarPolizasManageForm()

	c = {'facturas':facturasData,'msg':msg,'form':form,}
	return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def plantilla_poliza_manageView(request, id = None, template_name='herramientas/plantilla_poliza.html'):
	message = ''

	if id:
		plantilla = get_object_or_404(PlantillaPolizas_V, pk=id)
	else:
		plantilla =PlantillaPolizas_V()

	if request.method == 'POST':
		plantilla_form = PlantillaPolizaManageForm(request.POST, request.FILES, instance=plantilla)

		plantilla_items 		= PlantillaPoliza_items_formset(ConceptoPlantillaPolizaManageForm, extra=1, can_delete=True)
		plantilla_items_formset = plantilla_items(request.POST, request.FILES, instance=plantilla)
		
		if plantilla_form.is_valid() and plantilla_items_formset .is_valid():
			plantilla = plantilla_form.save(commit = False)
			plantilla.save()

			#GUARDA CONCEPTOS DE PLANTILLA
			for concepto_form in plantilla_items_formset :
				Detalleplantilla = concepto_form.save(commit = False)
				#PARA CREAR UNO NUEVO
				if not Detalleplantilla.id:
					Detalleplantilla.plantilla_poliza_v = plantilla
			
			plantilla_items_formset .save()
			return HttpResponseRedirect('/ventas/PreferenciasEmpresa/')
	else:
		plantilla_items = PlantillaPoliza_items_formset(ConceptoPlantillaPolizaManageForm, extra=1, can_delete=True)
		plantilla_form= PlantillaPolizaManageForm(instance=plantilla)
	 	plantilla_items_formset  = plantilla_items(instance=plantilla)
	
	c = {'plantilla_form': plantilla_form, 'formset': plantilla_items_formset , 'message':message,}

	return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def plantilla_poliza_delete(request, id = None):
	plantilla = get_object_or_404(PlantillaPolizas_V, pk=id)
	plantilla.delete()

	return HttpResponseRedirect('/ventas/PreferenciasEmpresa/')

