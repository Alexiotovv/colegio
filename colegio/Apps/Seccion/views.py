from django.shortcuts import render
from colegio.Apps.Seccion.models import Seccion
from colegio.Apps.Seccion.forms import SeccionForm
from django.views.generic import ListView, UpdateView, CreateView, DeleteView

class SeccionList(ListView):
	model = Seccion
	template_name = 'seccion/list_seccion.html' #template_name es un atributo de la clase

class SeccionCreate(CreateView):
	model = Seccion
	form_class = SeccionForm
	template_name = 'seccion/create_update_seccion.html'
	success_url = '/seccion/create'

class SeccionUpdate(UpdateView):
	model=Seccion
	form_class=SeccionForm
	template_name='seccion/create_update_seccion.html'
	success_url = '/seccion/list/'

class SeccionDelete(DeleteView):
	model=Seccion
	template_name='seccion/delete_seccion.html'
	success_url = '/seccion/list/'

