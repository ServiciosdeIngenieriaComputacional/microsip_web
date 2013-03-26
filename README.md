microsip_web
============

INSTALACION

1) Instalar Python 2.7.3 de la pagina http://www.python.org/download/
	Agregar a la variable de entorno de windows "PATH" 
	"C:\Python27;C:\Python27\Lib;C:\Python27\DLLs;C:\Python27\Lib\lib-tk;C:\Python27\Scripts;"
2) Reinstalar firebird (Asegurarse que al instalar de nuevo este seleccionado copiar libreria cliente a carpeta <sistem>)

3) Installar setuptools de la pagina https://pypi.python.org/pypi/setuptools

4) Instalar pip con setup.py install de https://pypi.python.org/pypi/pip

5) Instalar django-auto-complete con el comando "pip install django-autocomplete-light"

6) Instalar libreria de firebird en python "fdb" con el comando "pip install fdb"
	
	It seems you don't have Firebird client library installed, do you? If
	it's installed, then the problem is that FDB can't find it. If you're on
	Windows, try reinstall Firebird and check the option to copy client
	library to Windows/System directory (recommended on Vista/7), or copy it
	there yourself (XP).
	
7) Instalar django-firebird con el comando "pip install django-fiebird"

8) LISTO

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





I guess a test would be to install a package with pip using a --index-url=file:////localhost/c$/some/package/index where /index contains subdirectories of projects:

/index
/pkg
/pkg-0.0.1.tar.gz
The pip command: pip install --index-url=file:////localhost/c$/some/package/index pkg should find and install pkg-0.0.1.tar.gz.

MIGRATIONS

Follow these steps:

Export your data to a fixture using the dumpdata management command
Drop the table
Run syncdb
Reload your data from the fixture using the loaddata management command



