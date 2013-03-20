#encoding:utf-8
from django import forms

import autocomplete_light

from ventas.models import *
from django.contrib.auth.models import User
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from inventarios.models import *

class InformacionContableManageForm(forms.ModelForm):
	tipo_poliza_ve 			= forms.ModelChoiceField(queryset= TipoPoliza.objects.all(), required=True)
	condicion_pago_contado 	= forms.ModelChoiceField(queryset= CondicionPago.objects.all(), required=True)
	
	class Meta:
		model = InformacionContable_V

class GenerarPolizasManageForm(forms.Form):
	fecha_ini 				= forms.DateField()
	fecha_fin 				= forms.DateField()
	ignorar_facturas_cont 	= forms.BooleanField(required=False, initial=True)
	plantilla  				= forms.ModelChoiceField(queryset= PlantillaPolizas_V.objects.all(), required=True)
	descripcion 			= forms.CharField(max_length=100, required=False)

	CREAR_POR = (
	    ('Documento', 'Documento'),
	    ('Dia', 'Dia'),
	    ('Periodo', 'Periodo'),
	)

	crear_polizas_por 		= forms.ChoiceField(choices=CREAR_POR)

class PlantillaPolizaManageForm(forms.ModelForm):
	class Meta:
		model = PlantillaPolizas_V

class ConceptoPlantillaPolizaManageForm(forms.ModelForm):
	class Meta:
		model = DetallePlantillaPolizas_V

def PlantillaPoliza_items_formset(form, formset = BaseInlineFormSet, **kwargs):
	return inlineformset_factory(PlantillaPolizas_V, DetallePlantillaPolizas_V, form, formset, **kwargs)