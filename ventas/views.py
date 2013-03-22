#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from inventarios.models import *
from ventas.forms import *
import datetime, time
from django.db.models import Q
from datetime import timedelta
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
		consecutivo = TipoPolizaDet.objects.all().aggregate(max = Sum('consecutivo'))
		consecutivo = consecutivo['max']

		if consecutivo == None:
			consecutivo = 1

		if tipo_poliza.tipo_consec == 'M':		
			tipo_poliza_det = TipoPolizaDet.objects.create(id=c_get_next_key('ID_CATALOGOS'), tipo_poliza=tipo_poliza, ano=fecha.year, mes=fecha.month, consecutivo = 1,)
		elif tipo_poliza.tipo_consec == 'E':
			#Si existe permanente toma su consecutivo para crear uno nuevo si no existe inicia en 1
			consecutivo = TipoPolizaDet.objects.filter(tipo_poliza = tipo_poliza, mes=0, ano =0).aggregate(max = Sum('consecutivo'))
			consecutivo = consecutivo['max']

			if consecutivo == None:
				consecutivo = 1

			tipo_poliza_det = TipoPolizaDet.objects.create(id=c_get_next_key('ID_CATALOGOS'), tipo_poliza=tipo_poliza, ano=fecha.year, mes=0, consecutivo=consecutivo,)
		elif tipo_poliza.tipo_consec == 'P':
			tipo_poliza_det = TipoPolizaDet.objects.create(id=c_get_next_key('ID_CATALOGOS'), tipo_poliza=tipo_poliza, ano=0, mes=0, consecutivo = consecutivo,)								
		
	return tipo_poliza_det

