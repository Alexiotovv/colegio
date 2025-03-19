from django.shortcuts import render
from colegio.Apps.Grado.models import Grado
from colegio.Apps.Grado.forms import GradoForm
from django.views.generic import ListView,DeleteView,UpdateView,CreateView

class GradoList(ListView):
	model=Grado
	template_name='grado/list_grado.html'

class GradoDelete(DeleteView):
	model=Grado
	template_name = 'grado/delete_grado.html'
	success_url = '/grado/list/'

class GradoCreate(CreateView):
	model=Grado
	form_class=GradoForm
	template_name='grado/create_update_grado.html'
	success_url='/grado/create/'
class GradoUpdate(UpdateView):
	model=Grado
	form_class=GradoForm
	template_name='grado/create_update_grado.html'
	success_url='/grado/list/'
	