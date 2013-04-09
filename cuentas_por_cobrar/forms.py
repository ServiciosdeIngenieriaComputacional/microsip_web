#encoding:utf-8
from django import forms

import autocomplete_light

from ventas.models import *
from django.contrib.auth.models import User
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from cuentas_por_cobrar.models import *

class InformacionContableManageForm(forms.ModelForm):
	condicion_pago_contado 	= forms.ModelChoiceField(queryset= CondicionPago.objects.all(), required=True)

	class Meta:
		model = InformacionContable_CC

class GenerarPolizasManageForm(forms.Form):
	fecha_ini 					= forms.DateField()
	fecha_fin 					= forms.DateField()
	ignorar_documentos_cont 	= forms.BooleanField(required=False, initial=True)
	CREAR_POR = (
	    ('Documento', 'Documento'),
	    ('Dia', 'Dia'),
	    ('Periodo', 'Periodo'),
	)
	crear_polizas_por 			= forms.ChoiceField(choices=CREAR_POR)

	plantilla 					= forms.ModelChoiceField(queryset= PlantillaPolizas_CC.objects.all(), required=True)
	#plantilla_2 = forms.ModelChoiceField(queryset= PlantillaPolizas_V.objects.all(), required=True)
	descripcion 				= forms.CharField(max_length=100, required=False)
	crear_polizas_de 			= forms.ModelChoiceField(queryset= ConceptoCc.objects.filter(crear_polizas='S'), required=True)


class PlantillaPolizaManageForm(forms.ModelForm):
	tipo = forms.ModelChoiceField(queryset= ConceptoCc.objects.filter(crear_polizas='S'), required=True)
	class Meta:
		model = PlantillaPolizas_CC

class ConceptoPlantillaPolizaManageForm(forms.ModelForm):
	cuenta_co = forms.ModelChoiceField(queryset=CuentaCo.objects.all().order_by('cuenta'), required=True)
	class Meta:
		model = DetallePlantillaPolizas_CC

def PlantillaPoliza_items_formset(form, formset = BaseInlineFormSet, **kwargs):
	return inlineformset_factory(PlantillaPolizas_CC, DetallePlantillaPolizas_CC, form, formset, **kwargs)