def crear_polizas_por_documento(facturas, depto_co, informacion_contable, prefijo, msg, plantilla=None, descripcion = ''):
	facturasData 		= []
	cuenta 				= ''
	conceptos_poliza	= DetallePlantillaPolizas_V.objects.filter(plantilla_poliza_v=plantilla).order_by('id')

	for factura in facturas:
		tipo_poliza_det = get_folio_poliza(informacion_contable.tipo_poliza_ve, factura.fecha)

		poliza = DoctoCo(
				id                    	= c_get_next_key('ID_DOCTOS'),
				tipo_poliza				= informacion_contable.tipo_poliza_ve,
				poliza					= '%s%s'% (prefijo,("%09d" % tipo_poliza_det.consecutivo)[len(prefijo):]),
				fecha 					= factura.fecha,
				moneda 					= factura.moneda, 
				tipo_cambio 			= factura.tipo_cambio,
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
		factura.contabilizado = 'S'
		factura.save()

		#CONSECUTIVO DE FOLIO DE POLIZA
		tipo_poliza_det.consecutivo += 1 
		tipo_poliza_det.save()

		descuento_total 		= get_descuento_total_ve(factura.id)
		total 					= factura.total_impuestos + factura.importe_neto
		bancos_o_clientes 		= total - descuento_total
		bancos_o_clientes_0 	= total - descuento_total
		bancos_o_clientes_iva 	= total - descuento_total

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
			ventas_0 = ventas_0['ventas_0']
		
		ventas_16 = total - ventas_0 - factura.total_impuestos 
		if ventas_16 < 0:
			msg = 'Existe al menos una factura del cliente %s el cual [no tiene indicado cobrar inpuestos] por favor corrije esto para poder crear las polizas de este ciente '% factura.cliente.nombre
		else:
			posicion = 1
			for concepto in conceptos_poliza:
				importe = 0
				cuenta = []

				if concepto.valor_tipo == 'Ventas':
					if concepto.valor_iva == '0':
						importe = ventas_0
					elif concepto.valor_iva == 'I':
						importe = ventas_16
					elif concepto.valor_iva == 'A':
						importe = ventas_16 + ventas_0
					
					#SI LA FACTURA ES A CREDITO Y EL CONCEPTO NO ES A CREDITO
					if not factura.condicion_pago == informacion_contable.condicion_pago_contado and not concepto.valor_contado_credito == 'Credito' and not concepto.valor_contado_credito == 'Ambos':
						importe = 0 
					#SI LA FACTURA ES A CONTADO Y EL CONCEPTO NO ES DE CONTADO
					elif factura.condicion_pago == informacion_contable.condicion_pago_contado and not concepto.valor_contado_credito == 'Contado' and not concepto.valor_contado_credito == 'Ambos':
						importe = 0

					cuenta = concepto.cuenta_co
				#SI ES A CREDITO y ES CLIENTES
				elif concepto.valor_tipo == 'Clientes' and not factura.condicion_pago == informacion_contable.condicion_pago_contado: 
					if concepto.valor_iva == '0':
						importe = 0
					elif concepto.valor_iva == 'I':
						importe = 0
					elif concepto.valor_iva == 'A':
						importe = bancos_o_clientes

					#SI EL CLIENTE NO TIENE CUENTA SE VA A PUBLICO EN GENERAL
					if not factura.cliente.cuenta_xcobrar == None:
						cuenta =  get_object_or_404(CuentaCo, cuenta = factura.cliente.cuenta_xcobrar)
					else:
						cuenta = concepto.cuenta_co
				#SI ES BANCOS Y ES DE CONTADO
				elif concepto.valor_tipo == 'Bancos' and factura.condicion_pago == informacion_contable.condicion_pago_contado:
					if concepto.valor_iva == '0':
						importe = 0
					elif concepto.valor_iva == 'I':
						importe = 0
					elif concepto.valor_iva == 'A':
						importe = bancos_o_clientes

					cuenta = concepto.cuenta_co

				elif concepto.valor_tipo == 'Descuentos':
					importe = descuento_total
					cuenta = concepto.cuenta_co

				elif concepto.valor_tipo == 'IVA':
					importe = factura.total_impuestos
					cuenta = concepto.cuenta_co

					#SI LA FACTURA ES A CREDITO Y EL CONCEPTO NO ES A CREDITO
					if not factura.condicion_pago == informacion_contable.condicion_pago_contado and not concepto.valor_contado_credito == 'Credito' and not concepto.valor_contado_credito == 'Ambos':
						importe = 0 
					#SI LA FACTURA ES A CONTADO Y EL CONCEPTO NO ES DE CONTADO
					elif factura.condicion_pago == informacion_contable.condicion_pago_contado and not concepto.valor_contado_credito == 'Contado' and not concepto.valor_contado_credito == 'Ambos':
						importe = 0

				if importe > 0 and not cuenta == []:
					DoctosCoDet.objects.create(
						id				= -1,
						docto_co		= poliza,
						cuenta			= cuenta,
						depto_co		= depto_co,
						tipo_asiento	= concepto.tipo,
						importe			= importe,
						importe_mn		= 0,#PENDIENTE
						ref				= factura.folio,
						descripcion		= '',
						posicion		= posicion,
						recordatorio	= None,
						fecha			= factura.fecha,
						cancelado		= 'N', aplicado = 'N', ajuste = 'N', 
						moneda			= factura.moneda,
					)
					posicion +=1

				#elif if concepto.valor_tipo == 'IVA Pagado':
				#elif if concepto.valor_tipo == 'IVA Pendiente':

		facturasData.append ({
			'folio'		:factura.folio,
			'total'		:total,
			'ventas_0'	:ventas_0,
			'ventas_16'	:ventas_16,
			'impuesos'	:factura.total_impuestos,
			'tipo_cambio':factura.tipo_cambio,
			})

	return msg, facturasData

def crear_polizas_por_dia(facturas, depto_co, informacion_contable, prefijo, msg, plantilla=None, descripcion = ''):
	facturasData 		= []
	cuenta 				= ''
	conceptos_poliza	= DetallePlantillaPolizas_V.objects.filter(plantilla_poliza_v=plantilla).order_by('id')
	
	iva_pend_cobrar = iva_efec_cobrado 	= iva_tot 			= descuento_total 	= descuento_total_tot = total = total_tot	= bancos = clientes = 0 
	ventas_0_tot 	= ventas_16_tot 	= ventas_16_credito = ventas_0_credito  = ventas_16_contado = ventas_0_contado 	= 0
	moneda_local = get_object_or_404(Moneda,es_moneda_local='S')

	factura_numero = 0
	for factura_no, factura in enumerate(facturas):
		siguente_fatura = facturas[(factura_no +1)%len(facturas)]
		factura_numero = factura_no

		descuento_total 		= get_descuento_total_ve(factura.id)
		descuento_total_tot 	+= descuento_total 
		total 					= factura.total_impuestos + factura.importe_neto
		total_tot += total
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
			ventas_0 = ventas_0['ventas_0']
		
		ventas_16 = total - ventas_0 - factura.total_impuestos
		ventas_16_tot += ventas_16
		iva_tot += factura.total_impuestos
		ventas_0_tot += ventas_0 
		
		#SI LA FACTURA ES A CREDITO
		if not factura.condicion_pago == informacion_contable.condicion_pago_contado:
			ventas_16_credito 	+= ventas_16
			ventas_0_credito 	+= ventas_0
			iva_pend_cobrar 	+= factura.total_impuestos
			clientes 			+= total - descuento_total
		elif factura.condicion_pago == informacion_contable.condicion_pago_contado:
			ventas_16_contado 	+= ventas_16
			ventas_0_contado	+= ventas_0
			iva_efec_cobrado 	+= factura.total_impuestos
			bancos 				+= total - descuento_total

		#Cuando la fecha de la factura siguiente sea diferente
		if not factura.fecha == siguente_fatura.fecha or factura_no +1 == len(facturas):
			if ventas_16 < 0:
				msg = 'Existe al menos una factura del cliente %s el cual [no tiene indicado cobrar inpuestos] por favor corrije esto para poder crear las polizas de este ciente '% factura.cliente.nombre
			else:
				tipo_poliza_det = get_folio_poliza(informacion_contable.tipo_poliza_ve, factura.fecha)

				poliza = DoctoCo(
						id                    	= c_get_next_key('ID_DOCTOS'),
						tipo_poliza				= informacion_contable.tipo_poliza_ve,
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
								importe = ventas_0_credito
							elif concepto.valor_iva == 'I':
								importe = ventas_16_credito
							elif concepto.valor_iva == 'A':
								importe = ventas_16_credito + ventas_0_credito
						elif concepto.valor_contado_credito == 'Contado':
							if concepto.valor_iva == '0':
								importe = ventas_0_contado
							elif concepto.valor_iva == 'I':
								importe = ventas_16_contado
							elif concepto.valor_iva == 'A':
								importe = ventas_16_contado + ventas_0_contado
						elif concepto.valor_contado_credito == 'Ambos':
							if concepto.valor_iva == '0':
								importe = ventas_0_tot
							elif concepto.valor_iva == 'I':
								importe = ventas_16_tot
							elif concepto.valor_iva == 'A':
								importe = ventas_16_tot + ventas_0_tot

						cuenta = concepto.cuenta_co
					#SI ES A CREDITO y ES CLIENTES
					elif concepto.valor_tipo == 'Clientes': 
						if concepto.valor_iva == '0':
							importe = 0
						elif concepto.valor_iva == 'I':
							importe = 0
						elif concepto.valor_iva == 'A':
							importe = clientes

						cuenta = concepto.cuenta_co
					#SI ES BANCOS Y ES DE CONTADO
					elif concepto.valor_tipo == 'Bancos':
						if concepto.valor_iva == '0':
							importe = 0
						elif concepto.valor_iva == 'I':
							importe = 0
						elif concepto.valor_iva == 'A':
							importe = bancos

						cuenta = concepto.cuenta_co

					elif concepto.valor_tipo == 'Descuentos':
						importe = descuento_total_tot
						cuenta = concepto.cuenta_co

					elif concepto.valor_tipo == 'IVA':
						if concepto.valor_contado_credito == 'Credito':
							importe = iva_pend_cobrar
						elif concepto.valor_contado_credito == 'Contado':
							importe = iva_efec_cobrado
						elif concepto.valor_contado_credito == 'Ambos':
							importe = iva_tot

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
							ref				= factura.fecha,#PENDIENTE VER COMO VA
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
					'total'		:total,
					'ventas_0'	:ventas_0_tot,
					'ventas_16'	:ventas_16_tot,
					'impuesos'	:iva_tot,
					'tipo_cambio':1,
					})
				iva_pend_cobrar = iva_efec_cobrado 	= iva_tot 			= descuento_total = descuento_total_tot	= total = total_tot = bancos = clientes = 0 
				ventas_0_tot 	= ventas_16_tot 	= ventas_16_credito = ventas_0_credito  = ventas_16_contado = ventas_0_contado 	= 0

		factura.contabilizado = 'S'
		factura.save()
	return msg, facturasData

