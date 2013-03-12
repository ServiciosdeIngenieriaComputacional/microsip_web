#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from inventarios.models import *
from cuentas_por_pagar.forms import *
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


@login_required(login_url='/inventarios/login/')
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

	c= {'form':form,'msg':msg,}
	return render_to_response(template_name, c, context_instance=RequestContext(request))

def generar_polizas(fecha_ini=None, fecha_fin=None, ignorar_facturas_cont=True):
	error 					= 0 
	informacion_contable 	= []
	
	if ignorar_facturas_cont:
		documentos_cp 			= DoctosCp.objects.filter(contabilizado ='N', fecha__gt=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
	else:
		documentos_cp 			= DoctosCp.objects.filter(fecha__gt=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]

	facturasData 			= []
	msg 					= ''
	cuenta = ''

	try:
		informacion_contable = InformacionContable_CP.objects.all()[:1]
		informacion_contable = informacion_contable[0]
	except ObjectDoesNotExist:
		error = 1
	
	# if error == 0:
	# 	#PREFIJO
	# 	#prefijo = informacion_contable.tipo_poliza_ve.prefijo
	# 	#if not informacion_contable.tipo_poliza_ve.prefijo:
	# 	#	prefijo = ''

	# 	for documento_cp in documentos_cp:
	# 		#CONSECUTIVO FOLIOS
	# 		tipo_poliza_det = ventas.views.get_folio_poliza(informacion_contable.tipo_poliza_ve, documento_cp.fecha)
			
	# 		descuento_total = get_descuento_total_ve(factura.id)
	# 		total = factura.total_impuestos + factura.importe_neto
	# 		bancos_o_clientes =  total - descuento_total

	# 		#SI ES DE CONTADO
	# 		if factura.condicion_pago == informacion_contable.condicion_pago_contado:
	# 			cuenta = informacion_contable.cobros
	# 		else:
	# 			#SI EL CLIENTE NO TIENE NO TIENE CUENTA SE VA A PUBLICO EN GENERAL
	# 			if not factura.cliente.cuenta_xcobrar == None:
	# 				cuenta =  get_object_or_404(CuentaCo, cuenta = factura.cliente.cuenta_xcobrar)
	# 			else:
	# 				cuenta = informacion_contable.cuantaxcobrar
			

	# 		if ventas_16 < 0:
	# 			msg = 'Existe al menos una factura del cluiente %s el cual [no tiene indicado cobrar inpuestos] por favor corrije esto para poder crear las polizas de este ciente '% factura.cliente.nombre
	# 		else:
	# 			id_poli = c_get_next_key('ID_DOCTOS')
	# 			folio = '%s%s'% (prefijo,("%09d" % tipo_poliza_det.consecutivo)[len(prefijo):])

	# 			poliza = DoctoCo(
	# 				id                    	= id_poli,
	# 				tipo_poliza				= informacion_contable.tipo_poliza_ve,
	# 				poliza					= folio,
	# 				fecha 					= factura.fecha,
	# 				moneda 					= factura.moneda, 
	# 				tipo_cambio 			= factura.tipo_cambio,
	# 				estatus 				= 'P', cancelado= 'N', aplicado = 'N', ajuste = 'N', integ_co = 'S',
	# 				descripcion 			= informacion_contable.descripcion_polizas_ve,
	# 				forma_emitida 			= 'N', sistema_origen = 'CO',
	# 				nombre 					= '',
	# 				grupo_poliza_periodo 	= None,
	# 				integ_ba 				= 'N',
	# 				usuario_creador			= 'SYSDBA',
	# 				fechahora_creacion		= datetime.datetime.now(), usuario_aut_creacion = None, 
	# 				usuario_ult_modif 		= 'SYSDBA', fechahora_ult_modif = datetime.datetime.now(), usuario_aut_modif 	= None,
	# 				usuario_cancelacion 	= None, fechahora_cancelacion 	=  None, usuario_aut_cancelacion 				= None,
	# 			)

	# 			#GUARDA LA PILIZA
	# 			poliza_o = poliza.save()
	# 			factura.contabilizado = 'S'
	# 			factura.save()

	# 			tipo_poliza_det.consecutivo += 1 
	# 			tipo_poliza_det.save()

	# 			posicion = 1
	# 			#DEBE
	# 			DoctosCoDet.objects.create(
	# 					id				= -1,
	# 					docto_co		= poliza,
	# 					cuenta			= cuenta,
	# 					depto_co		= depto_co,
	# 					tipo_asiento	= 'C',
	# 					importe			= bancos_o_clientes,
	# 					importe_mn		= 0,#PENDIENTE
	# 					ref				= factura.folio,
	# 					descripcion		= '',
	# 					posicion		= posicion,
	# 					recordatorio	= None,
	# 					fecha			= factura.fecha,
	# 					cancelado		= 'N', aplicado = 'N', ajuste = 'N', 
	# 					moneda			= factura.moneda,
	# 				)
	# 			posicion +=1
			
	# 		# facturasData.append ({
	# 		# 	'folio'		:factura.folio,
	# 		# 	'total'		:total,
	# 		# 	'ventas_0'	:ventas_0,
	# 		# 	'ventas_16'	:ventas_16,
	# 		# 	'impuesos'	:factura.total_impuestos,
	# 		# 	'tipo_cambio':factura.tipo_cambio,
	# 		# 	})

	# elif error == 1:
	# 	msg = 'No se han derfinido las preferencias de la empresa para generar polizas [Por favor definelas primero en Configuracion > Preferencias de la empresa]'

	return facturasData, msg



