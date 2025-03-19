from multiprocessing import context
from urllib import request, response
from django.http import JsonResponse
from django.shortcuts import render, redirect

from colegio.Apps.Matricula.models import Matricula
from colegio.Apps.Alumno.models import Alumno
from colegio.Apps.AnoAcademico.models import AnoAcademico

# from django.contrib import messages
# from django.http import HttpResponse
from django.views.generic import CreateView,  DetailView, DeleteView, UpdateView
from colegio.Apps.Matricula.forms import MatriculaForm
from colegio.Apps.Alumno.forms import AlumnoForm
from colegio.Apps.AnoAcademico.forms import AnoAcademicoForm
#from braces.views import GroupRequiredMixin, LoginRequiredMixin

from datetime import *

from colegio.Apps.Matricula.forms import ImportFile
from colegio.Apps.Matricula.functions.functions import handle_uploaded_file

from openpyxl import Workbook, load_workbook
from django.shortcuts import get_object_or_404


def MatriculaPrincipal(request):
	return render(request,'matricula/matricula_principal.html')

def GuardaNuevaMatricula(request):
	msje={}
	existe=Matricula.objects.filter(
		Grado=request.POST.get("grado"),
		Seccion=request.POST.get("seccion"),
		Alumno_id=request.POST.get("alumno"),
		AnoAcademico_id=request.POST.get("academico")
		)
	if existe:
		msje={'Mensaje':'existe'}
	else:
		obj = Matricula()
		obj.AnoAcademico_id = request.POST.get("academico")
		obj.Grado=request.POST.get("grado")
		obj.Seccion=request.POST.get("seccion")
		obj.Alumno_id=request.POST.get("alumno")
		obj.FechaMat=request.POST.get("fechamat")
		obj.save()
		msje={'Mensaje':'ok'}
	return JsonResponse(msje)

def NuevaMatricula(request):
	ano_actual = AnoAcademico.objects.get(Ano=datetime.now().year)
	alu=Alumno.objects.filter(Estado='A')
	ano= AnoAcademico.objects.all().order_by('-id')
	return render(request,'matricula/matricula_nueva.html',{'alu':alu,'ano':ano})

def ListarMatriculaPorNiveles(request):
	if request.method=='POST':
		ano = request.POST.get("academico")
		grado=request.POST.get("grado")
		seccion=request.POST.get("seccion")

		mat_list = list(Matricula.objects.filter(AnoAcademico=ano,Grado=grado,Seccion=seccion,Alumno__Estado='A').values('id','Alumno__DNI','Alumno__ApellidoPaterno','Alumno__ApellidoMaterno','Alumno__Nombres','AnoAcademico_id','Grado','Seccion').order_by('Alumno__ApellidoPaterno','Alumno__ApellidoMaterno','Alumno__Nombres'))

	return JsonResponse(mat_list,safe=False)
	# return render(request,'matricula/listar_matricula.html',contexto2)

def MatriculaPorNiveles(request):
	anoacademico= AnoAcademico.objects.all().order_by('-id')
	contexto={'anoacademico':anoacademico}
	return render(request,'matricula/matriculaporniveles.html',contexto)

def NewMatriculaAlumno(request):
	lista_anos=AnoAcademico.objects.all().order_by('-id')
	guar=''
	mensaje_dni=''
	if request.method=='POST':
		dni=Alumno.objects.filter(DNI=request.POST.get('dni'))#busca dni
		if dni.exists():
			mensaje_dni='DNI  ya existe!'
		else:	
			alu= Alumno()
			mat=Matricula()

			alu.Nombres=request.POST.get('nombres')
			alu.ApellidoPaterno=request.POST.get('apellidopaterno')
			alu.ApellidoMaterno=request.POST.get('apellidomaterno')
			alu.Direccion='Calle000'
			alu.DNI=request.POST.get('dni')
			alu.FechaNacimiento='1999-08-01'
			alu.Sexo='M'
			alu.Estado='A'
			alu.save()
			ultimo_alu=Alumno.objects.last()#obteniendo el ultimo registro
			
			alu=Alumno()
			alu.id=ultimo_alu.id
				
			aaa=AnoAcademico()
			aaa.id=request.POST.get('anoacademico')
			
			mat.Alumno=alu
			mat.AnoAcademico=aaa
			mat.FechaMat=datetime.now()
			mat.Grado=request.POST.get('grado')
			mat.Seccion=request.POST.get('seccion')
			mat.save()
			guar='ok'
		contexto={'lista_anos':lista_anos,'guar':guar,'mensaje_dni':mensaje_dni}
		return render(request,'matricula/new_matricula_alumno.html',contexto)
	else:
		guar=''
		contexto={'lista_anos':lista_anos,'guar':guar,'mensaje_dni':mensaje_dni}
		return render(request,'matricula/new_matricula_alumno.html',contexto)


