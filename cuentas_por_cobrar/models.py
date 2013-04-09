#encoding:utf-8
from django.db import models
from datetime import datetime 
from django.db.models.signals import pre_save
from django.core import urlresolvers
from inventarios.models import *

class ConceptoCc(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='CONCEPTO_CC_ID')
    nombre_abrev        = models.CharField(max_length=30, db_column='NOMBRE_ABREV')
    crear_polizas       = models.CharField(default='N', max_length=1, db_column='CREAR_POLIZAS')
    cuenta_contable     = models.CharField(max_length=30, db_column='CUENTA_CONTABLE')
    clave_tipo_poliza   = models.CharField(max_length=1, db_column='TIPO_POLIZA')
    descripcion_poliza  = models.CharField(max_length=200, db_column='DESCRIPCION_POLIZA')

    def __unicode__(self):
        return self.nombre_abrev

    class Meta:
        db_table = u'conceptos_cc'

class DoctosCc(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='DOCTO_CC_ID')
    concepto            = models.ForeignKey(ConceptoCc, db_column='CONCEPTO_CC_ID')
    folio               = models.CharField(max_length=9, db_column='FOLIO')
    naturaleza_concepto = models.CharField(max_length=1, db_column='NATURALEZA_CONCEPTO')
    fecha               = models.DateField(auto_now=True, db_column='FECHA') 
    cliente           	= models.ForeignKey(Cliente, db_column='CLIENTE_ID')
    cancelado           = models.CharField(default='N', max_length=1, db_column='CANCELADO')
    aplicado            = models.CharField(default='S', max_length=1, db_column='APLICADO')
    descripcion         = models.CharField(blank=True, null=True, max_length=200, db_column='DESCRIPCION')
    contabilizado       = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='CONTABILIZADO')
    tipo_cambio         = models.DecimalField(max_digits=18, decimal_places=6, db_column='TIPO_CAMBIO')
    condicion_pago      = models.ForeignKey(CondicionPago, db_column='COND_PAGO_ID')

    def __unicode__(self):
        return u'%s' % self.id

    class Meta:
        db_table = u'doctos_cc'

################################################################
####                                                        ####
####        MODELOS EXTRA A BASE DE DATOS MICROSIP          ####
####                                                        ####
################################################################

class InformacionContable_CC(models.Model):
    condicion_pago_contado  = models.ForeignKey(CondicionPago, blank=True, null=True)

    def __unicode__(self):
        return u'%s'% self.id

class PlantillaPolizas_CC(models.Model):
    nombre  = models.CharField(max_length=200)
    tipo    = models.ForeignKey(ConceptoCc)
    
    def __unicode__(self):
        return u'%s'%self.nombre

class DetallePlantillaPolizas_CC(models.Model):
    TIPOS = (('C', 'Cargo'),('A', 'Abono'),)
    VALOR_TIPOS =(
        ('Compras', 'Compras'),
        ('Proveedores', 'Proveedores'),
        ('Bancos', 'Bancos'),
        ('Fletes', 'Fletes'),
        ('Descuentos', 'Descuentos'),
        ('Devoluciones','Devoluciones'),
        ('Anticipos','Anticipos'),
        ('IVA', 'IVA'),
    )
    VALOR_IVA_TIPOS             = (('A', 'Ambos'),('I', 'Solo IVA'),('0', 'Solo 0%'),)
    VALOR_CONTADO_CREDITO_TIPOS = (('Ambos', 'Ambos'),('Contado', 'Contado'),('Credito', 'Credito'),)

    plantilla_poliza_CC      = models.ForeignKey(PlantillaPolizas_CC)
    cuenta_co               = models.ForeignKey(CuentaCo)
    tipo                    = models.CharField(max_length=2, choices=TIPOS, default='C')
    valor_tipo              = models.CharField(max_length=20, choices=VALOR_TIPOS)
    valor_iva               = models.CharField(max_length=2, choices=VALOR_IVA_TIPOS, default='A')
    valor_contado_credito   = models.CharField(max_length=10, choices=VALOR_CONTADO_CREDITO_TIPOS, default='Ambos')

    def __unicode__(self):
        return u'%s'%self.id

