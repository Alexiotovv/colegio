from django.shortcuts import render
from colegio.Apps.Notas.models import Notas,NotasComp
from colegio.Apps.AvanceNotas.models import AvanceNotas, AvanceNotasComp
from colegio.Apps.PeriodoAcademico.models import PAcademico
from colegio.Apps.AnoAcademico.models import AnoAcademico
from colegio.Apps.Curso.models import Curso
from colegio.Apps.Docente.models import Docente
from colegio.Apps.DocenteCurso.models import DocenteCurso
from django.contrib.auth.models import User

def is_member(user):
    return user.groups.filter(name='Administrador').exists()

def BuscarNotas(request):
	ano=AnoAcademico.objects.all().order_by('-id')
	paca=PAcademico.objects.all().order_by('id')
	curso= DocenteCurso.objects.filter(Docente__User__id=request.user.id)

	docente = Docente.objects.get(User__id=request.user.id)
	grados_list = str(docente.GradoNivel).split()#Extrae los grados de la cadena y los pone en lista
	secciones_list = str(docente.Seccion).split()#Extrae las secciones de la cadena y los pone en lista
	contexto={'ano':ano,'paca':paca,'curso':curso,'grados_list':grados_list,'secciones_list':secciones_list}

	if request.method =='POST':
		grado=request.POST.get("grado")
		seccion=request.POST.get("seccion")
		ano=request.POST.get("ano")

		pac=PAcademico()
		pac.id=request.POST.get("pacademico")

		an=AnoAcademico()
		an.id=request.POST.get("ano")

		cur = Curso()
		cur.id=request.POST.get("curso")

		notita = NotasComp.objects.filter(Curso=cur,Matricula__Grado=grado,Matricula__Seccion=seccion,Matricula__AnoAcademico=an,PAcademico=pac)
		contexto_notas={'notita':notita}
		return render(request, 'buscar_notas/listar_notas_buscadas.html',contexto_notas)	
	else:
		return render(request, 'buscar_notas/buscar_notas.html',contexto)
	
	


	# model = Notas
	# nota= ''
	# ano=AnoAcademico.objects.all().order_by('-Ano')
	# paca=PAcademico.objects.all().order_by('id')
	# curso=Curso.objects.all().order_by('Nivel','Orden')

	# docente = Docente.objects.get(User__id=request.user.id)
	# gra_list = str(docente.GradoNivel).split()#Extrae los grados de la cadena y los pone en lista
	# sec_list = str(docente.Seccion).split()#Extrae las secciones de la cadena y los pone en lista

	# contexto={'ano':ano,'paca':paca,'gra_list':gra_list,'sec_list':sec_list,'curso':curso}

	# if request.method =='POST':
	# 	grado=request.POST.get("grado")
	# 	seccion=request.POST.get("seccion")
	# 	anop=request.POST.get("ano")

	# 	pac=PAcademico()
	# 	pac.id=request.POST.get("pacademico")

	# 	an=AnoAcademico()
	# 	an.id=request.POST.get("ano")

	# 	cur = Curso()
	# 	cur.id=request.POST.get("curso")

	# 	#Aqui Poner si es Administrador o Docente para que pueda ver todo
	# 	notita = Notas.objects.filter(Curso=cur,Matricula__Grado=grado,Matricula__Seccion=seccion,Matricula__AnoAcademico=an,PAcademico=pac, Docente__User__id=request.user.id)
	# 	if is_member(request.user):
	# 		notita = NotasComp.objects.filter(Curso=cur,Matricula__Grado=grado,Matricula__Seccion=seccion,Matricula__AnoAcademico=an,PAcademico=pac)			
	# 	contexto_notas={'notita':notita}
	# 	return render(request, 'buscar_notas/listar_notas_buscadas.html',contexto_notas)	
	# else:
	# 	return render(request, 'buscar_notas/buscar_notas.html',contexto)

def BuscarAvanceNotas(request):

	ano=AnoAcademico.objects.all().order_by('-id')
	paca=PAcademico.objects.all().order_by('id')
	curso=DocenteCurso.objects.filter(Docente__User__id=request.user.id)
	
	docente = Docente.objects.get(User__id=request.user.id)
	grados_list = str(docente.GradoNivel).split()#Extrae los grados de la cadena y los pone en lista
	secciones_list = str(docente.Seccion).split()#Extrae las secciones de la cadena y los pone en lista
	contexto={'ano':ano,'paca':paca,'curso':curso,'grados_list':grados_list,'secciones_list':secciones_list}

	if request.method =='POST':
		grado=request.POST.get("grado")
		seccion=request.POST.get("seccion")
		anop=request.POST.get("ano")

		pac=PAcademico()
		pac.id=request.POST.get("pacademico")

		an=AnoAcademico()
		an.id=request.POST.get("ano")

		cur = Curso()
		cur.id=request.POST.get("curso")

		notita = AvanceNotasComp.objects.filter(Curso=cur,Matricula__Grado=grado,Matricula__Seccion=seccion,Matricula__AnoAcademico=an,PAcademico=pac)
		contexto_notas={'notita':notita}
		return render(request, 'buscar_notas/listar_avancenotas_buscadas.html',contexto_notas)	
	else:
		return render(request, 'buscar_notas/buscar_avancenotas.html',contexto)

# def BuscarAvanceNotasComp(request):

# 	ano=AnoAcademico.objects.all().order_by('-id')
# 	paca=PAcademico.objects.all().order_by('id')
# 	curso=Curso.objects.all()
# 	contexto={'ano':ano,'paca':paca,'curso':curso}

# 	if request.method =='POST':
# 		grado=request.POST.get("grado")
# 		seccion=request.POST.get("seccion")
# 		anop=request.POST.get("ano")

# 		pac=PAcademico()
# 		pac.id=request.POST.get("pacademico")

# 		an=AnoAcademico()
# 		an.id=request.POST.get("ano")

# 		cur = Curso()
# 		cur.id=request.POST.get("curso")

# 		notita = AvanceNotasComp.objects.filter(Curso=cur,Matricula__Grado=grado,Matricula__Seccion=seccion,Matricula__AnoAcademico=an,PAcademico=pac)
# 		contexto_notas={'notita':notita}
# 		return render(request, 'buscar_notas/listar_avancenotas_buscadas.html',contexto_notas)	
# 	else:
# 		return render(request, 'buscar_notas/buscar_avancenotas.html',contexto)