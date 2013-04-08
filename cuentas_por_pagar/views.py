#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from inventarios.models import *
from cuentas_por_pagar.forms import *
from ventas.views import get_folio_poliza

import datetime, time
from django.db.models import Q
#Paginacion

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# user autentication
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Max
from django.db import connection
from inventarios.views import c_get_next_key
import ventas 

@login_required(login_url='/login/')
def preferenciasEmpresa_View(request, template_name='herramientas/preferencias_empresa_CP.html'):
	try:
		informacion_contable = InformacionContable_CP.objects.all()[:1]
		informacion_contable = informacion_contable[0]
	except:
		informacion_contable = InformacionContable_CP()

	msg = ''
	if request.method == 'POST':
		form = InformacionContableManageForm(request.POST, instance=informacion_contable)
		if form.is_valid():
			form.save()
			msg = 'Datos Guardados Exitosamente'
	else:
		form = InformacionContableManageForm(instance=informacion_contable)

	plantillas = PlantillaPolizas_CP.objects.all()
	c= {'form':form,'msg':msg,'plantillas':plantillas,}
	return render_to_response(template_name, c, context_instance=RequestContext(request))

def get_totales_documento_cp(documento, es_contado=None, totales=None):
	msg = totales['msg']
	error = totales['error']
	importesDocto = ImportesDoctosCP.objects.filter(docto_cp=documento)[0]

	compras_16_credito = compras_0_credito = iva_pend_pagar 	= proveedores 	= compras_0 	= 0
	compras_16_contado = compras_0_contado = iva_efec_pagado 	= bancos  		= compras_16 	= 0

	descuento_total 		= 0
	total 					= (importesDocto.total_impuestos * documento.tipo_cambio) + (importesDocto.importe_neto * documento.tipo_cambio)
	
	if importesDocto.total_impuestos <= 0:
		compras_0 = importesDocto.importe_neto * documento.tipo_cambio
	else:
		compras_16 = importesDocto.importe_neto * documento.tipo_cambio

	#si llega a  haber un proveedor que no tenga cargar impuestos
	if compras_16 < 0:
		compras_0 += compras_16
		compras_16 = 0
		msg = 'Existe al menos una documento donde el proveedor [no tiene indicado cargar inpuestos] POR FAVOR REVISTA ESO!!'
		if crear_polizas_por == 'Dia':
			msg = '%s, REVISA LAS POLIZAS QUE SE CREARON'% msg 

		error = 1
	impuestos = importesDocto.total_impuestos
	tipo_cambio = documento.tipo_cambio
	tot_impuestos =impuestos * tipo_cambio
	#SI LA documento ES A CREDITO
	
	if not es_contado:
		compras_16_credito 	= compras_16
		compras_0_credito 	= compras_0
		iva_pend_pagar 		= tot_impuestos
		proveedores 		= total - descuento_total
	elif es_contado:
		compras_16_contado 	= compras_16
		compras_0_contado	= compras_0
		iva_efec_pagado 	= tot_impuestos
		proveedores 		= total - descuento_total
	
	return {
		'descuento_total'	: totales['descuento_total'] + descuento_total,
		'total'				: totales['total']+total,
		'compras_16_credito': totales['compras_16_credito']+ compras_16_credito,
		'compras_0_credito' : totales['compras_0_credito'] + compras_0_credito,
		'iva_pend_pagar' 	: totales['iva_pend_pagar'] + iva_pend_pagar,
		'proveedores' 		: totales['proveedores']+proveedores,
		'compras_16_contado': totales['compras_16_contado'] + compras_16_contado,
		'compras_0_contado' : totales['compras_0_contado'] + compras_0_contado,
		'iva_efec_pagado' 	: totales['iva_efec_pagado'] + iva_efec_pagado,
		'bancos'			: totales['bancos'] + bancos,
		'error'				: error,
		'msg'				: msg,
	}

