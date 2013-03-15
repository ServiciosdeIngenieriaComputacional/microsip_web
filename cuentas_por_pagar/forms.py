#encoding:utf-8
from django import forms

import autocomplete_light

from ventas.models import *
from django.contrib.auth.models import User
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from inventarios.models import *

class InformacionContableManageForm(forms.ModelForm):
	cuentas_por_pagar 			= forms.ModelChoiceField(queryset= CuentaCo.objects.all().order_by('cuenta'), required=True)
	anticipos					= forms.ModelChoiceField(queryset= CuentaCo.objects.all().order_by('cuenta'), required=True)
	descuentos_pronto_pago		= forms.ModelChoiceField(queryset= CuentaCo.objects.all().order_by('cuenta'), required=True)
	
	class Meta:
		model = InformacionContable_CP

class GenerarPolizasManageForm(forms.Form):
	fecha_ini =  forms.DateField()
	fecha_fin =  forms.DateField()
	ignorar_facturas_cont = forms.BooleanField(required=False, initial=True)