def ImportarArchivo(request):
	num=1
	if request.method=='POST':
		file=ImportFile(request.POST,request.FILES)	
		if file.is_valid():
			nombre_archivo=str(request.FILES['file'])
			if nombre_archivo=="Formato_Importacion_Matricula.xlsx":
				ruta = "/var/www/vhosts/colegio_venv/colegio/static/upload/Formato_Importacion_Matricula.xlsx"
				# ruta = "static/upload/Formato_Importacion_Matricula.xlsx"
				handle_uploaded_file(request.FILES['file'],ruta)
				
				Libro = load_workbook(ruta)
				Hoja1 = Libro.active
				
				C1=Hoja1["A1"].value
				C2=Hoja1["B1"].value
				C3=Hoja1["C1"].value
				C4=Hoja1["D1"].value
				C5=Hoja1["E1"].value
				C6=Hoja1["F1"].value
				C7=Hoja1["G1"].value
				C8=Hoja1["H1"].value
				C9=Hoja1["I1"].value
				C10=Hoja1["J1"].value
				C11=Hoja1["K1"].value
				C12=Hoja1["L1"].value

				reg=Hoja1["E2"].value
				resultado= ""
				#1. Primero Prueba la plantilla del excel si es el corecto
				if CompruebaExcel(C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11,C12):
					#2. Comprueba si hay registros
					if CompruebaRegistros(reg):
						sigue=True
						celdavacia=False
						while sigue:
							num=num+1
							dato=Hoja1["E"+str(num)].value
							if dato==None:
								sigue=False
							else:
								m1=Hoja1["A"+str(num)].value
								m2=Hoja1["B"+str(num)].value
								m3=Hoja1["C"+str(num)].value
								m4=Hoja1["D"+str(num)].value
								m5=Hoja1["E"+str(num)].value
								m6=Hoja1["F"+str(num)].value
								m7=Hoja1["G"+str(num)].value
								m8=Hoja1["H"+str(num)].value
								m9=Hoja1["I"+str(num)].value
								m10=Hoja1["J"+str(num)].value
								m11=Hoja1["K"+str(num)].value
								m12=Hoja1["L"+str(num)].value
								if CompruebaCeldasVacias(m1,m2,m3,m4,m5,m6,m7,m8,m9,m10,m11,m12):
									resultado=resultado + ", Existen Celdas Vacías, revise por favor"
									break
								if nombre_archivo!='Formato_Importacion_Matricula.xlsx':
									resultado=resultado + ", El nombre del Archivo, no es el Correcto"
									break
					else:
						resultado="No hay Registro en la primera Fila para Importar"
				else:
					resultado="Al parecer no está usando la plantilla o ha sido modificado"
				
				#Desde Aquí se Hará la importación
				no_registrados=0
				if resultado=='':
					#Aquí se hara la importación a la base de datos
					###AQUIIIIIIIIII###
					
					for x in range(2,num):
						alu=Alumno()
						if (str(alu.DNI)==str(Hoja1["E"+str(x)].value)):
							no_registrados=no_registrados+1
						else:
							alu.ApellidoPaterno=Hoja1["A"+str(x)].value
							alu.ApellidoMaterno=Hoja1["B"+str(x)].value
							alu.Nombres=Hoja1["C"+str(x)].value
							alu.Direccion=Hoja1["D"+str(x)].value
							alu.DNI=Hoja1["E"+str(x)].value
							alu.FechaNacimiento=Hoja1["F"+str(x)].value
							alu.Sexo=Hoja1["G"+str(x)].value
							alu.Estado=Hoja1["H"+str(x)].value
							alu.save()
							ult_reg_alu=Alumno.objects.last()
							
							mat=Matricula()
							
							alu=Alumno()
							alu.id=ult_reg_alu.id
							mat.Alumno=alu#Llave foránea Instanceada de ALumno
							
							aaca=AnoAcademico.objects.get(Ano=Hoja1["I"+str(x)].value)
							aac=AnoAcademico()
							aac.id=aaca.id
							mat.AnoAcademico= aaca

							mat.Grado= Hoja1["J"+str(x)].value
							mat.Seccion= Hoja1["K"+str(x)].value
							mat.FechaMat= Hoja1["L"+str(x)].value
							mat.save()

					resultado="Los regitros se importaron Correctamente. Alumnos no registrados: "+ str(no_registrados)+ " (alumnos ya existen.)"
				Libro.save(ruta)
			else:
				resultado="Nombre de Archivo Incorrecto"
			context={'resultado':resultado}
			return render(request,'matricula/mensaje_importado.html',context)
	else:
		file=ImportFile()#ImportFile es el Form
		return render(request,'matricula/importar_matriculas.html',{'form':file})

