import autocomplete_light

from models import Articulos

autocomplete_light.register(Articulos, search_fields=('nombre',),
    autocomplete_js_attributes={'placeholder': 'Nombre ..'})