def generar_polizas(fecha_ini=None, fecha_fin=None, ignorar_facturas_cont=True, crear_polizas_por='Documento', plantilla='', descripcion= ''):
	error 	= 0
	msg		= ''
	facturasData = []
	
	try:
		informacion_contable = InformacionContable_V.objects.all()[:1]
		informacion_contable = informacion_contable[0]
	except ObjectDoesNotExist:
		error = 1
	
	if crear_polizas_por == 'Dia':
		fecha_fin = fecha_fin# + timedelta(days=1)
	#Si estadefinida la informacion contable no hay error!!!
	if error == 0:

		if ignorar_facturas_cont:
			facturas 			= DoctoVe.objects.filter(tipo='F', contabilizado ='N', estado ='N', fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
		else:
			facturas 			= DoctoVe.objects.filter(tipo='F', estado ='N', fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]

		#PREFIJO
		prefijo = informacion_contable.tipo_poliza_ve.prefijo
		if not informacion_contable.tipo_poliza_ve.prefijo:
			prefijo = ''

		if crear_polizas_por =='Documento':
			msg, facturasData = crear_polizas_por_documento(facturas, get_object_or_404(DeptoCo, pk=2090), informacion_contable, prefijo, msg , plantilla, descripcion)
		if crear_polizas_por =='Dia':
			msg, facturasData = crear_polizas_por_dia(facturas, get_object_or_404(DeptoCo, pk=2090), informacion_contable, prefijo, msg , plantilla, descripcion)

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
			plantilla 				= form.cleaned_data['plantilla']
			descripcion 			= form.cleaned_data['descripcion']

			msg = 'es valido'
			facturasData, msg = generar_polizas(fecha_ini, fecha_fin, ignorar_facturas_cont, crear_polizas_por, plantilla, descripcion)
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