def CompruebaCeldasVacias(m1,m2,m3,m4,m5,m6,m7,m8,m9,m10,m11,m12):
	if m1=='' or m2=='' or m3=='' or m4=='' or m5=='' or m6=='' or m7=='' or m8=='' or m9=='' or m10=='' or m11=='' or m12=='':
		msa=True
	else:
		msa=False
	return(msa)
def CompruebaRegistros(valor):
	if valor=='':
		ms=False
	else:
		ms=True
	return(ms)

def CompruebaExcel(C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11,C12):
	if C1=="ApellidoPaterno" and C2=="ApellidoMaterno" and C3=="Nombres" and C4=="Direccion" and C5=="DNI" and C6=="FechaNacimiento" and C7=="Sexo" and C8=="Estado" and C9=="AñoAcadémico" and C10=="Grado" and C11=="Seccion" and C12=="FechaMat":
		rpta=True
	else:
		rpta=False
	return(rpta)

def PlantillaMatriculados(request):
	Ruta="https://colcoopcv.com/static/files/Formato_Importacion_Matricula.xlsx"
	return redirect(Ruta)
class MatriculaNew(CreateView):#con Vista 
	model = Matricula
	template_name = 'matricula/create_update_matricula.html'
	form_class = MatriculaForm
	second_form_class = AlumnoForm
	success_url = '/matricula/listar/'

def MatriculaNewEvent(request,id_alumno):	
	if request.method == 'POST':
		matri = Matricula()

		alum = Alumno()
		alum.id = id_alumno
		matri.Alumno= alum

		aac = AnoAcademico()
		ano_academico = AnoAcademico.objects.get(Ano=datetime.now().year)
		aac.id = ano_academico.id
		matri.AnoAcademico=aac

		#Grado, Nivel,	#Sección, Fecha vienen de POST
		matri.Grado = request.POST.get("Grado")
		matri.Seccion = request.POST.get("Seccion")
		matri.FechaMat = request.POST.get("FechaMat")
		matri.save()

		return redirect('app_matricula_listar')
	else:
		alumno = Alumno.objects.get(id=id_alumno)#esto es para el nombre del alumno en la parte superior
		ano = AnoAcademico.objects.get(Ano=datetime.now().year)
		#matri = Matricula.objects.get(Alumno=id_alumno)
		#Cuando se instancia todo el modelo se puede 
		#referencias todas las tablas referenciadas Ejm. en el html "matri.Alumno.Nombres" 
		form=MatriculaForm()
		form.fields['Alumno'].queryset = Alumno.objects.filter(id=id_alumno)
		#.objects.filter(id=id_alumno)
		contexto = {'alum':alumno,'ano':ano,'form':form}		
	return render(request,'matricula/create_matricula.html', contexto)
