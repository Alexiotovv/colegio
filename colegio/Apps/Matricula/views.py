from multiprocessing import context
from urllib import request, response
from django.http import JsonResponse
from django.shortcuts import render, redirect

from colegio.Apps.Matricula.models import Matricula
from colegio.Apps.Alumno.models import Alumno
from colegio.Apps.AnoAcademico.models import AnoAcademico
from django.core.files.storage import FileSystemStorage
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
import pandas as pd
from django.conf import settings

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
	if request.method=='POST':
		file=ImportFile(request.POST,request.FILES)	
		if file.is_valid():
			nombre_archivo=request.FILES['file']
			fs = FileSystemStorage(location=settings.MEDIA_ROOT)
			
			filename = fs.save(nombre_archivo.name, nombre_archivo)
			file_path = fs.path(filename)
			df=pd.read_excel(file_path, engine="openpyxl")
			dni_list = df['DNI'].astype(str).str.strip().str.zfill(8).tolist()

			no_registrados=0
			registrados=0
			ultimo_ano = AnoAcademico.objects.last()

			if len(dni_list)>0:
			# 	#Aquí se hara la importación a la base de datos
				for index, row in df.iterrows():
					print("entro al for del dataframe")
					dni = str(row['DNI']).strip()
					Nombres = row['Nombres']
					ApellidoPaterno = row['ApellidoPaterno']
					ApellidoMaterno = row['ApellidoMaterno']
					Direccion = row['Direccion']
					FechaNacimiento = row['FechaNacimiento']
					Sexo = row['Sexo']
					Grado=row['Grado']
					Seccion=row['Seccion']
					FechaMat=row['FechaMat']
					# Solo guardar si no existe ya en la base de datos
					if not Alumno.objects.filter(DNI=dni).exists():	
						registrados+=1
						alumno = Alumno.objects.create(
							Nombres=Nombres,
							ApellidoPaterno=ApellidoPaterno,
							ApellidoMaterno=ApellidoMaterno,
							Direccion=Direccion,
							FechaNacimiento=FechaNacimiento,
							Sexo=Sexo,
							DNI=dni,
							Estado='A'
						)
						Matricula.objects.create(
							Alumno=alumno,
							AnoAcademico=ultimo_ano,
							Grado=Grado,
							Seccion=Seccion,
							FechaMat=FechaMat
						)
					else:
						no_registrados+=1
						
				Alumno.objects.filter(Estado='A').update(Estado='R')
				Alumno.objects.filter(DNI__in=dni_list).update(Estado='A')
				cantidad_dnis = len(dni_list)
				resultado=f"Se importaron {registrados} registros correctamente. No se importaron {no_registrados} registros. Cantidad de Alumnos Estado=Activo: {cantidad_dnis}"
				
				fs.delete(filename)
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