from django.shortcuts import render
from colegio.Apps.AnoAcademico.models import AnoAcademico
from colegio.Apps.Matricula.models import Matricula
from django.views.generic import ListView, UpdateView, CreateView, DeleteView
from colegio.Apps.AnoAcademico.forms import AnoAcademicoForm

class AnoAcademicoList(ListView):
	model = AnoAcademico
	template_name = 'academico/listar_academico.html' #template_name es un atributo de la clase

def AnoAcademicoNew(request):
	ano=AnoAcademico()
	#mat=Matricula()
	#anoultimo = AnoAcademico.objects.last()
	#matri_list = Matricula.objects.filter(AnoAcademico__Ano=anoultimo.Ano)
	object_list = AnoAcademico.objects.all()	
	contexto = {'object_list':object_list}
	if request.method=='POST':
		ano.Ano = request.POST.get('ano')
		ano.FechaInicio = request.POST.get('fechainicio')
		ano.FechaFinal = request.POST.get('fechafinal')
		ano.save()
		return render(request,'academico/listar_academico.html',contexto)
	else:
		return render(request,'academico/create_academico.html')

class AnoAcademicoUpdate(UpdateView):
	model=AnoAcademico
	form_class=AnoAcademicoForm
	template_name='academico/update_academico.html'
	success_url = '/academico/listar/'

class AnoAcademicoDelete(DeleteView):
	model=AnoAcademico
	template_name='academico/delete_academico.html'
	success_url = '/academico/listar/'

class AnoAcademicoDetalle(DeleteView):
	model=AnoAcademico
	template_name='academico/detalle_academico.html'
	success_url = '/academico/detalle_academico/'
