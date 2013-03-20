#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from inventarios.models import *
from ventas.forms import *
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
	conceptos_poliza	= DetallePlantillaPolizas_V.objects.filter(plantilla_poliza_v=plantilla)

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

		descuento_total = get_descuento_total_ve(factura.id)
		total = factura.total_impuestos + factura.importe_neto
		bancos_o_clientes =  total - descuento_total

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
			# #SI ES DE CONTADO
			# if factura.condicion_pago == informacion_contable.condicion_pago_contado:
			# 	cuenta = informacion_contable.cobros
			# else:
			# 	#SI EL CLIENTE NO TIENE CUENTA SE VA A PUBLICO EN GENERAL
			# 	if not factura.cliente.cuenta_xcobrar == None:
			# 		cuenta =  get_object_or_404(CuentaCo, cuenta = factura.cliente.cuenta_xcobrar)
			# 	else:
			# 		cuenta = informacion_contable.cuantaxcobrar

			posicion = 1
			for concepto in conceptos_poliza:
				if concepto.valor_tipo == 'Ventas':
					if concepto.valor_iva == '0':
						DoctosCoDet.objects.create(
								id				= -1,
								docto_co		= poliza,
								cuenta			= concepto.cuenta_co,
								depto_co		= depto_co,
								tipo_asiento	= concepto.tipo,
								importe			= ventas_0,
								importe_mn		= 0,
								ref				= factura.folio,
								descripcion		= '',
								posicion		= posicion,
								recordatorio	= None,
								fecha			= factura.fecha,
								cancelado		= 'N', aplicado = 'N', ajuste = 'N', 
								moneda			= factura.moneda,
							)
					elif concepto.valor_iva == 'I':
						DoctosCoDet.objects.create(
							id				= -1,
							docto_co		= poliza,
							cuenta			= concepto.cuenta_co,
							depto_co		= depto_co,
							tipo_asiento	= concepto.tipo,
							importe			= ventas_16,
							importe_mn		= 0,
							ref				= factura.folio,
							descripcion		= '',
							posicion		= posicion,
							recordatorio	= None,
							fecha			= factura.fecha,# datetime.date(1000, 01, 01),#datetime.date.today()
							cancelado		= 'N', aplicado = 'N', ajuste = 'N', 
							moneda			= factura.moneda,
						)
					elif concepto.valor_iva == 'A':
						DoctosCoDet.objects.create(
							id				= -1,
							docto_co		= poliza,
							cuenta			= concepto.cuenta_co,
							depto_co		= depto_co,
							tipo_asiento	= concepto.tipo,
							importe			= ventas_16 + ventas_0,
							importe_mn		= 0,
							ref				= factura.folio,
							descripcion		= '',
							posicion		= posicion,
							recordatorio	= None,
							fecha			= factura.fecha,# datetime.date(1000, 01, 01),#datetime.date.today()
							cancelado		= 'N', aplicado = 'N', ajuste = 'N', 
							moneda			= factura.moneda,
						)
					
					posicion +=1
				elif concepto.valor_tipo == 'Clientes' : 
					#SI ES DE CONTADO
					if not factura.condicion_pago == informacion_contable.condicion_pago_contado:
						#SI EL CLIENTE NO TIENE CUENTA SE VA A PUBLICO EN GENERAL
						if not factura.cliente.cuenta_xcobrar == None:
							cuenta =  get_object_or_404(CuentaCo, cuenta = factura.cliente.cuenta_xcobrar)

						DoctosCoDet.objects.create(
								id				= -1,
								docto_co		= poliza,
								cuenta			= concepto.cuenta_co,
								depto_co		= depto_co,
								tipo_asiento	= concepto.tipo,
								importe			= bancos_o_clientes,
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
				elif concepto.valor_tipo == 'Bancos':
					DoctosCoDet.objects.create(
						id				= -1,
						docto_co		= poliza,
						cuenta			= concepto.cuenta_co,
						depto_co		= depto_co,
						tipo_asiento	= concepto.tipo,
						importe			= bancos_o_clientes,
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
				elif concepto.valor_tipo == 'Descuentos':
					DoctosCoDet.objects.create(
							id				= -1,
							docto_co		= poliza,
							cuenta			= concepto.cuenta_co,
							depto_co		= depto_co,
							tipo_asiento	= concepto.tipo,
							importe			= descuento_total,
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
				elif concepto.valor_tipo == 'IVA':
					DoctosCoDet.objects.create(
							id				= -1,
							docto_co		= poliza,
							cuenta			= concepto.cuenta_co,
							depto_co		= depto_co,	
							tipo_asiento	= concepto.tipo,
							importe			= ventas_16,
							importe_mn		= 0,
							ref				= factura.folio,
							descripcion		= '',
							posicion		= posicion,
							recordatorio	= None,
							fecha			= factura.fecha,# datetime.date(1000, 01, 01),#datetime.date.today()
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

def generar_polizas(fecha_ini=None, fecha_fin=None, ignorar_facturas_cont=True, crear_polizas_por='Documento', plantilla='', descripcion= ''):
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

		if ignorar_facturas_cont:
			facturas 			= DoctoVe.objects.filter(tipo='F', contabilizado ='N', estado ='N', fecha__gt=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
		else:
			facturas 			= DoctoVe.objects.filter(tipo='F', estado ='N', fecha__gt=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]

		#PREFIJO
		prefijo = informacion_contable.tipo_poliza_ve.prefijo
		if not informacion_contable.tipo_poliza_ve.prefijo:
			prefijo = ''

		if crear_polizas_por =='Documento':
			msg, facturasData = crear_polizas_por_documento(facturas, get_object_or_404(DeptoCo, pk=2090), informacion_contable, prefijo, msg , plantilla, descripcion)

	elif error == 1:
		msg = 'No se han derfinido las preferencias de la empresa para generar polizas [Por favor definelas primero en Configuracion > Preferencias de la empresa]'

	return facturasData, msg

@login_required(login_url='/login/')
def facturas_View(request, template_name='herramientas/generar_polizas.html'):
	facturasData 	= []
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
			facturasData, msg  = generar_polizas(fecha_ini, fecha_fin, ignorar_facturas_cont, crear_polizas_por, plantilla, descripcion)
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

