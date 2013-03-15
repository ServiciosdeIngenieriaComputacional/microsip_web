#encoding:utf-8
from django.db import models
from datetime import datetime 
from django.db.models.signals import pre_save
from django.core import urlresolvers

class Moneda(models.Model):
    id = models.AutoField(primary_key=True, db_column='MONEDA_ID')
        
    class Meta:
        db_table = u'monedas'

class Paises(models.Model):
    PAIS_ID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, db_column='NOMBRE')

    class Meta:
        db_table = u'paises'

class ActivosFijos(models.Model):
    class Meta:
        db_table = u'activos_fijos'

class AcumCuentasCoTemp(models.Model):
    class Meta:
        db_table = u'acum_cuentas_co_temp'

class Aduanas(models.Model):
    class Meta:
        db_table = u'aduanas'

class Agentes(models.Model):
    AGENTE_ID = models.AutoField(primary_key=True)

    class Meta:
        db_table = u'agentes'

class Almacenes(models.Model):
    ALMACEN_ID = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    
    def __unicode__(self):
        return self.nombre

    class Meta:
        db_table = u'almacenes'

class Articulos(models.Model):
    id = models.AutoField(primary_key=True, db_column='ARTICULO_ID')
    nombre = models.CharField(max_length=100, db_column='NOMBRE')
    es_almacenable = models.CharField(default='S', max_length=1, db_column='ES_ALMACENABLE')

    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        db_table = u'articulos'

class ArticulosClientes(models.Model):
    class Meta:
        db_table = u'articulos_clientes'

class ArticulosDiscretos(models.Model):
    class Meta:
        db_table = u'articulos_discretos'

class Atributos(models.Model):
    class Meta:
        db_table = u'atributos'

class Bancos(models.Model):
    BANCO_ID = models.AutoField(primary_key=True)
    class Meta:
        db_table = u'bancos'

class Beneficiarios(models.Model):
    BENEFICIARIO_ID = models.AutoField(primary_key=True)

    class Meta:
        db_table = u'beneficiarios'

class Bitacora(models.Model):
    class Meta:
        db_table = u'bitacora'

class BookmarksReportes(models.Model):
    class Meta:
        db_table = u'bookmarks_reportes'

class Cajas(models.Model):
    class Meta:
        db_table = u'cajas'

class CajasCajeros(models.Model):
    class Meta:
        db_table = u'cajas_cajeros'

class Cajeros(models.Model):
    class Meta:
        db_table = u'cajeros'

class CapasCostos(models.Model):
    class Meta:
        db_table = u'capas_costos'

class CapasPedimentos(models.Model):
    class Meta:
        db_table = u'capas_pedimentos'

class CargosPeriodicosCc(models.Model):
    class Meta:
        db_table = u'cargos_periodicos_cc'

