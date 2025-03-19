from django.shortcuts import render
from colegio.Apps.Apoderado.models import Apoderado
from django.contrib import messages
from django.http import HttpResponse
from django.views.generic import ListView, CreateView,UpdateView,DeleteView
from colegio.Apps.Apoderado.forms import ApoderadoForm

class ApoderadoList(ListView):
	#context_obj_name = 'alumnos'
	model = Apoderado
	template_name = 'apoderado/listar_apoderado.html' #template_name es un atributo de la clase

class ApoderadoNew(CreateView):
	model = Apoderado
	form_class = ApoderadoForm
	template_name = 'apoderado/create_update_apoderado.html'
	success_url = '/apoderados/nuevo/'

class ApoderadoUpdate(UpdateView):
	model=Apoderado
	form_class=ApoderadoForm
	template_name='apoderado/create_update_apoderado.html'
	success_url = '/apoderados/listar/'

class ApoderadoDelete(DeleteView):
	model=Apoderado
	template_name='apoderado/delete_apoderado.html'
	success_url = '/apoderados/listar/'

class ApoderadoDetalle(DeleteView):
	model=Apoderado
	template_name='apoderado/detalle_apoderado.html'
	success_url = '/apoderados/editar/'