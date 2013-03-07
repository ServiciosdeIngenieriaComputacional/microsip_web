microsip_web
============


PATH DE PYTHON 

set PYTHONPATH=%PYTHONPATH%;C:\My_python_lib

CONFIGURACION EN APACHE

Primero que nada es necesario instalar apache (xampserver)

1)Descargar el modulo mod_wsgi de "http://code.google.com/p/modwsgi/downloads/list" y gurdarlo en la rota "C:\wamp\bin\apache\apache2.2.22\modules"
  Agregar la siguiente inea de configuracion en apache 
  LoadModule wsgi_module modules/mod_wsgi.so

2) Agregar estas lineas al archivo de configuracion de apache 
  
  WSGIScriptAlias / "C:/wamp/www/microsip_web/microsip_web/django.wsgi"
  Alias /static/ C:/wamp/www/microsip_web/inventarios/static/

AUTOCOMPLETE

Documentacion en: http://django-autocomplete-light.rtfd.org

Repocitorio en github https://github.com/yourlabs/django-autocomplete-light


1) Instalar el paquete con django-autocomplete-light:
	pip install django-autocomplete-light

2) En carpeta static copiar carpeta autocomplete_light de css y js

3) En carpeta templetes copiar carpeta autocomplete_light de templetes

4) Agregar archivo autocomplete_light_registry.py a carpeta de aplicacion

5) En formulario donde se desee aplicar poner el codigo segun el modelo a usar (archivo forms.py):
	#agregar al primcipio del archivo
	import autocomplete_light
	#agregar despues de class Meta:
  	"widgets = autocomplete_light.get_widgets_dict(DoctosInvfisDet)"