class CentrosCosto(models.Model):
    id = models.AutoField(primary_key=True, db_column='CENTRO_COSTO_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    es_predet = models.CharField(default='N', max_length=1, db_column='ES_PREDET')
    usuario_creador = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CREADOR')
    fechahora_creacion = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_CREACION')
    usuario_aut_creacion = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CREACION')
    usuario_ult_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_ULT_MODIF')
    usuario_aut_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_MODIF')

    def __unicode__(self):
        return self.nombre 
    class Meta:
        db_table = u'centros_costo'

class CertCfdProv(models.Model):
    class Meta:
        db_table = u'cert_cfd_prov'

class CfdRecibidos(models.Model):
    class Meta:
        db_table = u'cfd_recibidos'

class Ciudades(models.Model):
    class Meta:
        db_table = u'ciudades'

class RolesClavesArticulos(models.Model):
    id = models.AutoField(primary_key=True, db_column='ROL_CLAVE_ART_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    es_ppal = models.CharField(default='N', max_length=1, db_column='ES_PPAL')
    
    class Meta:
        db_table = u'roles_claves_articulos'

class ClavesArticulos(models.Model):
    id = models.AutoField(primary_key=True, db_column='CLAVE_ARTICULO_ID')
    clave = models.CharField(max_length=20, db_column='CLAVE_ARTICULO')
    articulo = models.ForeignKey(Articulos, db_column='ARTICULO_ID')
    rol = models.ForeignKey(RolesClavesArticulos, db_column='ROL_CLAVE_ART_ID')

    def __unicode__(self):
        return u'%s' % self.clave

    class Meta:
        db_table = u'claves_articulos'

class ClavesCatSec(models.Model):
    class Meta:
        db_table = u'claves_cat_sec'

class ClavesClientes(models.Model):
    class Meta:
        db_table = u'claves_clientes'

class ClavesEmpleados(models.Model):
    class Meta:
        db_table = u'claves_empleados'

class ClavesProveedores(models.Model):    
    class Meta:
        db_table = u'claves_proveedores'

class Proveedor(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='PROVEEDOR_ID')
    nombre              = models.CharField(max_length=100, db_column='NOMBRE')
    cuenta_xpagar       = models.CharField(max_length=9, db_column='CUENTA_CXP')
    cuenta_anticipos    = models.CharField(max_length=9, db_column='CUENTA_ANTICIPOS')
    moneda              = models.ForeignKey(Moneda, db_column='MONEDA_ID')

    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        db_table = u'proveedores'

class Cobradores(models.Model):
    class Meta:
        db_table = u'cobradores'

class ComandosDispositivos(models.Model):
    class Meta:
        db_table = u'comandos_dispositivos'

class ComandosTiposDispositivos(models.Model):
    class Meta:
        db_table = u'comandos_tipos_dispositivos'

class ComisCobTipoCli(models.Model):
    class Meta:
        db_table = u'comis_cob_tipo_cli'

class ComisCobZona(models.Model):
    class Meta:
        db_table = u'comis_cob_zona'

class ComisVenArt(models.Model):
    class Meta:
        db_table = u'comis_ven_art'

class ComisVenCli(models.Model):
    class Meta:
        db_table = u'comis_ven_cli'

class ComisVenGrupo(models.Model):
    class Meta:
        db_table = u'comis_ven_grupo'

class ComisVenLinea(models.Model):
    class Meta:
        db_table = u'comis_ven_linea'

class ComisVenTipoCli(models.Model):
    class Meta:
        db_table = u'comis_ven_tipo_cli'

class ComisVenZona(models.Model):
    class Meta:
        db_table = u'comis_ven_zona'

class CompromArticulos(models.Model):
    class Meta:
        db_table = u'comprom_articulos'

class ConceptosBa(models.Model):
    class Meta:
        db_table = u'conceptos_ba'

class ConceptosCc(models.Model):
    class Meta:
        db_table = u'conceptos_cc'

class ConceptoCp(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='CONCEPTO_CP_ID')
    nombre_abrev        = models.CharField(max_length=30, db_column='NOMBRE_ABREV')
    crear_polizas       = models.CharField(default='N', max_length=1, db_column='CREAR_POLIZAS')
    cuenta_contable     = models.CharField(max_length=30, db_column='CUENTA_CONTABLE')
    clave_tipo_poliza   = models.CharField(max_length=1, db_column='TIPO_POLIZA')
    descripcion_poliza  = models.CharField(max_length=200, db_column='DESCRIPCION_POLIZA')

    def __unicode__(self):
        return self.nombre_abrev

    class Meta:
        db_table = u'conceptos_cp'

class ConceptosDim(models.Model):
    class Meta:
        db_table = u'conceptos_dim'

class ConceptosEmp(models.Model):
    class Meta:
        db_table = u'conceptos_emp'

class ConceptosIn(models.Model):
    CONCEPTO_IN_ID = models.AutoField(primary_key=True)
    nombre_abrev = models.CharField(max_length=30, db_column='NOMBRE_ABREV')

    def __unicode__(self):
        return self.nombre_abrev

    class Meta:
        db_table = u'conceptos_in'

class ConceptosNo(models.Model):
    class Meta:
        db_table = u'conceptos_no'

class CondicionPago(models.Model):
    id = models.AutoField(primary_key=True, db_column='COND_PAGO_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    
    def __unicode__(self):
        return self.nombre
    class Meta:
        db_table = u'condiciones_pago'

class CondicionesPagoCp(models.Model):
    class Meta:
        db_table = u'condiciones_pago_cp'

class ConfTicketsCajas(models.Model):
    class Meta:
        db_table = u'conf_tickets_cajas'

class ConfTicketsCajasPrns(models.Model):
    class Meta:
        db_table = u'conf_tickets_cajas_prns'

class ConsignatariosCm(models.Model):
    class Meta:
        db_table = u'consignatarios_cm'

class CuentasBancarias(models.Model):
    class Meta:
        db_table = u'cuentas_bancarias'

class CuentaCo(models.Model):
    id = models.AutoField(primary_key=True, db_column='CUENTA_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    cuenta = models.CharField(max_length=50, db_column='CUENTA_PT')
    
    def __unicode__(self):
        return u'%s (%s)' % (self.cuenta, self.nombre)
    class Meta:
        db_table = u'cuentas_co'

class CuentasNo(models.Model):
    class Meta:
        db_table = u'cuentas_no'

class DeptoCo(models.Model):
    id = models.AutoField(primary_key=True, db_column='DEPTO_CO_ID')
    
    class Meta:
        db_table = u'deptos_co'

class DeptosNo(models.Model):
    class Meta:
        db_table = u'deptos_no'

class DescripPolizas(models.Model):
    class Meta:
        db_table = u'descrip_polizas'

class DesgloseEnDiscretos(models.Model):
    class Meta:
        db_table = u'desglose_en_discretos'

class DesgloseEnDiscretosCm(models.Model):
    class Meta:
        db_table = u'desglose_en_discretos_cm'

class DesgloseEnDiscretosInvfis(models.Model):
    class Meta:
        db_table = u'desglose_en_discretos_invfis'

class DesgloseEnDiscretosPv(models.Model):
    class Meta:
        db_table = u'desglose_en_discretos_pv'

class DesgloseEnDiscretosVe(models.Model):
    class Meta:
        db_table = u'desglose_en_discretos_ve'

class DesgloseEnPedimentos(models.Model):
    class Meta:
        db_table = u'desglose_en_pedimentos'

class DirsClientes(models.Model):
    class Meta:
        db_table = u'dirs_clientes'

class Dispositivos(models.Model):
    class Meta:
        db_table = u'dispositivos'

class DispositivosCajas(models.Model):
    class Meta:
        db_table = u'dispositivos_cajas'

class DoctosBa(models.Model):
    class Meta:
        db_table = u'doctos_ba'

class DoctosCc(models.Model):
    class Meta:
        db_table = u'doctos_cc'

class DoctosCm(models.Model):
    class Meta:
        db_table = u'doctos_cm'

class DoctosCmDet(models.Model):
    class Meta:
        db_table = u'doctos_cm_det'

class DoctosCmLigas(models.Model):
    class Meta:
        db_table = u'doctos_cm_ligas'

class DoctosCmLigasDet(models.Model):
    class Meta:
        db_table = u'doctos_cm_ligas_det'

class DoctosCmProeve(models.Model):
    class Meta:
        db_table = u'doctos_cm_proeve'

##########################################
##                                      ##
##                POLIZAS               ##
##                                      ##
##########################################
class Recordatorio(models.Model):
    id = models.AutoField(primary_key=True, db_column='RECORDATORIO_ID')
    
    class Meta:
        db_table = u'recordatorios'

class GrupoPolizasPeriodoCo(models.Model):
    id = models.AutoField(primary_key=True, db_column='GRUPO_POL_PERIOD_ID')

    class Meta:
        db_table = 'grupos_polizas_period_co'

class TipoPoliza(models.Model):
    id          = models.AutoField(primary_key=True, db_column='TIPO_POLIZA_ID')
    clave       = models.CharField(max_length=1, db_column='CLAVE')
    nombre      = models.CharField(max_length=30, db_column='NOMBRE')
    tipo_consec = models.CharField(max_length=1, db_column='TIPO_CONSEC')
    prefijo     = models.CharField(max_length=1, db_column='PREFIJO')

    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        db_table = u'tipos_polizas'

class TipoPolizaDet(models.Model):
    id              = models.AutoField(primary_key=True, db_column='TIPO_POLIZA_DET_ID')
    tipo_poliza     = models.ForeignKey(TipoPoliza, db_column='TIPO_POLIZA_ID')
    ano         = models.SmallIntegerField(db_column='ANO')
    mes         = models.SmallIntegerField(db_column='MES')
    consecutivo = models.IntegerField(db_column='CONSECUTIVO')

    def __unicode__(self):
        return u'%s' % self.id
        
    class Meta:
        db_table = u'tipos_polizas_det'

class DoctoCo(models.Model):
    id                      = models.AutoField(primary_key=True, db_column='DOCTO_CO_ID')
    tipo_poliza             = models.ForeignKey(TipoPoliza, db_column='TIPO_POLIZA_ID')
    poliza                  = models.CharField(max_length=9, db_column='POLIZA')
    fecha                   = models.DateField(db_column='FECHA')
    moneda                  = models.ForeignKey(Moneda, db_column='MONEDA_ID')
    tipo_cambio             = models.DecimalField(max_digits=18, decimal_places=6, db_column='TIPO_CAMBIO')
    estatus                 = models.CharField(default='N', max_length=1, db_column='ESTATUS')
    cancelado               = models.CharField(default='N', max_length=1, db_column='CANCELADO')
    aplicado                = models.CharField(default='S', max_length=1, db_column='APLICADO')
    ajuste                  = models.CharField(default='N', max_length=1, db_column='AJUSTE')
    integ_co                = models.CharField(default='S', max_length=1, db_column='INTEG_CO')
    descripcion             = models.CharField(blank=True, null=True, max_length=200, db_column='DESCRIPCION')
    forma_emitida           = models.CharField(default='N', max_length=1, db_column='FORMA_EMITIDA')
    sistema_origen          = models.CharField(max_length=2, db_column='SISTEMA_ORIGEN')
    nombre                  = models.CharField(blank=True, null=True, max_length=30, db_column='NOMBRE')
    grupo_poliza_periodo    = models.ForeignKey(GrupoPolizasPeriodoCo, blank=True, null=True, db_column='GRUPO_POL_PERIOD_ID')
    integ_ba                = models.CharField(default='N', max_length=1, db_column='INTEG_BA')
    
    usuario_creador         = models.CharField(max_length=31, db_column='USUARIO_CREADOR')
    fechahora_creacion      = models.DateTimeField(auto_now_add=True, db_column='FECHA_HORA_CREACION')
    usuario_aut_creacion    = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CREACION')
    usuario_ult_modif       = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif     = models.DateTimeField(auto_now=True, blank=True, null=True, db_column='FECHA_HORA_ULT_MODIF')
    usuario_aut_modif       = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_MODIF')
    usuario_cancelacion     = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CANCELACION')
    fechahora_cancelacion   = models.DateTimeField(auto_now=True, blank=True, null=True, db_column='FECHA_HORA_CANCELACION')
    usuario_aut_cancelacion = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CANCELACION')

    def __unicode__(self):
        return u'%s' % self.id

    class Meta:
        db_table = u'doctos_co'

class DoctosCoDet(models.Model):
    id          = models.AutoField(primary_key=True, db_column='DOCTO_CO_DET_ID')
    docto_co    = models.ForeignKey(DoctoCo, db_column='DOCTO_CO_ID')
    cuenta      = models.ForeignKey(CuentaCo, db_column='CUENTA_ID')
    depto_co    = models.ForeignKey(DeptoCo, db_column='DEPTO_CO_ID')
    tipo_asiento= models.CharField(default='C', max_length=1, db_column='TIPO_ASIENTO')
    importe     = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE')
    importe_mn  = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE_MN')
    ref         = models.CharField(max_length=10, db_column='REFER')
    descripcion = models.CharField(blank=True, null=True, max_length=200, db_column='DESCRIPCION')
    posicion    = models.IntegerField(default=0)
    recordatorio= models.ForeignKey(Recordatorio, blank=True, null=True, db_column='RECORDATORIO_ID')
    fecha       = models.DateField(db_column='FECHA')
    cancelado   = models.CharField(default='N', max_length=1, db_column='CANCELADO')
    aplicado    = models.CharField(default='N', max_length=1, db_column='APLICADO')
    ajuste      = models.CharField(default='N', max_length=1, db_column='AJUSTE')
    moneda      = models.ForeignKey(Moneda, db_column='MONEDA_ID')

    class Meta:
        db_table = u'doctos_co_det'

class DoctosCp(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='DOCTO_CP_ID')
    concepto            = models.ForeignKey(ConceptoCp, db_column='CONCEPTO_CP_ID')
    folio               = models.CharField(max_length=9, db_column='FOLIO')
    naturaleza_concepto = models.CharField(max_length=1, db_column='NATURALEZA_CONCEPTO')
    fecha               = models.DateField(auto_now=True, db_column='FECHA') 
    proveedor           = models.ForeignKey(Proveedor, db_column='PROVEEDOR_ID')
    cancelado           = models.CharField(default='N', max_length=1, db_column='CANCELADO')
    aplicado            = models.CharField(default='S', max_length=1, db_column='APLICADO')
    descripcion         = models.CharField(blank=True, null=True, max_length=200, db_column='DESCRIPCION')
    contabilizado       = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='CONTABILIZADO')
    tipo_cambio         = models.DecimalField(max_digits=18, decimal_places=6, db_column='TIPO_CAMBIO')

    def __unicode__(self):
        return u'%s' % self.id
        
    class Meta:
        db_table = u'doctos_cp'

class ImportesDoctosCP(models.Model):
    id          = models.AutoField(primary_key=True, db_column='IMPTE_DOCTO_CP_ID')
    docto_cp    = models.ForeignKey(DoctosCp, db_column='DOCTO_CP_ID')
    importe     = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE')

    class Meta:
        db_table = u'importes_doctos_cp'
        
class DoctosEntreSis(models.Model):
    class Meta:
        db_table = u'doctos_entre_sis'

class DoctosIn(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='DOCTO_IN_ID')
    folio               = models.CharField(max_length=50, db_column='FOLIO')
    almacen             = models.ForeignKey(Almacenes, db_column='ALMACEN_ID')
    descripcion         = models.CharField(blank=True, null=True, max_length=200, db_column='DESCRIPCION')
    concepto            = models.ForeignKey(ConceptosIn, db_column='CONCEPTO_IN_ID')
    naturaleza_concepto = models.CharField(default='S', max_length=1, db_column='NATURALEZA_CONCEPTO')
    fecha               = models.DateField(auto_now=True, db_column='FECHA') 
    cancelado           = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='CANCELADO')
    aplicado            = models.CharField(default='S',blank=True, null=True, max_length=1, db_column='APLICADO')
    forma_emitida       = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='FORMA_EMITIDA')
    contabilizado       = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='CONTABILIZADO')
    sistema_origen      = models.CharField(default='PV', max_length=2, db_column='SISTEMA_ORIGEN')
    usuario_creador     = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CREADOR')
    fechahora_creacion  = models.DateTimeField(auto_now_add=True, db_column='FECHA_HORA_CREACION')
    usuario_ult_modif   = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif = models.DateTimeField(auto_now=True, blank=True, null=True, db_column='FECHA_HORA_ULT_MODIF')
    
    class Meta:
        db_table = u'doctos_in'

