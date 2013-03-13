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

	c= {'form':form,'msg':msg,}
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

def generar_polizas(fecha_ini=None, fecha_fin=None, ignorar_facturas_cont=True):
	depto_co 				= get_object_or_404(DeptoCo, pk=2090) 
	error 					= 0 
	informacion_contable 	= []
	
	if ignorar_facturas_cont:
		facturas 			= DoctoVe.objects.filter(tipo='F', contabilizado ='N', estado ='N', fecha__gt=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
	else:
		facturas 			= DoctoVe.objects.filter(tipo='F', estado ='N', fecha__gt=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]

	facturasData 			= []
	msg 					= ''
	cuenta = ''

	try:
		informacion_contable = InformacionContable_V.objects.all()[:1]
		informacion_contable = informacion_contable[0]
	except ObjectDoesNotExist:
		error = 1
	
	if error == 0:
		#PREFIJO
		prefijo = informacion_contable.tipo_poliza_ve.prefijo
		if not informacion_contable.tipo_poliza_ve.prefijo:
			prefijo = ''

		for factura in facturas:
			#CONSECUTIVO FOLIOS
			tipo_poliza_det = get_folio_poliza(informacion_contable.tipo_poliza_ve, factura.fecha)
			
			descuento_total = get_descuento_total_ve(factura.id)
			total = factura.total_impuestos + factura.importe_neto
			bancos_o_clientes =  total - descuento_total

			#SI ES DE CONTADO
			if factura.condicion_pago == informacion_contable.condicion_pago_contado:
				cuenta = informacion_contable.cobros
			else:
				#SI EL CLIENTE NO TIENE NO TIENE CUENTA SE VA A PUBLICO EN GENERAL
				if not factura.cliente.cuenta_xcobrar == None:
					cuenta =  get_object_or_404(CuentaCo, cuenta = factura.cliente.cuenta_xcobrar)
				else:
					cuenta = informacion_contable.cuantaxcobrar
			
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

			ventas_16 = total - ventas_0 - factura.total_impuestos 

			if ventas_16 < 0:
				msg = 'Existe al menos una factura del cluiente %s el cual [no tiene indicado cobrar inpuestos] por favor corrije esto para poder crear las polizas de este ciente '% factura.cliente.nombre
			else:
				id_poli = c_get_next_key('ID_DOCTOS')
				folio = '%s%s'% (prefijo,("%09d" % tipo_poliza_det.consecutivo)[len(prefijo):])

				poliza = DoctoCo(
					id                    	= id_poli,
					tipo_poliza				= informacion_contable.tipo_poliza_ve,
					poliza					= folio,
					fecha 					= factura.fecha,
					moneda 					= factura.moneda, 
					tipo_cambio 			= factura.tipo_cambio,
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
				factura.contabilizado = 'S'
				factura.save()

				contabilizado ='N'
				tipo_poliza_det.consecutivo += 1 
				tipo_poliza_det.save()

				posicion = 1
				#DEBE
				DoctosCoDet.objects.create(
						id				= -1,
						docto_co		= poliza,
						cuenta			= cuenta,
						depto_co		= depto_co,
						tipo_asiento	= 'C',
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

				if not descuento_total == 0:
					DoctosCoDet.objects.create(
							id				= -1,
							docto_co		= poliza,
							cuenta			= informacion_contable.descuentos,
							depto_co		= depto_co,
							tipo_asiento	= 'C',
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
							posicion		= posicion,
							recordatorio	= None,
							fecha			= factura.fecha,
							cancelado		= 'N', aplicado = 'N', ajuste = 'N', 
							moneda			= factura.moneda,
						)
					posicion +=1

				if not factura.total_impuestos == 0:

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
							posicion		= posicion,
							recordatorio	= None,
							fecha			= factura.fecha,# datetime.date(1000, 01, 01),#datetime.date.today()
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
							importe			= factura.total_impuestos,
							importe_mn		= 0,
							ref				= factura.folio,
							descripcion		= '',
							posicion		= posicion + 1,
							recordatorio	= None,
							fecha			= factura.fecha,
							cancelado		= 'N', aplicado = 'N', ajuste = 'N', 
							moneda			= factura.moneda,
						),
					])

			
			facturasData.append ({
				'folio'		:factura.folio,
				'total'		:total,
				'ventas_0'	:ventas_0,
				'ventas_16'	:ventas_16,
				'impuesos'	:factura.total_impuestos,
				'tipo_cambio':factura.tipo_cambio,
				})

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
			fecha_ini = form.cleaned_data['fecha_ini']
			fecha_fin = form.cleaned_data['fecha_fin']
			ignorar_facturas_cont = form.cleaned_data['ignorar_facturas_cont']

			msg = 'es valido'
			facturasData, msg  = generar_polizas(fecha_ini, fecha_fin, ignorar_facturas_cont)		
	else:
		form = GenerarPolizasManageForm()

	c = {'facturas':facturasData,'msg':msg,'form':form,}
	return render_to_response(template_name, c, context_instance=RequestContext(request))

