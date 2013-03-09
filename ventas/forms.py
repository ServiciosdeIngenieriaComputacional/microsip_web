#encoding:utf-8
from django import forms

import autocomplete_light

from ventas.models import *
from django.contrib.auth.models import User
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from inventarios.models import *

class InformacionContableManageForm(forms.ModelForm):
	cuantaxcobrar 			= forms.ModelChoiceField(queryset= CuentaCo.objects.all().order_by('cuenta'), required=True)
	cobros					= forms.ModelChoiceField(queryset= CuentaCo.objects.all().order_by('cuenta'), required=True)
	descuentos			    = forms.ModelChoiceField(queryset= CuentaCo.objects.all().order_by('cuenta'), required=True)
	tipo_poliza_ve 			= forms.ModelChoiceField(queryset= TipoPoliza.objects.all(), required=True)
	condicion_pago_contado 	= forms.ModelChoiceField(queryset= CondicionPago.objects.all(), required=True)
	
	class Meta:
		model = InformacionContable

class GenerarPolizasManageForm(forms.Form):
	fecha_ini =  forms.DateField()
	fecha_fin =  forms.DateField()
	ignorar_facturas_cont = forms.BooleanField(required=True, initial=True)


class ConfiguracionPolizasManageForm(forms.ModelForm):
	class Meta:
		model = ConfiguracionPolizas