from django.shortcuts import render
from colegio.Apps.Alumno.models import Alumno
from django.contrib import messages
from django.http import HttpResponse
from django.views.generic import ListView, CreateView,UpdateView,DeleteView,DetailView
from colegio.Apps.Alumno.forms import AlumnoForm
#def index(request):
#	return render(request, 'Home/index.html')


def AlumnoList(request):	
	if request.method=='POST':
		return render(request,'alumno/listar_alumnos.html',contexto)
	else:	
		list_alumnos=Alumno.objects.filter(Estado='A')
		contexto={'list_alumnos':list_alumnos}
		return render(request,'alumno/listar_alumnos.html',contexto)

def AlumnoListNoActivos(request):
	if request.method=='POST':
		return render(request,'alumno/listar_alumnos_noactivos.html',contexto)
	else:
		list_alumnos=Alumno.objects.exclude(Estado='A')
		contexto={'list_alumnos':list_alumnos}
		return render(request,'alumno/listar_alumnos_noactivos.html',contexto)

class AlumnoNew(CreateView):
	model = Alumno
	form_class = AlumnoForm
	template_name = 'alumno/create_update_alumno.html'
	success_url = '/alumnos/listar'

class AlumnoUpdate(UpdateView):
	model=Alumno
	form_class=AlumnoForm
	template_name='alumno/create_update_alumno.html'
	success_url = '/alumnos/listar/'

class AlumnoDelete(DeleteView):
	model=Alumno
	template_name='alumno/delete_alumno.html'
	success_url = '/alumnos/listar/'

class AlumnoDetalle(DetailView):
	model=Alumno
	template_name='alumno/detalle_alumno.html'
	success_url = '/alumnos/detalle_alumno/'