class DoctosInvfis(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='DOCTO_INVFIS_ID')
    almacen             = models.ForeignKey(Almacenes, db_column='ALMACEN_ID')
    folio               = models.CharField(max_length=9, db_column='FOLIO')
    fecha               = models.DateField(auto_now=True, db_column='FECHA') 
    cancelado           = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='CANCELADO')
    aplicado            = models.CharField(default='N',blank=True, null=True, max_length=1, db_column='APLICADO')
    descripcion         = models.CharField(blank=True, null=True, max_length=200, db_column='DESCRIPCION')
    usuario_creador     = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CREADOR')
    fechahora_creacion  = models.DateTimeField(auto_now_add=True, db_column='FECHA_HORA_CREACION')
    usuario_aut_creacion= models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CREACION')
    usuario_ult_modif   = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif = models.DateTimeField(auto_now=True, blank=True, null=True, db_column='FECHA_HORA_ULT_MODIF')
    usuario_aut_modif   = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_MODIF')

    class Meta:
        db_table = u'doctos_invfis'

class DoctosInvfisDet(models.Model):
    id          = models.AutoField(primary_key=True, db_column='DOCTO_INVFIS_DET_ID')
    docto_invfis= models.ForeignKey(DoctosInvfis, db_column='DOCTO_INVFIS_ID')
    clave       = models.CharField(blank=True, null=True, max_length=20, db_column='CLAVE_ARTICULO')
    articulo    = models.ForeignKey(Articulos, db_column='ARTICULO_ID')
    unidades    = models.IntegerField(default=0, blank=True, null=True, db_column='UNIDADES')
    
    class Meta:
        db_table = u'doctos_invfis_det'

