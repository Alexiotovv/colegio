from django.shortcuts import render
from colegio.Apps.Turno.models import Turno

def ListarTurno(request):
	listaturno=Turno.objects.all()
	contexto={'lista':listaturno}
	if	request.method=='POST':
		obj = Turno()
		turno=request.POST.get("nombre")
		seccion_update=request.POST.get("nombre_update")
		idturno=request.POST.get("idturno")
		accion=request.POST.get("accion")

		if accion== 'EDITAR':
			Turno.objects.filter(id=idturno).update(Nombre=turno_update)
		else:
			obj.Nombre=turno
			obj.save()
		return render(request,'turno/list_turno.html',contexto)
	else:
		return render(request,'turno/list_turno.html',contexto)