def crear_polizas(documentos, depto_co, informacion_contable, msg, plantilla=None, descripcion = '', crear_polizas_por='',crear_polizas_de=None,):
	
	DocumentosData 		= []
	cuenta 				= ''
	conceptos_poliza	= DetallePlantillaPolizas_CP.objects.filter(plantilla_poliza_CP=plantilla).order_by('id')
	
	totales_documento = {
		'descuento_total'	: 0, 'total'				: 0, 'compras_16_credito' : 0, 'compras_0_credito' 	: 0,
		'iva_pend_pagar' 	: 0, 'proveedores' 			: 0, 'compras_16_contado' : 0, 'compras_0_contado' 	: 0,
		'iva_efec_pagado' 	: 0, 'iva_total'			: 0, 'bancos'			 : 0, 'error'				: 0, 'msg'				: msg,
	}

	departamentos = []
	importes = []
	fletes_departamentos = []
	fletes_importes = []
	moneda_local = get_object_or_404(Moneda,es_moneda_local='S')
	documento_numero = 0
	polizas = []
	detalles_polizas = []
	
	for documento_no, documento in enumerate(documentos):
		
		if documento.naturaleza_concepto == 'C':
			es_contado = documento.condicion_pago == informacion_contable.condicion_pago_contado
		else:
			es_contado = False

		siguente_documento = documentos[(documento_no +1)%len(documentos)]
		documento_numero = documento_no

		totales_documento = get_totales_documento_cp(documento, es_contado, totales_documento)
		departamentos = importes = fletes_departamentos =fletes_importes = []

		if totales_documento['error'] == 0:
		
			#Cuando la fecha de la documento siguiente sea diferente y sea por DIA, o sea la ultima
			if (not documento.fecha == siguente_documento.fecha and crear_polizas_por == 'Dia') or documento_no +1 == len(documentos) or crear_polizas_por == 'Documento':

				tipo_poliza = TipoPoliza.objects.filter(clave=documento.concepto.clave_tipo_poliza)[0]
				tipo_poliza_det = get_folio_poliza(tipo_poliza, documento.fecha)

				campos_particulares = LibresCargosCP.objects.filter(pk=documento.id)[0]

				if not campos_particulares.departamentos == None:
					departamentos = campos_particulares.departamentos.split(',')
				if not campos_particulares.importes == None:
					importes = campos_particulares.importes.split(',')
				if not campos_particulares.fletes_departamentos == None:
					fletes_departamentos = campos_particulares.fletes_departamentos.split(',')
				if not campos_particulares.fletes_importes == None:
					fletes_importes = campos_particulares.fletes_importes.split(',')
				
				#PREFIJO
				prefijo = tipo_poliza.prefijo
				if not tipo_poliza.prefijo:
					prefijo = ''
				
				try:
					cuenta_proveedor =  CuentaCo.objects.get(cuenta=documento.proveedor.cuenta_xpagar)

				except ObjectDoesNotExist:
					cuenta_proveedor = None

				
				#Si no tiene una descripcion el documento se pone lo que esta indicado en la descripcion general
				descripcion_doc = documento.descripcion
				if documento.descripcion == None or crear_polizas_por=='Dia':
					descripcion_doc = descripcion

				referencia = documento.folio
				if crear_polizas_por == 'Dia':
					referencia = ''

				poliza = DoctoCo(
						id                    	= c_get_next_key('ID_DOCTOS'),
						tipo_poliza				= tipo_poliza,
						poliza					= '%s%s'% (prefijo,("%09d" % tipo_poliza_det.consecutivo)[len(prefijo):]),
						fecha 					= documento.fecha,
						moneda 					= moneda_local, 
						tipo_cambio 			= 1,
						estatus 				= 'P', cancelado= 'N', aplicado = 'N', ajuste = 'N', integ_co = 'S',
						descripcion 			= descripcion_doc,
						forma_emitida 			= 'N', sistema_origen = 'CO',
						nombre 					= '',
						grupo_poliza_periodo 	= None,
						integ_ba 				= 'N',
						usuario_creador			= 'SYSDBA',
						fechahora_creacion		= datetime.datetime.now(), usuario_aut_creacion = None, 
						usuario_ult_modif 		= 'SYSDBA', fechahora_ult_modif = datetime.datetime.now(), usuario_aut_modif 	= None,
						usuario_cancelacion 	= None, fechahora_cancelacion 	=  None, usuario_aut_cancelacion 				= None,
					)
				

				polizas.append(poliza)
				#GUARDA LA PILIZA
				#poliza_o = poliza.save()
				
				#CONSECUTIVO DE FOLIO DE POLIZA
				tipo_poliza_det.consecutivo += 1 
				tipo_poliza_det.save()

				posicion = 1
				for concepto in conceptos_poliza:
					importe = 0
					cuenta = []

					if concepto.valor_tipo == 'Compras': 
						if concepto.valor_contado_credito == 'Credito':
							if concepto.valor_iva == '0':
								importe = totales_documento['compras_0_credito']
							elif concepto.valor_iva == 'I':
								importe = totales_documento['compras_16_credito']
							elif concepto.valor_iva == 'A':
								importe = totales_documento['compras_16_credito'] + totales_documento['compras_0_credito']
						elif concepto.valor_contado_credito == 'Contado':
							if concepto.valor_iva == '0':
								importe = totales_documento['compras_0_contado']
							elif concepto.valor_iva == 'I':
								importe = totales_documento['compras_16_contado']
							elif concepto.valor_iva == 'A':
								importe = totales_documento['compras_16_contado'] + totales_documento['compras_0_contado']+totales_documento['compras_16_credito'] + totales_documento['compras_0_credito']
						elif concepto.valor_contado_credito == 'Ambos':
							
							if not importes  == []:
								for depto, impor in zip(departamentos,importes):
									importe = impor

									cuenta = concepto.cuenta_co

									try:
										depto = DeptoCo.objects.get(clave=depto)
										if importe > 0 and not cuenta == []:
											detalle_poliza = DoctosCoDet(
												id				= -1,
												docto_co		= poliza,
												cuenta			= cuenta,
												depto_co		= depto,
												tipo_asiento	= concepto.tipo,
												importe			= importe,
												importe_mn		= 0,#PENDIENTE
												ref				= referencia,
												descripcion		= '',
												posicion		= posicion,
												recordatorio	= None,
												fecha			= documento.fecha,
												cancelado		= 'N', aplicado = 'N', ajuste = 'N', 
												moneda			= moneda_local,
											)
											posicion +=1
											detalles_polizas.append(detalle_poliza)

									except ObjectDoesNotExist:
										importe = 0
										cuenta = 0
								importe = 0
								cuenta = 0
							else:
								
								if concepto.valor_iva == '0':
									importe = totales_documento['compras_0_credito'] + totales_documento['compras_0_contado']
								elif concepto.valor_iva == 'I':
									importe = totales_documento['compras_16_credito'] + totales_documento['compras_16_contado']
								elif concepto.valor_iva == 'A':
									importe =totales_documento['compras_0_credito'] + totales_documento['compras_0_contado'] + totales_documento['compras_16_credito'] + totales_documento['compras_16_contado']

								cuenta = concepto.cuenta_co
								folio_doc = documento.folio


						
					#SI ES A CREDITO y ES proveedores
					elif concepto.valor_tipo == 'Proveedores': 
						
						if concepto.valor_iva == '0':
							importe = 0
						elif concepto.valor_iva == 'I':
							importe = 0
						elif concepto.valor_iva == 'A':
							importe = totales_documento['proveedores']

						if cuenta_proveedor == None:
							cuenta = concepto.cuenta_co
						else:
							cuenta = cuenta_proveedor

					#SI ES BANCOS Y ES DE CONTADO

					elif concepto.valor_tipo == 'Fletes':
						if not importes == []:
							for depto, impor in zip(fletes_departamentos,fletes_importes):
								importe = impor
								cuenta = concepto.cuenta_co
								try:
									depto = DeptoCo.objects.get(clave=depto)

									detalle_poliza = DoctosCoDet(
										id				= -1,
										docto_co		= poliza,
										cuenta			= cuenta,
										depto_co		= depto,
										tipo_asiento	= concepto.tipo,
										importe			= importe,
										importe_mn		= 0,#PENDIENTE
										ref				= referencia,
										descripcion		= '',
										posicion		= posicion,
										recordatorio	= None,
										fecha			= documento.fecha,
										cancelado		= 'N', aplicado = 'N', ajuste = 'N', 
										moneda			= moneda_local,
									)
									posicion +=1
									detalles_polizas.append(detalle_poliza)

								except ObjectDoesNotExist:
									importe = 0
									cuenta = 0
							
							importe = 0
							cuenta = 0
							
					elif concepto.valor_tipo == 'Bancos':
						if concepto.valor_iva == '0':
							importe = 0
						elif concepto.valor_iva == 'I':
							importe = 0
						elif concepto.valor_iva == 'A':
							importe = totales_documento['bancos']

						cuenta = concepto.cuenta_co

					elif concepto.valor_tipo == 'Descuentos':
						importe = totales_documento['descuento_total']
						cuenta = concepto.cuenta_co

					elif concepto.valor_tipo == 'IVA':
						if concepto.valor_contado_credito == 'Credito':
							importe = totales_documento['iva_pend_pagar']
						elif concepto.valor_contado_credito == 'Contado':
							importe = totales_documento['iva_efec_pagado']
						elif concepto.valor_contado_credito == 'Ambos':
							importe = totales_documento['iva_pend_pagar'] + totales_documento['iva_efec_pagado']

						cuenta = concepto.cuenta_co
							
					if importe > 0 and not cuenta == []:
						detalle_poliza = DoctosCoDet(
							id				= -1,
							docto_co		= poliza,
							cuenta			= cuenta,
							depto_co		= depto_co,
							tipo_asiento	= concepto.tipo,
							importe			= importe,
							importe_mn		= 0,#PENDIENTE
							ref				= referencia,
							descripcion		= '',
							posicion		= posicion,
							recordatorio	= None,
							fecha			= documento.fecha,
							cancelado		= 'N', aplicado = 'N', ajuste = 'N', 
							moneda			= moneda_local,
						)
						posicion +=1
						detalles_polizas.append(detalle_poliza)

				DocumentosData.append ({
					'folio'		:poliza.poliza,
					'total'		:totales_documento['total'],
					'compras_0'	:totales_documento['compras_0_credito'] + totales_documento['compras_0_contado'],
					'compras_16'	:totales_documento['compras_16_credito'] + totales_documento['compras_16_contado'],
					'impuesos'	:totales_documento['iva_pend_pagar'] + totales_documento['iva_efec_pagado'],
					'tipo_cambio':1,
					})
				
				totales_documento = {
					'descuento_total'	: 0,
					'total'				: 0,
					'compras_16_credito': 0,
					'compras_0_credito' : 0,
					'iva_pend_pagar' 	: 0,
					'proveedores' 		: 0,
					'compras_16_contado': 0,
					'compras_0_contado' : 0,
					'iva_efec_pagado' 	: 0,
					'iva_total'			: 0,
					'bancos'			: 0,
					'error'				: 0,
					'msg'				: msg,
				}

 			DoctosCp.objects.filter(id=documento.id).update(contabilizado = 'S')
	
	DoctoCo.objects.bulk_create(polizas)
	DoctosCoDet.objects.bulk_create(detalles_polizas)

	polizas = []
	detalles_polizas = []

	return totales_documento['msg'], DocumentosData

