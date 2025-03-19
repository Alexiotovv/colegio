from django.shortcuts import render, redirect
from colegio.Apps.PeriodoAcademico.models import PAcademico
from django.views.generic import ListView, UpdateView, CreateView, DeleteView
from colegio.Apps.PeriodoAcademico.forms import PAcademicoForm

class PAcademicoList(ListView):
	model = PAcademico
	template_name = 'pacademico/listar_pacademico.html' #template_name es un atributo de la clase

def PAcademicoNew(request):
	if request.method=='POST':
		if request.POST.get("Status") =='Activo':
			PAcademico.objects.all().update(Status='Inactivo')
			print("Entro al if")
		paca = PAcademico()
		paca.Nombre=request.POST.get("Nombre")
		paca.FechaInicio=request.POST.get("FechaInicio")
		paca.FechaFinal=request.POST.get("FechaFinal")
		paca.Status=request.POST.get("Status")
		paca.save()
		return redirect('app_pacademico_listar')
	else:
		return render(request,'pacademico/create_pacademico.html')

def PAcademicoUpdate(request,id_paca):
	paca = PAcademico.objects.get(id=id_paca)
	if request.method == 'GET':
		form = PAcademicoForm(instance=paca)
	else:
		form = PAcademicoForm(request.POST,instance=paca)
		PAcademico.objects.all().update(Status='Inactivo')
		if form.is_valid():
			form.save()
		return redirect('app_pacademico_listar')
	contexto = {'form':form}
	return render(request,'pacademico/update_pacademico.html',contexto)

	#model=PAcademico
	#form_class=PAcademicoForm
	#template_name='pacademico/update_pacademico.html'#crear form para el update
	#success_url = '/pacademico/listar/'

class PAcademicoDelete(DeleteView):
	model=PAcademico
	template_name='pacademico/delete_pacademico.html'
	success_url = '/pacademico/listar/'

class PAcademicoDetalle(DeleteView):
	model=PAcademico
	template_name='pacademico/detalle_pacademico.html'
	success_url = '/pacademico/detalle/'