class DoctosInDet(models.Model):
    id              = models.AutoField(primary_key=True, db_column='DOCTO_IN_DET_ID')
    doctosIn        = models.ForeignKey(DoctosIn, db_column='DOCTO_IN_ID')
    almacen         = models.ForeignKey(Almacenes, db_column='ALMACEN_ID')
    concepto        = models.ForeignKey(ConceptosIn, db_column='CONCEPTO_IN_ID')
    claveArticulo   = models.CharField(blank=True, null=True, max_length=20, db_column='CLAVE_ARTICULO')
    articulo        = models.ForeignKey(Articulos, db_column='ARTICULO_ID')
    tipo_movto      = models.CharField(default='E', max_length=1, db_column='TIPO_MOVTO')
    unidades        = models.IntegerField(default=0, blank=True, null=True, db_column='UNIDADES')
    costo_unitario  = models.DecimalField(default=0, blank=True, null=True, max_digits=18, decimal_places=2, db_column='COSTO_UNITARIO')
    costo_total     = models.DecimalField(default=0, blank=True, null=True, max_digits=15, decimal_places=2, db_column='COSTO_TOTAL')
    metodo_costeo   = models.CharField(default='C', max_length=1, db_column='METODO_COSTEO')
    cancelado       = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='CANCELADO')
    aplicado        = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='APLICADO')
    costeo_pend     = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='COSTEO_PEND')
    pedimento_pend  = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='PEDIMENTO_PEND')
    rol             = models.CharField(default='N', max_length=1, db_column='ROL')
    fecha           = models.DateField(auto_now=True, blank=True, null=True, db_column='FECHA') 
    #centros_costo = models.ForeignKey(CentrosCosto, db_column='CENTRO_COSTO_ID', blank=True, null=True,)

    class Meta:
        db_table = u'doctos_in_det'