def PasarTodosNuevoAno(request):
	ano = AnoAcademico.objects.all()	
	if request.method=='POST':
		ul_reg_ano=AnoAcademico.objects.last()
		uano=int(ul_reg_ano.Ano)-1
		#ulti_ano=AnoAcademico.objects.get(Ano=uano)
		todas_matriculas=Matricula.objects.filter(AnoAcademico__Ano=uano,Alumno__Estado='A')		
		for mat in todas_matriculas:
			NGrado=NuevoGrado(mat.Grado)
			if NGrado!='False':
				new_mat=Matricula()
				new_mat.Grado   = NGrado
				new_mat.Seccion = mat.Seccion
				new_mat.FechaMat= datetime.now()
				new_mat.Alumno  =  mat.Alumno
				new_mat.AnoAcademico  =  ul_reg_ano
				new_mat.save()
			else:
				Alumno.objects.filter(id=mat.Alumno.id).update(Estado='E')

		matriculados=Matriculas_Ultimo_Ano()
		contexto={'ano_list':ano,'matriculados':matriculados}
		
		return redirect('app_matricula_listar')
		#return render(request,'matricula/mensaje_pase_año.html')
	else:
		return render(request,'matricula/mensaje_pase_ano.html')
def MatriculaList(request):
	ano = AnoAcademico.objects.all().order_by('-id')
	if request.method=='POST':
		aaa = AnoAcademico()
		aaa.id = request.POST.get("ano")
		ano_escogido = AnoAcademico.objects.get(id=aaa.id)
		ano_selected=ano_escogido.Ano
		mat_list = Matricula.objects.filter(AnoAcademico=aaa.id,Alumno__Estado='A') 
		matriculados=Matriculas_Ultimo_Ano()
		contexto2={'mat_list':mat_list,'ano_list':ano,'matriculados':matriculados,'ano_selected':ano_selected}
		return render(request,'matricula/listar_matricula.html',contexto2)
	else:
		matriculados=Matriculas_Ultimo_Ano()
		ulti_ano=AnoAcademico.objects.last()
		mat_list = Matricula.objects.filter(AnoAcademico=ulti_ano.id,Alumno__Estado='A') 
		contexto={'ano_list':ano,'matriculados':matriculados,'mat_list':mat_list}
		return render(request,'matricula/listar_matricula.html',contexto)

def MatriculaDelete(request, id):
    try:
        Matricula.objects.filter(id=id).delete()
        return JsonResponse({'data':'success','status':'200'})
    except Exception as e:
        return JsonResponse({"data":'ocurrió un error '+str(e),'status':500})

	
class MatriculaDetalle(DetailView):
	model = Matricula
	template_name = 'matricula/detalle_matricula.html'
	success_url = '/matricula/detalle_matricula/'
class MatriculaUpdate(UpdateView):
	model = Matricula
	form_class = MatriculaForm
	template_name = 'matricula/create_update_matricula.html'
	success_url = '/matricula/listar'

####Esta función será para verificar El duplicado de DNI
def VerificarDni(request):
	dni=request.POST.get('dni')
	print(dni)
	contexto={'existe':Alumno.objects.filter(DNI=dni).exists()}
	if contexto['existe']:
		contexto['mensaje']='Un Alumno con el DNI ingresado ya existe'
	return JsonResponse(contexto)

def Matriculas_Ultimo_Ano():
	ulti_ano=AnoAcademico.objects.last()
	#Desdeaqui verifica si ya existen matriculados con el último año registrado
	mats=Matricula.objects.filter(AnoAcademico=ulti_ano.id)
	if mats:
		matriculados=True
	else:
		matriculados=False

	return(matriculados)

def NuevoGrado(grado):
	if grado=='5SEC':
		Ngrado='False'
	else:
		if grado=='4SEC':
			Ngrado='5SEC'
		else:
			if grado=='3SEC':
				Ngrado='4SEC'
			else:
				if grado=='2SEC':
					Ngrado='3SEC'
				else:
					if grado=='1SEC':
						Ngrado='2SEC'
					else:
						if grado=='6PRIM':
							Ngrado='1SEC'
						else:
							if grado=='5PRIM':
								Ngrado='6PRIM'
							else:
								if grado=='4PRIM':
									Ngrado='5PRIM'
								else:
									if grado=='3PRIM':
										Ngrado='4PRIM'
									else:
										if grado=='2PRIM':
											Ngrado='3PRIM'
										else:
											if grado=='1PRIM':
												Ngrado='2PRIM'
	return(Ngrado)