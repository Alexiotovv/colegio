from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import ListView, UpdateView, DeleteView, DetailView
from colegio.Apps.Docente.forms import DocenteForm
from colegio.Apps.Docente.models import Docente
from django.contrib.auth.models import User

class DocenteList (ListView):
	model = Docente
	template_name = 'docente/listar_docentes.html'

def DocenteNew (request,id_user):
	if request.method == 'POST':
		doce=Docente()
		
		usu=User()
		usu.id=id_user
		doce.User=usu
		
		#DNI, Gradoynivel, Seccion...etc
		doce.DNI = request.POST.get("DNI")
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
		doce.GradoNivel = grados#Campo

		secA=request.POST.get("A")
		secB=request.POST.get("B")
		secC=request.POST.get("C")
		secD=request.POST.get("D")
		secE=request.POST.get("E")
		secF=request.POST.get("F")
		secG=request.POST.get("G")

		if secA=='on':
			secA='A'
		else:
			secA=''
		if secB=='on':
			secB='B'
		else:
			secB=''
		if secC=='on':
			secC='C'
		else:
			secC=''
		if secD=='on':
			secD='D'
		else:
			secD=''

		if secE=='on':
			secE='E'
		else:
			secE=''

		if secF=='on':
			secF='F'
		else:
			secF=''

		if secG=='on':
			secG='G'
		else:
			secG=''
		secciones=(secA+' '+secB+' '+secC+' '+secD+' '+secE+' '+secF+' '+secG)
		doce.Seccion=secciones#Campo Secciones
		doce.Direccion=request.POST.get("Direccion")
		doce.FechaNacimiento=request.POST.get("FechaNacimiento")
		doce.Sexo=request.POST.get("Sexo")
		doce.Telefono=request.POST.get("Telefono")
		doce.TutorGrado=request.POST.get("tutor_grado")
		doce.TutorSeccion=request.POST.get("tutor_seccion")
		doce.save()
		return redirect('app_docente_listar')
	else:
		usuario=User.objects.get(id=id_user)
		contexto={'usu':usuario}
		return render(request,'docente/create_docente.html',contexto)

def DocenteUpdate(request,id_docente):
	docente = Docente.objects.get(id=id_docente)
	if request.method == 'GET':
		form = DocenteForm(instance=docente)
	else:
		form = DocenteForm(request.POST,instance=docente)
		if form.is_valid():
			form.save()
		return redirect('app_docente_listar')
	contexto = {'docente':docente,'form':form}
	return render(request,'docente/update_docente.html',contexto)

class DocenteDelete (DeleteView):
	model = Docente
	template_name = 'docente/delete_docente.html'
	success_url = '/docentes/listar/'

class DocenteDetalle (DetailView):
	model = Docente
	template_name = 'docente/detalle_docente.html'
	success_url = '/docentes/listar/'
