#encoding:utf-8
from django import forms
from inventarios.models import *
from django.contrib.auth.models import User
from django.forms.models import BaseInlineFormSet, inlineformset_factory

class DoctosInManageForm(forms.ModelForm):
	class Meta:
		model = DoctosIn
		exclude = (
			'cancelado',
			'aplicado',
			'forma_emitida',
			'contabilizado',
			'sistema_origen',
			'naturaleza_concepto',
			'usuario_creador',
			'fechahora_creacion',
			'usuario_ult_modif',
			'fechahora_ult_modif',
			)

class DoctosInDetManageForm(forms.ModelForm):
	class Meta:
		model = DoctosInDet
		exclude = (
			'tipo_movto',
			'almacen',
			'conceptoIn',
			'metodo_costeo',
			'rol',
			'cancelado',
			'aplicado',
			'costeo_pend',
			'pedimento_pend',
			'fecha',)

class DoctosInvfisManageForm(forms.ModelForm):
	file_inventario = forms.CharField(widget=forms.FileInput)
	
	class Meta:
		model = DoctosInvfis
		exclude = (
			'cancelado',
			'aplicado',
			'usuario_creador',
			'fechahora_creacion',
			'usuario_aut_creacion',
			'usuario_ult_modif',
			'fechahora_ult_modif',
			'usuario_aut_modif',
			)

class DoctosInvfisDetManageForm(forms.ModelForm):
	class Meta:
		model = DoctosInvfisDet
		exclude = (
			'claveArticulo',
			)

def get_DoctosIn_items_formset(form, formset = BaseInlineFormSet, **kwargs):
	return inlineformset_factory(DoctosIn, DoctosInDet, form, formset, **kwargs)

def inventarioFisico_items_formset(form, formset = BaseInlineFormSet, **kwargs):
	return inlineformset_factory(DoctosInvfis, DoctosInvfisDet, form, formset, **kwargs)