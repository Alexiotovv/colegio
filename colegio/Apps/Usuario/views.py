from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView

from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import Group

from colegio.Apps.Usuario.forms import RegistroForm
#from django.contrib.auth.forms import UserChangeForm # esto es para Prueba de Changeform
from django.contrib.auth import update_session_auth_hash

def change_password(request):
	if request.method=='POST':
		form = PasswordChangeForm(request.user, request.POST)
		contexto=''
		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request, user)
			success=True
			contexto={'success':success}
		else:
			success=False
			contexto={'success':success}

		return render(request,'usuario/change_password.html',contexto)
	else:
		form = PasswordChangeForm(request.user)
	return render(request, 'usuario/change_password.html',{'form': form})


#class ActualizarForm(UpdateView):
#	model = User
#	template_name = 'usuario/update_usuario.html'
#	form_class = UserChangeForm
#	success_url = '/usuario/listar_usuario'

def RegistroUsuario(request):
	form=RegistroForm(request.POST or None)
	if request.method=='POST':		
		contexto=''
		if form.is_valid():
			user=form.save() # Despues descomentar

			idGrupo = request.POST.get('Lista')#Capturo el nombre del Grupo
			
			#group = Group.objects.get(id='Nombregrupo')
			group = Group.objects.get(id=idGrupo)#Instancio el nombre del Grupo
			user.groups.add(group) #Agrego el nombre del grupo Instanciado al nuevo usuario agregado
			
			form=RegistroForm()
			success=True
			contexto={'success':success}
		else:
			success=False
			contexto={'success':success}
		return render(request,'usuario/create_usuario.html',contexto)
	else:
		form=RegistroForm()
	return render(request,'usuario/create_usuario.html',{'form':form})

class UsuarioList(ListView):
	model = User
	template_name='usuario/listar_usuario.html'

class UsuarioView(DetailView):
	model = User
	template_name = 'usuario/detalle_usuario.html'
	success_url = '/usuario/detalle/'
