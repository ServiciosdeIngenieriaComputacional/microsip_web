 #encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
import datetime, time

#Paginacion

# user autentication
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, AdminPasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, permission_required

from django.utils.encoding import smart_str, smart_unicode

@login_required(login_url='/login/')
def index(request):
  	return render_to_response('index.html', {}, context_instance=RequestContext(request))# Create your views here.
