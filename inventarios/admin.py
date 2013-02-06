import autocomplete_light
from inventarios.models import Articulos, DoctosInvfisDet
from django.contrib import admin

class DoctosInvfisDetAdmin(admin.ModelAdmin):
    articulo = autocomplete_light.modelform_factory(Articulos)

admin.site.register(DoctosInvfisDet, DoctosInvfisDetAdmin)
admin.site.register(Articulos)
