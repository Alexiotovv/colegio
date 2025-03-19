from django.shortcuts import render,redirect
from django.views.generic import DeleteView,UpdateView
from colegio.Apps.DocenteCurso.models import DocenteCurso
from colegio.Apps.DocenteCurso.forms import DocenteCursoForm
from colegio.Apps.Docente.models import Docente
from colegio.Apps.Curso.models import Curso


###aqui me quedé
def DocenteListarAsginaciones(request):
	listar = DocenteCurso.objects.filter(Docente__User__is_active=True)
	return render(request,'docentecurso/listar_asignaciones.html',{'listar':listar})

def DocenteCursoCreate(request,id_docente):
	docente = Docente.objects.get(id=id_docente)
	excluidos=[]
	if request.method=='POST':
		docecur=DocenteCurso()
		
		cur = Curso()
		cur.id = request.POST.get("Curso")
		docecur.Curso= cur

		doce = Docente()
		doce.id = id_docente
		docecur.Docente = doce

		docecur.save()
  
		docente_list = DocenteCurso.objects.filter(Docente__id=id_docente)
		
		for x in docente_list:
			excluidos.append(x.Curso_id)
		lista_cursos = Curso.objects.exclude(id__in=excluidos)
	
		contexto = {'doce':docente, 'doce_list':docente_list,'lista_cursos':lista_cursos}
  
		return render(request,'docentecurso/create_docentecurso.html',contexto)
	else:
		docente_list = DocenteCurso.objects.filter(Docente__id=id_docente)
		for x in docente_list:
			excluidos.append(x.Curso_id)
		lista_cursos = Curso.objects.exclude(id__in=excluidos)
		contexto = {'doce':docente, 'doce_list':docente_list,'lista_cursos':lista_cursos}
		return render(request,'docentecurso/create_docentecurso.html',contexto)

class DocenteCursoDelete(DeleteView):
	model = DocenteCurso
	template_name = 'docentecurso/delete_docentecurso.html'
	success_url = '/docentes/listar/'

class DocenteCursoUpdate(UpdateView):
	model=DocenteCurso
	form_class=DocenteCursoForm
	template_name='docentecurso/editar_docente_curso.html'
	success_url = '/docentes/listar/'