#encoding:utf-8
from django.db import models
from datetime import datetime 
from django.db.models.signals import pre_save
from django.core import urlresolvers

# Create your models here.
class DoctosVe(models.Model):
    id = models.AutoField(primary_key=True, db_column='DOCTO_VE_ID')
    folio = models.CharField(max_length=9, db_column='FOLIO')
    contabilizado = models.CharField(default='N', max_length=1, db_column='CONTABILIZADO')

    class Meta:
        db_table = u'dostos_ve'