#######################################################VENTAS###############################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
class Cliente(models.Model):
    id              = models.AutoField(primary_key=True, db_column='CLIENTE_ID')
    nombre          = models.CharField(max_length=9, db_column='NOMBRE')
    cuenta_xcobrar  = models.CharField(max_length=9, db_column='CUENTA_CXC')

    class Meta:
        db_table = u'clientes'

class TiposImpuestos(models.Model):
    id      = models.AutoField(primary_key=True, db_column='TIPO_IMPTO_ID')
    nombre  = models.CharField(max_length=30, db_column='NOMBRE')
    tipo    = models.CharField(max_length=30, db_column='TIPO')

    class Meta:
        db_table = u'tipos_impuestos'

class Impuestos(models.Model):
    id              = models.AutoField(primary_key=True, db_column='IMPUESTO_ID')
    tipoImpuesto    = models.ForeignKey(TiposImpuestos, on_delete= models.SET_NULL, blank=True, null=True, db_column='TIPO_IMPTO_ID')
    nombre          = models.CharField(max_length=30, db_column='NOMBRE')
    porcentaje      = models.DecimalField(default=0, blank=True, null=True, max_digits=9, decimal_places=6, db_column='PCTJE_IMPUESTO')

    class Meta:
        db_table = u'impuestos'