def generar_polizas(fecha_ini=None, fecha_fin=None, ignorar_documentos_cont=True, crear_polizas_por='Documento', crear_polizas_de='', plantilla='', descripcion= ''):
	
	error 	= 0
	msg		= ''
	documentosCPData = []
	
	try:
		informacion_contable = InformacionContable_CP.objects.all()[:1]
		informacion_contable = informacion_contable[0]
	except ObjectDoesNotExist:
		error = 1

	#Si estadefinida la informacion contable no hay error!!!
	if error == 0:

		if ignorar_documentos_cont:
			documentosCP  = DoctosCp.objects.filter(contabilizado ='N', concepto= crear_polizas_de , fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
		else:
			documentosCP  = DoctosCp.objects.filter(concepto= crear_polizas_de , fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
		

		msg, documentosCPData = crear_polizas(documentosCP, get_object_or_404(DeptoCo, pk=76), informacion_contable, msg , plantilla, descripcion, crear_polizas_por, crear_polizas_de)
	
	elif error == 1:
		msg = 'No se han derfinido las preferencias de la empresa para generar polizas [Por favor definelas primero en Configuracion > Preferencias de la empresa]'

	return documentosCPData, msg

@login_required(login_url='/login/')
def generar_polizas_View(request, template_name='herramientas/generar_polizas_CP.html'):
	
	documentosData 	= []
	msg 			= msg_resultados = ''

	if request.method == 'POST':
		
		form = GenerarPolizasManageForm(request.POST)
		if form.is_valid():
			fecha_ini 				= form.cleaned_data['fecha_ini']
			fecha_fin 				= form.cleaned_data['fecha_fin']
			ignorar_documentos_cont = form.cleaned_data['ignorar_documentos_cont']
			crear_polizas_por 		= form.cleaned_data['crear_polizas_por']
			crear_polizas_de 		= form.cleaned_data['crear_polizas_de']
			plantilla 				= form.cleaned_data['plantilla']
			descripcion 			= form.cleaned_data['descripcion']

			msg = 'es valido'

			documentosData, msg = generar_polizas(fecha_ini, fecha_fin, ignorar_documentos_cont, crear_polizas_por, crear_polizas_de, plantilla, descripcion)
			if documentosData == []:
				msg_resultados = 'Lo siento, no se encontraron resultados para este filtro'
	else:
		form = GenerarPolizasManageForm()

	c = {'documentos':documentosData,'msg':msg,'form':form, 'msg_resultados':msg_resultados,}
	return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def plantilla_poliza_manageView(request, id = None, template_name='herramientas/plantilla_poliza_CP.html'):
	message = ''

	if id:
		plantilla = get_object_or_404(PlantillaPolizas_CP, pk=id)
	else:
		plantilla =PlantillaPolizas_CP()

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
					Detalleplantilla.plantilla_poliza_CP = plantilla
			
			plantilla_items_formset .save()
			return HttpResponseRedirect('/cuentas_por_pagar/PreferenciasEmpresa/')
	else:
		plantilla_items = PlantillaPoliza_items_formset(ConceptoPlantillaPolizaManageForm, extra=1, can_delete=True)
		plantilla_form= PlantillaPolizaManageForm(instance=plantilla)
	 	plantilla_items_formset  = plantilla_items(instance=plantilla)
	
	c = {'plantilla_form': plantilla_form, 'formset': plantilla_items_formset , 'message':message,}

	return render_to_response(template_name, c, context_instance=RequestContext(request))



