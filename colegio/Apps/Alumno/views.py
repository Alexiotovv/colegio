from django.shortcuts import render, get_object_or_404, redirect
from colegio.Apps.Alumno.models import Alumno
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.generic import ListView, CreateView,UpdateView,DeleteView,DetailView
from colegio.Apps.Alumno.forms import AlumnoForm
from django.db.models import ProtectedError


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

def editar_alumno(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id)
    if request.method == 'POST':
        form = AlumnoForm(request.POST, instance=alumno)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            print("error de form is valid")
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = AlumnoForm(instance=alumno)
        # Puedes usar esto para cargar el formulario como HTML si deseas
        return JsonResponse({
            'DNI': alumno.DNI,
            'ApellidoPaterno': alumno.ApellidoPaterno,
            'ApellidoMaterno': alumno.ApellidoMaterno,
            'Nombres': alumno.Nombres,
            'Sexo': alumno.Sexo,
            'FechaNacimiento': alumno.FechaNacimiento.strftime('%Y-%m-%d'),
			'Direccion': alumno.Direccion,
			'Estado': alumno.Estado
        })

def eliminar_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)

    if request.method == 'POST':
        try:
            alumno.delete()
            messages.success(request, "Alumno eliminado correctamente.")
            return redirect('app_alumno_listar')
        except ProtectedError:
            messages.error(request, "No se puede eliminar el alumno porque tiene registros relacionados.")
            return redirect('app_alumno_listar')
    else:
    	return render(request, 'alumno/delete_alumno.html', {'object': alumno})

class AlumnoDetalle(DetailView):
	model=Alumno
	template_name='alumno/detalle_alumno.html'
	success_url = '/alumnos/detalle_alumno/'