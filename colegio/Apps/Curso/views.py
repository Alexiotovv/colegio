from django.shortcuts import render, redirect
from colegio.Apps.Curso.models import Curso
from django.views.generic import ListView, DeleteView
from colegio.Apps.Curso.forms import CursoForm

class CursoList(ListView):
	#context_obj_name = 'Cursos'
	model = Curso
	template_name = 'curso/listar_cursos.html' #template_name es un atributo de la clase

def NuevoCurso(request):
	if request.method == 'POST':
		curso = Curso()
		#variable para atrapar todos los grados del html
		curso.CodCurso = request.POST.get("CodEvaluacion")
		curso.Nombre = request.POST.get("NombreEvaluacion")
		curso.Orden=request.POST.get("Orden")
		curso.Nivel=request.POST.get("Nivel")
		curso.Tipo = request.POST.get("TipoEvaluacion")
		gra1=request.POST.get("1PRIM")
		gra2=request.POST.get("2PRIM")
		gra3=request.POST.get("3PRIM")
		gra4=request.POST.get("4PRIM")
		gra5=request.POST.get("5PRIM")
		gra6=request.POST.get("6PRIM")
		gra11=request.POST.get("1SEC")
		gra12=request.POST.get("2SEC")
		gra13=request.POST.get("3SEC")
		gra14=request.POST.get("4SEC")
		gra15=request.POST.get("5SEC")
		if gra1=='on':
			gra1='1PRIM'
		else:
			gra1=''
		if gra2=='on':
			gra2='2PRIM'
		else:
			gra2=''
		if gra3=='on':
			gra3='3PRIM'
		else:
			gra3=''
		if gra4=='on':
			gra4='4PRIM'
		else:
			gra4=''
		if gra5=='on':
			gra5='5PRIM'
		else:
			gra5=''
		if gra6=='on':
			gra6='6PRIM'
		else:
			gra6=''
		if gra11=='on':
			gra11='1SEC'
		else:
			gra11=''
		if gra12=='on':
			gra12='2SEC'
		else:
			gra12=''
		if gra13=='on':
			gra13='3SEC'
		else:
			gra13=''
		if gra14=='on':
			gra14='4SEC'
		else:
			gra14=''
		if gra15=='on':
			gra15='5SEC'
		else:
			gra15=''
		grados=(gra1+' '+gra2+' '+gra3+' '+gra4+' '+gra5+' '+gra6+' '+gra11+' '+gra12+' '+gra13+' '+gra14+' '+gra15)
		curso.Grados = grados


		curso.save()	
		return redirect ('app_curso_nuevo')
	else:
		return render(request,'curso/create_curso.html')

def EditarCurso(request,id_curso):
	curso = Curso.objects.get(id=id_curso)
	if request.method == 'GET':
		form = CursoForm(instance=curso)
	else:
		form = CursoForm(request.POST,instance=curso)
		if form.is_valid():
			form.save()
		return redirect('app_curso_listar')
	contexto = {'curso':curso,'form':form}
	return render(request,'curso/update_curso.html',contexto)

class CursoDelete(DeleteView):
	model=Curso
	template_name='curso/delete_curso.html'
	success_url = '/cursos/listar/'

class CursoDetalle(DeleteView):
	model=Curso
	template_name='curso/detalle_curso.html'
	success_url = '/cursos/detalle_curso/'