class DoctoVe(models.Model):
    id              = models.AutoField(primary_key=True, db_column='DOCTO_VE_ID')
    folio           = models.CharField(max_length=9, db_column='FOLIO')
    fecha           = models.DateField(db_column='FECHA')
    contabilizado   = models.CharField(default='N', max_length=1, db_column='CONTABILIZADO')
    cliente         = models.ForeignKey(Cliente, db_column='CLIENTE_ID')
    tipo            = models.CharField(max_length=1, db_column='TIPO_DOCTO')
    importe_neto    = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE_NETO')
    total_impuestos = models.DecimalField(max_digits=15, decimal_places=2, db_column='TOTAL_IMPUESTOS')
    moneda          = models.ForeignKey(Moneda, db_column='MONEDA_ID')
    tipo_cambio     = models.DecimalField(max_digits=18, decimal_places=6, db_column='TIPO_CAMBIO')
    estado          = models.CharField(max_length=1, db_column='ESTATUS')
    condicion_pago  = models.ForeignKey(CondicionPago, db_column='COND_PAGO_ID')
    
    #almacen = models.ForeignKey(Almacenes, db_column='ALMACEN_ID')
    #condicion_pago = models.ForeignKey(CondicionesPago, on_delete= models.SET_NULL, blank=True, null=True, db_column='COND_PAGO_ID')
    def __unicode__(self):
        return u'%s' % self.id
    class Meta:
        db_table = u'doctos_ve'

