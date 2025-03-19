from django.shortcuts import render
from colegio.Apps.Nivel.models import Nivel
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from colegio.Apps.Nivel.forms import NivelForm

class NivelList(ListView):
	model=Nivel
	template_name='nivel/list_nivel.html'

class NivelCreate(CreateView):
	model=Nivel
	form_class=NivelForm
	template_name='nivel/create_update_nivel.html'
	success_url='/nivel/list/'

class NivelUpdate(UpdateView):
	model=Nivel
	form_class=NivelForm
	template_name='nivel/create_update_nivel.html'
	success_url='/nivel/list/'

class NivelDelete(DeleteView):
	model=Nivel
	template_name='nivel/delete_nivel.html'
	success_url='/nivel/list'
	