class DoctoVeDet(models.Model):
    id = models.AutoField(primary_key=True, db_column='DOCTO_VE_DET_ID')
    docto_ve            = models.ForeignKey(DoctoVe, on_delete= models.SET_NULL, blank=True, null=True, db_column='DOCTO_VE_ID')
    articulo            = models.ForeignKey(Articulos, on_delete= models.SET_NULL, blank=True, null=True, db_column='ARTICULO_ID')
    unidades            = models.DecimalField(max_digits=18, decimal_places=5, db_column='UNIDADES')
    precio_unitario     = models.DecimalField(max_digits=18, decimal_places=6, db_column='PRECIO_UNITARIO')
    porcentaje_decuento = models.DecimalField(max_digits=9, decimal_places=6, db_column='PCTJE_DSCTO')
    precio_total_neto   = models.DecimalField(max_digits=15, decimal_places=2, db_column='PRECIO_TOTAL_NETO')

    class Meta:
        db_table = u'doctos_ve_det'

class ImpuestosArticulo(models.Model):
    id          = models.AutoField(primary_key=True, db_column='IMPUESTO_ART_ID')
    articulo    = models.ForeignKey(Articulos, on_delete= models.SET_NULL, blank=True, null=True, db_column='ARTICULO_ID')
    impuesto    = models.ForeignKey(Impuestos, on_delete= models.SET_NULL, blank=True, null=True, db_column='IMPUESTO_ID')

    class Meta:
        db_table = u'impuestos_articulos'


#############################################################################################################################################################
##################################################MODELOS DE APLICACION DJANGO###############################################################################
#############################################################################################################################################################

class InformacionContable_V(models.Model):
    cuantaxcobrar           = models.ForeignKey(CuentaCo, blank=True, null=True, on_delete= models.SET_NULL, related_name='cuantaxcobrar')
    cobros                  = models.ForeignKey(CuentaCo, blank=True, null=True, on_delete= models.SET_NULL, related_name='cobros')
    descuentos              = models.ForeignKey(CuentaCo, blank=True, null=True, on_delete= models.SET_NULL, related_name='descuentos')
    tipo_poliza_ve          = models.ForeignKey(TipoPoliza, blank=True, null=True, on_delete= models.SET_NULL)
    descripcion_polizas_ve  = models.CharField(max_length=200, blank=True, null=True)
    condicion_pago_contado  = models.ForeignKey(CondicionPago, blank=True, null=True, on_delete= models.SET_NULL)

    def __unicode__(self):
        return u'%s'% self.id

class InformacionContable_CP(models.Model):
    cuentas_por_pagar       = models.ForeignKey(CuentaCo, blank=True, null=True, on_delete= models.SET_NULL, related_name='cuantaxcobrar_cp')
    anticipos               = models.ForeignKey(CuentaCo, blank=True, null=True, on_delete= models.SET_NULL, related_name='cobros_cp')
    descuentos_pronto_pago  = models.ForeignKey(CuentaCo, blank=True, null=True, on_delete= models.SET_NULL, related_name='descuentos_cp')

    def __unicode__(self):
        return u'%s'% self.id

#############################################################################################################################################################
#############################################################################################################################################################
#############################################################################################################################################################