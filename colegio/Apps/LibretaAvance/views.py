from ast import For, If
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse

from openpyxl import Workbook,load_workbook
from django.db import connection ##permite conectar directamente a la base de datos

from colegio.Apps.Matricula.models import Matricula
from colegio.Apps.Alumno.models import Alumno
from colegio.Apps.Curso.models import Curso
from colegio.Apps.Notas.models import Notas,NotasComp
from colegio.Apps.AvanceNotas.models import AvanceNotas
from colegio.Apps.AvanceNotas.models import AvanceNotasComp
from colegio.Apps.AnoAcademico.models import AnoAcademico
from colegio.Apps.Docente.models import Docente
from colegio.Apps.PeriodoAcademico.models import PAcademico
from colegio.Apps.Competencias.models import CompetenciaCurso
from colegio.Apps.Pagos.models import Pagos
# from colegio.Apps.OtrasOpciones.views import FinalPrim, FinalSecun, calculo_promedio, numeros_a_letras
from colegio.Apps.OtrasOpciones.views import *

from colegio.Apps.Matricula.forms import MatriculaForm
from colegio.Apps.Notas.forms import NotasForm
from colegio.Apps.Alumno.forms import AlumnoForm
from colegio.Apps.Docente.forms import DocenteForm
from colegio.Apps.Curso.forms import CursoForm
from colegio.Apps.PeriodoAcademico.forms import PAcademicoForm
from colegio.Apps.AnoAcademico.forms import AnoAcademicoForm
from math import *
from datetime import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from colegio.Apps.Apis.models import Venta
from django.db.models import Count


def ImprimirAvancesxAlumno(request):

    if  request.method=='POST':
        gradonivel = request.POST.get("Grado")
        seccion = request.POST.get("Seccion")
        ano = request.POST.get("AnoAcademico")#El año que manda del form
        paca=request.POST.get("Pacademico")
        paca=int(paca)
        idMat=request.POST.get("idMat")
        nivel=str(gradonivel)[1:len(gradonivel)] #extrae solo PRIM
        grado=str(gradonivel)[0:1]
        #cursos=Curso.objects.filter(Nivel=nivel)

        if nivel=='PRIM':
            nivel='PRIMARIO'
        else:
            nivel='SECUNDARIO'
        paca=int(paca)
        nombrepaca=PAcademico.objects.get(id=paca)

        result = Curso.objects.raw('SELECT 1 as id,ccur."Curso_id" as IDCURSO,Count(*)-1 as NUM_COMPE FROM "Competencias_competenciacurso" as ccur GROUP BY ccur."Curso_id" ORDER BY ccur."Curso_id"')

        notas=AvanceNotasComp.objects.filter(PAcademico_id=paca,Matricula__AnoAcademico__Ano=ano,Matricula__Grado=gradonivel,Matricula__Seccion=seccion).order_by('Curso__Orden','Competencias__Orden')
        tutor=Docente.objects.filter(TutorGrado=gradonivel,TutorSeccion=seccion).last()
        matricula = Matricula.objects.filter(id=idMat,Grado=gradonivel,Seccion=seccion,AnoAcademico__Ano=ano).order_by('Alumno__ApellidoPaterno','Alumno__ApellidoMaterno','Alumno__Nombres')

        contexto={'grado':grado,'result':result,'tutor':tutor,'matricula':matricula,'nivel':nivel,'nombrepaca':nombrepaca,'ano':ano,'gradonivel':gradonivel,'seccion':seccion,'notas':notas}#para libreta de avance
        if nivel=='PRIMARIO':
            return render(request,'libretas/LibretaAvancePrimaria.html',contexto)
        else:
            return render(request,'libretas/LibretaAvanceSecundaria.html',contexto)

def ImprimirLibretasxAlumno(request):

    cursor = connection.cursor()
    if  request.method=='POST':
        #aactual= date.today().year#AÑO
        gradonivel = request.POST.get("Grado")
        seccion = request.POST.get("Seccion")
        ano = request.POST.get("AnoAcademico")#El año que manda del form
        paca=request.POST.get("Pacademico")
        paca=int(paca)
        nombrepaca=PAcademico.objects.get(id=paca)
        idMat=request.POST.get("idMat")
        nivel=str(gradonivel)[1:len(gradonivel)] #extrae solo PRIM
        grado=str(gradonivel)[0:1] #extrae solo PRI

        nivelcorto=''
        if nivel=='SEC':
            nivel='SECUNDARIO'
            nivelcorto='SEC'
        else:
            nivel='PRIMARIO'
            nivelcorto='PRIM'

        result = Curso.objects.raw('SELECT 1 as id,ccur."Curso_id" as IDCURSO,Count(*)-1 as NUM_COMPE FROM "Competencias_competenciacurso" as ccur GROUP BY ccur."Curso_id" ORDER BY ccur."Curso_id"')
        tutor=Docente.objects.filter(TutorGrado=gradonivel,TutorSeccion=seccion).last()
        matricula = Matricula.objects.filter(id=idMat,Grado=gradonivel,Seccion=seccion,AnoAcademico__Ano=ano).order_by('Alumno__ApellidoPaterno','Alumno__ApellidoMaterno','Alumno__Nombres')
        alumnos_idmat= Matricula.objects.filter(id=idMat,Grado=gradonivel,Seccion=seccion,AnoAcademico__Ano=ano).values('id','Grado').order_by('Alumno__ApellidoPaterno','Alumno__ApellidoMaterno','Alumno__Nombres')
        #Envia solamente para la apreciación del tutor
        apreciaciones=NotasComp.objects.filter(Matricula__AnoAcademico__Ano=ano,Matricula__Grado=gradonivel,Matricula__Seccion=seccion).order_by('PAcademico__id')

        if nivelcorto=='SEC':
            bim1="select n1.* from notas_primaria_ibimestre n1 WHERE n1.matricula=%s and n1.Ano=%s and n1.grado=%s and n1.seccion=%s and n1.nivelcurso=%s and n1.nombrecompetencia<>%s"
            cursor.execute(bim1,[idMat,ano,gradonivel,seccion,'SEC','CALIFICATIVO DE ÁREA'])
            notas = dictfetchall(cursor)

            bim2="select n2.* from notas_primaria_iibimestre n2 WHERE n2.matricula=%s and n2.Ano=%s and n2.grado=%s and n2.seccion=%s and n2.nivelcurso=%s and n2.nombrecompetencia<>%s"
            cursor.execute(bim2,[idMat,ano,gradonivel,seccion,'SEC','CALIFICATIVO DE ÁREA'])
            notas2 = dictfetchall(cursor)

            bim3="select n3.* from notas_primaria_iiibimestre n3 WHERE n3.matricula=%s and n3.Ano=%s and n3.grado=%s and n3.seccion=%s and n3.nivelcurso=%s and n3.nombrecompetencia<>%s"
            cursor.execute(bim3,[idMat,ano,gradonivel,seccion,'SEC','CALIFICATIVO DE ÁREA'])
            notas3 = dictfetchall(cursor)

            bim4="select n4.* from notas_primaria_ivbimestre n4 WHERE n4.matricula=%s and n4.Ano=%s and n4.grado=%s and n4.seccion=%s and n4.nivelcurso=%s and n4.nombrecompetencia<>%s"
            cursor.execute(bim4,[idMat,ano,gradonivel,seccion,'SEC','CALIFICATIVO DE ÁREA'])
            notas4 = dictfetchall(cursor)
        else:
            bim1="select n1.* from notas_primaria_ibimestre n1 WHERE n1.matricula=%s and n1.Ano=%s and n1.grado=%s and n1.seccion=%s and n1.nivelcurso=%s and n1.nombrecompetencia<>%s"
            cursor.execute(bim1,[idMat,ano,gradonivel,seccion,'PRIM','CALIFICATIVO DE ÁREA'])
            notas = dictfetchall(cursor)

            bim2="select n2.* from notas_primaria_iibimestre n2 WHERE n2.matricula=%s and n2.Ano=%s and n2.grado=%s and n2.seccion=%s and n2.nivelcurso=%s and n2.nombrecompetencia<>%s"
            cursor.execute(bim2,[idMat,ano,gradonivel,seccion,'PRIM','CALIFICATIVO DE ÁREA'])
            notas2 = dictfetchall(cursor)

            bim3="select n3.* from notas_primaria_iiibimestre n3 WHERE n3.matricula=%s and n3.Ano=%s and n3.grado=%s and n3.seccion=%s and n3.nivelcurso=%s and n3.nombrecompetencia<>%s"
            cursor.execute(bim3,[idMat,ano,gradonivel,seccion,'PRIM','CALIFICATIVO DE ÁREA'])
            notas3 = dictfetchall(cursor)

            bim4="select n4.* from notas_primaria_ivbimestre n4 WHERE n4.matricula=%s and n4.Ano=%s and n4.grado=%s and n4.seccion=%s and n4.nivelcurso=%s and n4.nombrecompetencia<>%s"
            cursor.execute(bim4,[idMat,ano,gradonivel,seccion,'PRIM','CALIFICATIVO DE ÁREA'])
            notas4 = dictfetchall(cursor)

        if paca==2:
            for n in notas:
                for n2 in notas2:
                    if n['competencia']==n2['competencia'] and  n['curso']==n2['curso'] and n['matricula']==n2['matricula']:
                        n['nota2']=n2['nota']
        if paca==4:
            for n in notas:
                for n2 in notas2:
                    if n['competencia']==n2['competencia'] and  n['curso']==n2['curso'] and n['matricula']==n2['matricula']:
                        n['nota2']=n2['nota']
            for n in notas:
                for n3 in notas3:
                    if n['competencia']==n3['competencia'] and  n['curso']==n3['curso'] and n['matricula']==n3['matricula']:
                        n['nota3']=n3['nota']
        if paca==5:
            for n in notas:
                for n2 in notas2:
                    if n['competencia']==n2['competencia'] and  n['curso']==n2['curso'] and n['matricula']==n2['matricula']:
                        n['nota2']=n2['nota']

            for n in notas:
                for n3 in notas3:
                    if n['competencia']==n3['competencia'] and  n['curso']==n3['curso'] and n['matricula']==n3['matricula']:
                        n['nota3']=n3['nota']

            for n in notas:
                for n4 in notas4:
                    if n['competencia']==n4['competencia'] and  n['curso']==n4['curso'] and n['matricula']==n4['matricula']:
                        n['nota4']=n4['nota']

        ########solo se usa para la situación final
        # SitFinalbim4="select n4.matricula,n4.nombrecurso,n4.nota,n4.tipocurso from notas_primaria_ivbimestre n4 WHERE n4.Ano=%s and n4.grado=%s and n4.seccion=%s and n4.nivelcurso=%s and n4.nombrecompetencia=%s"
        # cursor.execute(SitFinalbim4,[ano,gradonivel,seccion,nivelcorto,'CALIFICATIVO DE ÁREA'])
        # SitFinalnotas4 = dictfetchall(cursor)
        #######end para situacion final

        ########solo se usa para situacion final 2023 Modificado 19/dic/2023
        SitFinalbim4_2023="select n4.matricula,n4.nombrecurso,n4.nota,n4.tipocurso from notas_primaria_ivbimestre n4 WHERE n4.Ano=%s and n4.grado=%s and n4.seccion=%s and n4.nivelcurso=%s and n4.nombrecompetencia<>%s"
        cursor.execute(SitFinalbim4_2023,[ano,gradonivel,seccion,nivelcorto,'CALIFICATIVO DE ÁREA'])
        SitFinalnotas4_2023 = dictfetchall(cursor)
        #######end para situacion final



        if nivelcorto=='PRIM':
            SitFinal=SituacionFinalPrimaria_2023(alumnos_idmat,paca,SitFinalnotas4_2023,gradonivel)
        else:
            SitFinal=SituacionFinalSecundaria_2023(alumnos_idmat,paca,SitFinalnotas4_2023,gradonivel)
                

        contexto2={'SitFinal':SitFinal,'nombrepaca':nombrepaca,'apreciaciones':apreciaciones,'notas':notas,'result':result,'tutor':tutor,'matricula':matricula,'nivel':nivel,'paca':paca,'ano':ano,'gradonivel':gradonivel,'seccion':seccion,'grado':grado,'nivelcorto':nivelcorto}#para libreta
        if nivelcorto=='SEC':
            return render(request,'libretas/LibretaSecundaria.html',contexto2)
        else:
            return render(request,'libretas/LibretaPrimaria.html',contexto2)

def MatriculasPorAno(request,anhio):
	# aa=request.POST.get('AnoAcademico')
	mat=list(Matricula.objects.filter(AnoAcademico__Ano=anhio).values(
	'id','Alumno__DNI','Alumno__ApellidoPaterno','Alumno__ApellidoMaterno','Alumno__Nombres','Grado','Seccion'))
	return JsonResponse(mat,safe=False)

def LibretasPorAlumno(request):
	aa= list(AnoAcademico.objects.all().order_by('-id'))
	# return JsonResponse(lista,safe=False)
	contexto={'aa':aa}
	return render(request,'libretas/LibretasPorAlumno.html',contexto)

def AvancesPorAlumno(request):
	aa= list(AnoAcademico.objects.all().order_by('-id'))
	contexto={'aa':aa}
	return render(request,'libretas/AvancesPorAlumno.html',contexto)

#funcion que devuelve los nombres de las columnas
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def OpcionImprimir(request):
	return render(request,'libretas/opcion_imprimir.html')


def ImprimirAvanceNotasPrimaria(request):
    aac = AnoAcademico.objects.all().order_by('-Ano')
    pac = PAcademico.objects.all().order_by('Nombre')
    ano_actual = AnoAcademico.objects.get(Ano=datetime.now().year)
    alumnos = Matricula.objects.filter(AnoAcademico__Ano=ano_actual,Alumno__Estado='A').order_by('Alumno__ApellidoPaterno','Alumno__ApellidoMaterno','Alumno__Nombres')
    contexto = {'alumnos':alumnos,'aac':aac,'pac':pac}#para filtro

    if  request.method=='POST':
        
        #aactual= date.today().year#AÑO
        gradonivel = request.POST.get("Grado")
        seccion = request.POST.get("Seccion")
        ano = request.POST.get("Ano")#El año que manda del form
        paca=request.POST.get("Pacademico")
        filtrado=request.POST.get("habilitarfiltro")
        mespago=request.POST.get("pago")
        nombrepaca=PAcademico.objects.get(id=paca)
        nivel=str(gradonivel)[1:len(gradonivel)] #extrae solo PRIM
        grado=str(gradonivel)[0:1]
        if nivel=='PRIM':
            nivel='PRIMARIO'
        else:
            nivel='SECUNDARIO'
        #########################################################SE LE PUSO -1 PARA QUE NO SUME EL CALIFICATIVO DE ÁREA
        result = Curso.objects.raw('SELECT 1 as id,ccur."Curso_id" as IDCURSO,Count(*)-1 as NUM_COMPE FROM "Competencias_competenciacurso" as ccur GROUP BY ccur."Curso_id" ORDER BY ccur."Curso_id"')
        dnis=Pagos.objects.filter(PagoMes=mespago,PagoAno=ano).values('Dni')
        data = []
        for d in dnis:
            data.append(d["Dni"]) 
        notas=AvanceNotasComp.objects.filter(PAcademico=paca,Matricula__AnoAcademico__Ano=ano,Matricula__Grado=gradonivel,Matricula__Seccion=seccion).order_by('Curso__Orden','Competencias__Orden')
        tutor=Docente.objects.filter(TutorGrado=gradonivel,TutorSeccion=seccion).last()
        if filtrado=="SI":
            matricula = Matricula.objects.filter(Grado=gradonivel,Seccion=seccion,AnoAcademico__Ano=ano,Alumno__Estado='A',Alumno__DNI__in=data).order_by('Alumno__ApellidoPaterno','Alumno__ApellidoMaterno','Alumno__Nombres')
        else:
            matricula = Matricula.objects.filter(Grado=gradonivel,Seccion=seccion,AnoAcademico__Ano=ano,Alumno__Estado='A').order_by('Alumno__ApellidoPaterno','Alumno__ApellidoMaterno','Alumno__Nombres')
        contexto2={'nombrepaca':nombrepaca,'grado':grado,'result':result,'tutor':tutor,'matricula':matricula,'nivel':nivel,'nombrepaca':nombrepaca,'ano':ano,'gradonivel':gradonivel,'seccion':seccion,'notas':notas}#para libreta de avance
        return render(request,'libretas/LibretaAvancePrimaria.html',contexto2)
    else:
        return render(request,'otras_opciones/imprimir_avances_primaria.html',contexto)

def ImprimirAvanceNotasSecundaria(request):
    aac = AnoAcademico.objects.all().order_by('-Ano')
    pac = PAcademico.objects.all().order_by('Nombre')
    ano_actual = AnoAcademico.objects.get(Ano=datetime.now().year)
    alumnos = Matricula.objects.filter(AnoAcademico__Ano=ano_actual,Alumno__Estado='A').order_by('Alumno__ApellidoPaterno','Alumno__ApellidoMaterno','Alumno__Nombres')
    contexto = {'alumnos':alumnos,'aac':aac,'pac':pac}#para filtro
    
    if  request.method=='POST':

        gradonivel = request.POST.get("Grado")
        seccion = request.POST.get("Seccion")
        ano = request.POST.get("Ano")#El año que manda del form
        paca=request.POST.get("Pacademico")
        filtrado=request.POST.get("habilitarfiltro")
        nombrepaca=PAcademico.objects.get(id=paca)
        nivel=str(gradonivel)[1:len(gradonivel)] #extrae solo PRIM
        grado=str(gradonivel)[0:1]
        mespago=request.POST.get("pago")
        #cursos=Curso.objects.filter(Nivel=nivel)
        if nivel=='PRIM':
            nivel='PRIMARIO'
        else:
            nivel='SECUNDARIO'
        
        result = Curso.objects.raw('SELECT 1 as id,ccur."Curso_id" as IDCURSO,Count(*)-1 as NUM_COMPE FROM "Competencias_competenciacurso" as ccur GROUP BY ccur."Curso_id" ORDER BY ccur."Curso_id"')
        dnis=Pagos.objects.filter(PagoMes=mespago,PagoAno=ano).values('Dni')
        data = []
        for d in dnis:
            data.append(d["Dni"]) 
        notas=AvanceNotasComp.objects.filter(PAcademico=paca,Matricula__AnoAcademico__Ano=ano,Matricula__Grado=gradonivel,Matricula__Seccion=seccion).order_by('Curso__Orden','Competencias__Orden')
        tutor=Docente.objects.filter(TutorGrado=gradonivel,TutorSeccion=seccion).last()
        if filtrado=="SI":
            matricula = Matricula.objects.filter(Grado=gradonivel,Seccion=seccion,AnoAcademico__Ano=ano,Alumno__Estado='A',Alumno__DNI__in=data).order_by('Alumno__ApellidoPaterno','Alumno__ApellidoMaterno','Alumno__Nombres')
        else:
            matricula = Matricula.objects.filter(Grado=gradonivel,Seccion=seccion,AnoAcademico__Ano=ano,Alumno__Estado='A').order_by('Alumno__ApellidoPaterno','Alumno__ApellidoMaterno','Alumno__Nombres')

        
        contexto2={'nombrepaca':nombrepaca,'grado':grado,'result':result,'tutor':tutor,'matricula':matricula,'nivel':nivel,'ano':ano,'gradonivel':gradonivel,'seccion':seccion,'notas':notas}#para libreta de avance
        return render(request,'libretas/LibretaAvanceSecundaria.html',contexto2)
    else:
        return render(request,'otras_opciones/imprimir_avances_secundaria.html',contexto)

def ImprimirNotasPrimaria(request):

    aac = AnoAcademico.objects.all().order_by('-Ano')
    pac = PAcademico.objects.all().order_by('Nombre')
    contexto = {'aac':aac,'pac':pac}#para filtro
    cursor = connection.cursor()
    if  request.method=='POST':
        #aactual= date.today().year#AÑO
        gradonivel = request.POST.get("Grado")
        seccion = request.POST.get("Seccion")
        ano = request.POST.get("Ano")#El año que manda del form
        paca=request.POST.get("Pac")
        mes_seleccionado = int(request.POST.get("MesSeleccionado"))
        paca=int(paca)
        nombrepaca=PAcademico.objects.get(id=paca)
        nivel=str(gradonivel)[1:len(gradonivel)] #extrae solo PRIM
        grado=str(gradonivel)[0:1] #extrae solo 1 el grado
        nivelcorto=''
        if nivel=='PRIM':
            nivel='PRIMARIO'
            nivelcorto='PRIM'
        else:
            nivel='SECUNDARIO'
            nivelcorto='SEC'

        result = Curso.objects.raw('SELECT 1 as id,ccur."Curso_id" as IDCURSO,Count(*)-1 as NUM_COMPE FROM "Competencias_competenciacurso" as ccur GROUP BY ccur."Curso_id" ORDER BY ccur."Curso_id"')
        tutor=Docente.objects.filter(TutorGrado=gradonivel,TutorSeccion=seccion).last()
        dnis_filtrados = obtener_dnis_con_pagos_completos(mes_seleccionado)

        matricula = Matricula.objects.filter(
            Grado=gradonivel,
            Seccion=seccion,
            AnoAcademico__Ano=ano,
            Alumno__Estado='A',
            Alumno__DNI__in=dnis_filtrados).order_by('Alumno__ApellidoPaterno','Alumno__ApellidoMaterno','Alumno__Nombres')
        alumnos_idmat= Matricula.objects.filter(Grado=gradonivel,Seccion=seccion,AnoAcademico__Ano=ano).values('id','Grado').order_by('Alumno__ApellidoPaterno','Alumno__ApellidoMaterno','Alumno__Nombres')

        #Envia solamente para la apreciación del tutor
        apreciaciones=NotasComp.objects.filter(Matricula__AnoAcademico__Ano=ano,Matricula__Grado=gradonivel,Matricula__Seccion=seccion).order_by('PAcademico__id')

        bim1="select n1.* from notas_primaria_ibimestre n1 WHERE n1.Ano=%s and n1.grado=%s and n1.seccion=%s and n1.nivelcurso=%s and n1.nombrecompetencia<>%s"
        cursor.execute(bim1,[ano,gradonivel,seccion,'PRIM','CALIFICATIVO DE ÁREA'])
        notas = dictfetchall(cursor)

        bim2="select n2.* from notas_primaria_iibimestre n2 WHERE n2.Ano=%s and n2.grado=%s and n2.seccion=%s and n2.nivelcurso=%s and n2.nombrecompetencia<>%s"
        cursor.execute(bim2,[ano,gradonivel,seccion,'PRIM','CALIFICATIVO DE ÁREA'])
        notas2 = dictfetchall(cursor)

        bim3="select n3.* from notas_primaria_iiibimestre n3 WHERE n3.Ano=%s and n3.grado=%s and n3.seccion=%s and n3.nivelcurso=%s and n3.nombrecompetencia<>%s"
        cursor.execute(bim3,[ano,gradonivel,seccion,'PRIM','CALIFICATIVO DE ÁREA'])
        notas3 = dictfetchall(cursor)

        bim4="select n4.* from notas_primaria_ivbimestre n4 WHERE n4.Ano=%s and n4.grado=%s and n4.seccion=%s and n4.nivelcurso=%s and n4.nombrecompetencia<>%s"
        cursor.execute(bim4,[ano,gradonivel,seccion,'PRIM','CALIFICATIVO DE ÁREA'])
        notas4 = dictfetchall(cursor)


        ########solo se usa para la situación final
        SitFinalbim4="select n4.matricula,n4.nombrecurso,n4.nota,n4.tipocurso from notas_primaria_ivbimestre n4 WHERE n4.Ano=%s and n4.grado=%s and n4.seccion=%s and n4.nivelcurso=%s and n4.nombrecompetencia<>%s"
        cursor.execute(SitFinalbim4,[ano,gradonivel,seccion,'PRIM','CALIFICATIVO DE ÁREA'])
        SitFinalnotas4_2023 = dictfetchall(cursor)
        #######end para situacion final    
        

       #recorre cada vista consultada en cada bimestre y coloca en el objectlist la nota que le corresponde
        if paca==2:
            for n in notas:
                for n2 in notas2:
                    if n['competencia']==n2['competencia'] and  n['curso']==n2['curso'] and n['matricula']==n2['matricula']:
                        n['nota2']=n2['nota']
        if paca==4:
            for n in notas:
                for n2 in notas2:
                    if n['competencia']==n2['competencia'] and  n['curso']==n2['curso'] and n['matricula']==n2['matricula']:
                        n['nota2']=n2['nota']
            for n in notas:
                for n3 in notas3:
                    if n['competencia']==n3['competencia'] and  n['curso']==n3['curso'] and n['matricula']==n3['matricula']:
                        n['nota3']=n3['nota']
        if paca==5:
            for n in notas:
                for n2 in notas2:
                    if n['competencia']==n2['competencia'] and  n['curso']==n2['curso'] and n['matricula']==n2['matricula']:
                        n['nota2']=n2['nota']

            for n in notas:
                for n3 in notas3:
                    if n['competencia']==n3['competencia'] and  n['curso']==n3['curso'] and n['matricula']==n3['matricula']:
                        n['nota3']=n3['nota']

            for n in notas:
                for n4 in notas4:
                    if n['competencia']==n4['competencia'] and  n['curso']==n4['curso'] and n['matricula']==n4['matricula']:
                        n['nota4']=n4['nota']

        #SitFinal=SituacionFinalPrimaria(gradonivel,alumnos_idmat,paca,SitFinalnotas4)
        SitFinal=SituacionFinalPrimaria_2023(alumnos_idmat,paca,SitFinalnotas4_2023,gradonivel)
        
        
        contexto2={'SitFinal':SitFinal,'nombrepaca':nombrepaca,'apreciaciones':apreciaciones,'notas':notas,'result':result,'tutor':tutor,'matricula':matricula,'nivel':nivel,'paca':paca,'ano':ano,'gradonivel':gradonivel,'seccion':seccion,'grado':grado,'nivelcorto':nivelcorto}#para libreta de avance
        return render(request,'libretas/LibretaPrimaria.html',contexto2)
    else:
        return render(request,'otras_opciones/imprimir_libreta_primaria.html',contexto)

def ImprimirNotasSecundaria(request):
    
    aac = AnoAcademico.objects.all().order_by('-Ano')
    pac = PAcademico.objects.all().order_by('Nombre')
    
    contexto = {'aac':aac,'pac':pac}#para filtro
    cursor = connection.cursor()
    if  request.method=='POST':
        #aactual= date.today().year#AÑO
        gradonivel = request.POST.get("Grado")
        seccion = request.POST.get("Seccion")
        ano = request.POST.get("Ano")#El año que manda del form
        paca=request.POST.get("Pac")
        mes_seleccionado = int(request.POST.get("MesSeleccionado"))

        paca=int(paca)
        nombrepaca=PAcademico.objects.get(id=paca)
        nivel=str(gradonivel)[1:len(gradonivel)] #extrae solo PRIM
        grado=str(gradonivel)[0:1] #extrae solo PRIM
        nivelcorto=''
        if nivel=='SEC':
            nivel='SECUNDARIO'
            nivelcorto='SEC'
        else:
            nivel='PRIMARIO'
            nivelcorto='PRIM'

        result = Curso.objects.raw('SELECT 1 as id,ccur."Curso_id" as IDCURSO,Count(*)-1 as NUM_COMPE FROM "Competencias_competenciacurso" as ccur GROUP BY ccur."Curso_id" ORDER BY ccur."Curso_id"')
        
        tutor=Docente.objects.filter(TutorGrado=gradonivel,TutorSeccion=seccion).last()


        dnis_filtrados = obtener_dnis_con_pagos_completos(mes_seleccionado)

        matricula = Matricula.objects.filter(
            Grado=gradonivel,
            Seccion=seccion,
            AnoAcademico__Ano=ano,
            Alumno__Estado='A',
            Alumno__DNI__in=dnis_filtrados).order_by('Alumno__ApellidoPaterno','Alumno__ApellidoMaterno','Alumno__Nombres')
        
        alumnos_idmat= Matricula.objects.filter(Grado=gradonivel,Seccion=seccion,AnoAcademico__Ano=ano).values('id','Grado').order_by('Alumno__ApellidoPaterno','Alumno__ApellidoMaterno','Alumno__Nombres')
        #Envia solamente para la apreciación del tutor
        apreciaciones=NotasComp.objects.filter(Matricula__AnoAcademico__Ano=ano,Matricula__Grado=gradonivel,Matricula__Seccion=seccion).order_by('PAcademico__id')

        bim1="select n1.* from notas_primaria_ibimestre n1 WHERE n1.Ano=%s and n1.grado=%s and n1.seccion=%s and n1.nivelcurso=%s and n1.nombrecompetencia<>%s"
        cursor.execute(bim1,[ano,gradonivel,seccion,'SEC','CALIFICATIVO DE ÁREA'])
        notas = dictfetchall(cursor)

        bim2="select n2.* from notas_primaria_iibimestre n2 WHERE n2.Ano=%s and n2.grado=%s and n2.seccion=%s and n2.nivelcurso=%s and n2.nombrecompetencia<>%s"
        cursor.execute(bim2,[ano,gradonivel,seccion,'SEC','CALIFICATIVO DE ÁREA'])
        notas2 = dictfetchall(cursor)

        bim3="select n3.* from notas_primaria_iiibimestre n3 WHERE n3.Ano=%s and n3.grado=%s and n3.seccion=%s and n3.nivelcurso=%s and n3.nombrecompetencia<>%s"
        cursor.execute(bim3,[ano,gradonivel,seccion,'SEC','CALIFICATIVO DE ÁREA'])
        notas3 = dictfetchall(cursor)

        bim4="select n4.* from notas_primaria_ivbimestre n4 WHERE n4.Ano=%s and n4.grado=%s and n4.seccion=%s and n4.nivelcurso=%s and n4.nombrecompetencia<>%s"
        cursor.execute(bim4,[ano,gradonivel,seccion,'SEC','CALIFICATIVO DE ÁREA'])
        notas4 = dictfetchall(cursor)

        if paca==2:
            for n in notas:
                for n2 in notas2:
                    if n['competencia']==n2['competencia'] and  n['curso']==n2['curso'] and n['matricula']==n2['matricula']:
                        n['nota2']=n2['nota']
        if paca==4:
            for n in notas:
                for n2 in notas2:
                    if n['competencia']==n2['competencia'] and  n['curso']==n2['curso'] and n['matricula']==n2['matricula']:
                        n['nota2']=n2['nota']
            for n in notas:
                for n3 in notas3:
                    if n['competencia']==n3['competencia'] and  n['curso']==n3['curso'] and n['matricula']==n3['matricula']:
                        n['nota3']=n3['nota']

        if paca==5:
            for n in notas:#aqui se mete las notas del segundo,tercer y cuarto.
                for n2 in notas2:
                    if n['competencia']==n2['competencia'] and  n['curso']==n2['curso'] and n['matricula']==n2['matricula']:
                        n['nota2']=n2['nota']

            for n in notas:
                for n3 in notas3:
                    if n['competencia']==n3['competencia'] and  n['curso']==n3['curso'] and n['matricula']==n3['matricula']:
                        n['nota3']=n3['nota']

            for n in notas:
                for n4 in notas4:
                    if n['competencia']==n4['competencia'] and  n['curso']==n4['curso'] and n['matricula']==n4['matricula']:
                        n['nota4']=n4['nota']
        
        
        ########solo se usa para situacion final 2023 Modificado 19/dic/2023
        SitFinalbim4_2023="select n4.matricula,n4.nombrecurso,n4.nota,n4.tipocurso,n4.nombrecompetencia from notas_primaria_ivbimestre n4 WHERE n4.Ano=%s and n4.grado=%s and n4.seccion=%s and n4.nivelcurso=%s and n4.tipocurso=%s and n4.nombrecompetencia<>%s"
        cursor.execute(SitFinalbim4_2023,[ano,gradonivel,seccion,nivelcorto,'CURSO','CALIFICATIVO DE ÁREA'])
        SitFinalnotas4_2023 = dictfetchall(cursor)
        #######end para situacion final

        SitFinal=SituacionFinalSecundaria_2023(alumnos_idmat,paca,SitFinalnotas4_2023,gradonivel)        
       
        contexto2={'SitFinal':SitFinal,
                   'nombrepaca':nombrepaca,
                   'apreciaciones':apreciaciones,
                   'notas':notas,
                   'result':result,
                   'tutor':tutor,
                   'matricula':matricula,
                   'nivel':nivel,
                   'paca':paca,
                   'ano':ano,
                   'gradonivel':gradonivel,
                   'seccion':seccion,
                   'grado':grado,
                   'nivelcorto':nivelcorto}#para libreta
 
        
        return render(request,'libretas/LibretaSecundaria.html',contexto2)
    else:
        return render(request,'otras_opciones/imprimir_libreta_secundaria.html',contexto)

def SituacionFinalPrimaria(gradonivel,alumnos_idmat,paca,SitFinalnotas4):
    if paca==5: #el 5 es el id del bimestre
        alumnos=[]
        notamat=''
        notacom=''
        notaper=''
        notacyt=''

        for mat in alumnos_idmat:
            if gradonivel=='1PRIM':
                SituacionFinal='PROMOVIDO'
            elif gradonivel=='2PRIM' or gradonivel=='3PRIM' or gradonivel=='4PRIM' or gradonivel=='5PRIM' or gradonivel=='6PRIM':
                for notas in list(SitFinalnotas4):
                    if mat['id']==notas['matricula']:
                        if notas['nombrecurso']=='MATEMÁTICA':
                            notamat=notas['nota']
                        if notas['nombrecurso']=='COMUNICACIÓN':
                            notacom=notas['nota']
                        if notas['nombrecurso']=='PERSONAL SOCIAL':
                            notaper=notas['nota']
                        if notas['nombrecurso']=='CIENCIA Y TECNOLOGÍA':
                            notacyt=notas['nota']
                SituacionFinal=FinalPrim(gradonivel,notamat,notacom,notaper,notacyt)

            alumnos.append({"idMat":mat['id'],"sitfinal":SituacionFinal})#almacenando los datos de situacion final

        return alumnos

def SituacionFinalSecundaria(alumnos_idmat,paca,SitFinalnotas4,gradonivel):
    if paca==5: #el 5 es el id del bimestre
        alumnos=[]
        notamat=0
        notacom=0
        notaing=0
        notachi=0
        notaart=0
        notacie=0
        notadpe=0
        notaefi=0
        notarel=0
        notacta=0
        notatra=0
        if gradonivel=='5SEC':
            for mat in alumnos_idmat:
                for notas in list(SitFinalnotas4):
                    if mat['id']==notas['matricula']:
                        if notas['tipocurso']=='CURSO' and notas['nombrecompetencia']=='CALIFICATIVO DE ÁREA':
                            if notas['nombrecurso']=='MATEMÁTICA':
                                notamat=notas['promedio']
                            if notas['nombrecurso']=='COMUNICACIÓN':
                                notacom=notas['promedio']
                            if notas['nombrecurso']=='INGLÉS COMO LENGUA EXTRANJERA	':
                                notaing=notas['promedio']
                            if notas['nombrecurso']=='CHINO MANDARÍN':
                                notachi=notas['promedio']
                            if notas['nombrecurso']=='ARTE Y CULTURA':
                                notaart=notas['promedio']
                            if notas['nombrecurso']=='CIENCIAS SOCIALES':
                                notacie=notas['promedio']
                            if notas['nombrecurso']=='DESARROLLO PERSONAL, CIUDADANÍA Y CÍVICA':
                                notadpe=notas['promedio']
                            if notas['nombrecurso']=='EDUCACIÓN FÍSICA':
                                notaefi=notas['promedio']
                            if notas['nombrecurso']=='EDUCACIÓN RELIGIOSA':
                                notarel=notas['promedio']
                            if notas['nombrecurso']=='CIENCIA Y TECNOLOGÍA':
                                notacta=notas['promedio']
                            if notas['nombrecurso']=='EDUCACIÓN PARA EL TRABAJO':
                                notatra=notas['promedio']
                
                SituacionFinal=FinalSecun(notamat,notacom,notaing,notachi,notaart,notacie,notadpe,notaefi,notarel,notacta,notatra)

                alumnos.append({"idMat":mat['id'],"sitfinal":SituacionFinal})#almacenando los datos de situacion final
        else:
            for mat in alumnos_idmat:
                for notas in list(SitFinalnotas4):
                    if mat['id']==notas['matricula']:
                        if notas['tipocurso']=='CURSO':
                            if notas['nombrecurso']=='MATEMÁTICA':
                                notamat=notas['nota']
                            if notas['nombrecurso']=='COMUNICACIÓN':
                                notacom=notas['nota']
                            if notas['nombrecurso']=='INGLÉS COMO LENGUA EXTRANJERA':
                                notaing=notas['nota']
                            if notas['nombrecurso']=='CHINO MANDARÍN':
                                notachi=notas['nota']
                            if notas['nombrecurso']=='ARTE Y CULTURA':
                                notaart=notas['nota']
                            if notas['nombrecurso']=='CIENCIAS SOCIALES':
                                notacie=notas['nota']
                            if notas['nombrecurso']=='DESARROLLO PERSONAL, CIUDADANÍA Y CÍVICA':
                                notadpe=notas['nota']
                            if notas['nombrecurso']=='EDUCACIÓN FÍSICA':
                                notaefi=notas['nota']
                            if notas['nombrecurso']=='EDUCACIÓN RELIGIOSA':
                                notarel=notas['nota']
                            if notas['nombrecurso']=='CIENCIA Y TECNOLOGÍA':
                                notacta=notas['nota']
                            if notas['nombrecurso']=='EDUCACIÓN PARA EL TRABAJO':
                                notatra=notas['nota']

                SituacionFinal=FinalSecun(notamat,notacom,notaing,notachi,notaart,notacie,notadpe,notaefi,notarel,notacta,notatra)

                alumnos.append({"idMat":mat['id'],"sitfinal":SituacionFinal})#almacenando los datos de situacion final
        return alumnos


###solicitud de nuevo calculo de situación final###
def SituacionFinalSecundaria_2023(alumnos_idmat,paca,SitFinalnotas4,gradonivel):
     if paca==5: #el 5 es el id del bimestre IV
        alumnos=[]
        
        cursos=Curso.objects.filter(Tipo='CURSO', Nivel='SEC')
        
        ####--------ENCUENTRA LA SITUACIÓN FINAL--------------####
        if gradonivel=='1SEC' or gradonivel=='3SEC' or gradonivel=='4SEC': 
            for mat in alumnos_idmat:
                areas_aprobadas=0
                areas_desaprobadas=0
                areas_recuperacion=0
                
                cursos_recuperacion=[]
                cursos_repite=[]
                titulo_curso=""

                for curso in cursos:
                    A=0  #LAS A y AD
                    C=0  #LAS C
                    B=0
                    Exo=0
                    competencias=0
                    for notas in list(SitFinalnotas4):
                        if mat['id']==notas['matricula'] and notas['nombrecurso']==curso.Nombre:
                            
                            competencias+=1
                            letra=numeros_a_letras(notas['nota'])
                            ##obtiene las cantidades de compe aprobadas y desaprobadas        
                            if (letra=='A' or letra=='AD'):
                                A+=1
                            if letra=='B':
                                B+=1
                            if letra=='C': #SE ASUME  QUE ES "C"
                                C+=1
                            if letra=='EXO':
                                Exo+=1
                                
                    
                    competencias=round(competencias/2)
                    
                    if A >= competencias or B >= competencias or A>=C or B>=C and Exo==0:
                        areas_aprobadas+=1
                        
                    if C > competencias and Exo==0: 
                        areas_desaprobadas+=1
                        cursos_repite.append(curso.Nombre)
                    if C>=competencias and B<C and Exo==0:
                        areas_recuperacion+=1
                        cursos_recuperacion.append(curso.Nombre)
                        
                ##evalua la situacion final de cada alumno
                

                if areas_aprobadas==11 and len(cursos_recuperacion)==0:##A todas las áreas asociadas
                    titulo_curso="CURSOS RECUPERACIÓN"
                    alumnos.append({"idMat":mat['id'],"sitfinal":'PROMOVIDO',"titulo_curso":titulo_curso})
                elif areas_desaprobadas>=4:
                    titulo_curso="CURSOS REPITE"
                    alumnos.append({"idMat":mat['id'],"sitfinal":'REPITE',"titulo_curso":titulo_curso,"cursos_repite":cursos_repite})
                else:
                    titulo_curso="CURSOS RECUPERACIÓN"
                    alumnos.append({"idMat":mat['id'],"sitfinal":'RECUPERACIÓN',"cursos_recuperacion":cursos_recuperacion,"titulo_curso":titulo_curso})
                

        elif gradonivel=='2SEC' or gradonivel=='5SEC':
            for mat in alumnos_idmat:
                areas_aprobadas=0
                areas_desaprobadas=0
                areas_recuperacion=0
                
                cursos_recuperacion=[]
                cursos_repite=[]
                titulo_curso=""
                for curso in cursos:
                    A=0  #LAS A y AD
                    C=0  #LAS C
                    B=0
                    Exo=0
                    competencias=0
                    for notas in list(SitFinalnotas4):
                        if mat['id']==notas['matricula'] and notas['nombrecurso']==curso.Nombre:
                            competencias+=1
                            letra=numeros_a_letras(notas['nota'])
                            ##obtiene las cantidades de compe aprobadas y desaprobadas        
                            if (letra=='A' or letra=='AD'):
                                A+=1
                            if letra=='B':
                                B+=1
                            if letra=='C': #SE ASUME  QUE ES "C"
                                C+=1
                            if letra=='EXO':
                                Exo+=1
                    
                    competencias=round(competencias/2)
                    
                    if A >= B and C==0 and B<competencias and Exo==0: #esta bien para calcular el promovido
                        areas_aprobadas+=1
                        
                    if C >= B and C >= A and Exo==0: #esta bien para calcular la repitencia
                        areas_desaprobadas+=1
                        cursos_repite.append(curso.Nombre)
                    if C>0 or B>A:
                        areas_recuperacion+=1
                        cursos_recuperacion.append(curso.Nombre)

                if areas_aprobadas>=3 and areas_recuperacion==0:
                    titulo_curso="CURSOS RECUPERACIÓN"
                    alumnos.append({"idMat":mat['id'],"sitfinal":'PROMOVIDO',"titulo_curso":titulo_curso})
                elif areas_desaprobadas>=4:
                    titulo_curso="CURSOS REPITE"
                    alumnos.append({"idMat":mat['id'],"sitfinal":'REPITE',"cursos_repite":cursos_repite,"titulo_curso":titulo_curso})
                elif len(cursos_recuperacion)>0:
                    titulo_curso="CURSOS RECUPERACIÓN"
                    alumnos.append({"idMat":mat['id'],"sitfinal":'RECUPERACIÓN',"cursos_recuperacion":cursos_recuperacion,"titulo_curso":titulo_curso})
                
            

        return alumnos
            
def SituacionFinalPrimaria_2023(alumnos_idmat,paca,SitFinalnotas4,gradonivel):
    if paca==5: #el 5 es el id del bimestre
        alumnos=[]
        titulo_curso=""
        cursos=Curso.objects.filter(Tipo='CURSO',Nivel='PRIM')

        if gradonivel=='1PRIM':
            cursos_recuperacion=[]
            titulo_curso="CURSOS RECUPERACIÓN"
            for mat in alumnos_idmat:
                alumnos.append({"idMat":mat['id'],"sitfinal":'PROMOVIDO',"titulo_curso":titulo_curso})
            
        elif gradonivel=='2PRIM' or gradonivel=='4PRIM' or gradonivel=='6PRIM':
            

            cant_cursos=0
            
            if gradonivel=='2PRIM':
                cant_cursos=cursos.count()-1
            else:
                cant_cursos=cursos.count()
                
            for mat in alumnos_idmat:
                areas_aprobadas=0
                areas_desaprobadas=0
                areas_recuperacion=0
                cursos_recuperacion=[]    
                cursos_repite=[]

                for curso in cursos:
                    A=0  #LAS A y AD
                    C=0  #LAS C
                    B=0
                    Exo=0
                    #competencias=0
                    for notas in list(SitFinalnotas4):
                        
                        if mat['id']==notas['matricula'] and notas['nombrecurso']==curso.Nombre:
                            #competencias+=1
                            letra=notas['nota']
                            ##obtiene las cantidades de compe aprobadas y desaprobadas        
                            if (letra=='A' or letra=='AD'):
                                A+=1
                            if letra=='B':
                                B+=1
                            if letra=='C': #SE ASUME  QUE ES "C"
                                C+=1
                            if letra=='EXO':
                                Exo+=1

                    if A > C and A > B and Exo==0 or B>A: #esta bien para calcular el promovido
                        areas_aprobadas+=1
    
                    if C > B and C > A and Exo==0: #esta bien para calcular la repitencia
                        areas_desaprobadas+=1
                        cursos_repite.append(curso.Nombre)
                    if C>0 and Exo==0:
                        areas_recuperacion+=1
                        cursos_recuperacion.append(curso.Nombre)
                        
                if areas_desaprobadas >= 4:
                    titulo_curso="CURSOS REPITE"
                    alumnos.append({"idMat":mat['id'],"sitfinal":'REPITE','cursos_repite':cursos_repite,'titulo_curso':titulo_curso})
                else:
                    if areas_recuperacion>0:
                        titulo_curso="CURSOS RECUPERACIÓN"
                        alumnos.append({"idMat":mat['id'],"sitfinal":'RECUPERACIÓN',"cursos_recuperacion":cursos_recuperacion,'titulo_curso':titulo_curso})
                    else:
                        titulo_curso="CURSOS RECUPERACIÓN"
                        if areas_aprobadas>4:
                            alumnos.append({"idMat":mat['id'],"sitfinal":'PROMOVIDO','titulo_curso':titulo_curso})
        
        elif gradonivel=='3PRIM' or gradonivel=='5PRIM':
            cant_cursos=0
            if gradonivel=='3PRIM':
                cant_cursos=cursos.count() -1 #menos 1 el curso de chino desde 4 a 6
            else:
                cant_cursos=cursos.count()
                
            for mat in alumnos_idmat:
                areas_aprobadas=0
                areas_desaprobadas=0
                areas_recuperacion=0
                cursos_recuperacion=[]
                cursos_repite=[]
                for curso in cursos:
                    A=0  #LAS A y AD
                    C=0  #LAS C
                    B=0
                    Exo=0
                    competencias=0
                    for notas in list(SitFinalnotas4):
                        if mat['id']==notas['matricula']:
                            if notas['nombrecurso']==curso.Nombre:
                                competencias+=1
                                letra=notas['nota']
                                ##obtiene las cantidades de compe aprobadas y desaprobadas        
                                if (letra=='A' or letra=='AD'):
                                    A+=1
                                if letra=='B':
                                    B+=1
                                if letra=='C': #SE ASUME  QUE ES "C"
                                    C+=1
                                if letra=='EXO':
                                    Exo+=1
                                    
                    competencias=round(competencias/2)
                    if Exo>0:
                        cant_cursos-=1
                    
                    if B >= competencias or A >= competencias: #para Promovido
                        areas_aprobadas+=1
                    if C >= competencias: #para Repitencia
                        areas_desaprobadas+=1
                        cursos_repite.append(curso.Nombre)
                    if C > B and C > A:
                        areas_recuperacion+=1
                        cursos_recuperacion.append(curso.Nombre)
                      
                if areas_desaprobadas >=4:
                    titulo_curso="CURSOS REPITE"
                    alumnos.append({"idMat":mat['id'],"sitfinal":'REPITE',"cursos_repite":cursos_repite,"titulo_curso":titulo_curso})
                elif areas_aprobadas>=cant_cursos and areas_recuperacion==0:
                    titulo_curso="CURSOS RECUPERACIÓN"
                    alumnos.append({"idMat":mat['id'],"sitfinal":'PROMOVIDO',"titulo_curso":titulo_curso})
                elif areas_recuperacion>=0:
                    titulo_curso="CURSOS RECUPERACIÓN"
                    alumnos.append({"idMat":mat['id'],"sitfinal":'RECUPERACIÓN',"cursos_recuperacion":cursos_recuperacion, "titulo_curso":titulo_curso})
        
        return alumnos

def CaliFinalSec(paca,notas):
    if paca==5:
        for n in list(notas):
        
            nota1=n['nota']
            nota2=n['nota2']
            nota3=n['nota3']
            nota4=n['nota4']
            # print(calculo_promedio(nota1,nota2,nota3,nota4))
            if nota1 != '' and nota2 != '' and nota3 != '' and nota4 != '':
                n['promedio']=calculo_promedio(nota1,nota2,nota3,nota4)            
            else:
                n['promedio']=''
            # lista_promedios.append({'promedio':prom})
        return notas

def obtener_dnis_con_pagos_completos(hasta_mes: int):
    """
    Devuelve una lista de DNIs que tienen pagos completos desde marzo (3) hasta el mes dado.
    """
    meses_requeridos = list(range(3, hasta_mes + 1))

    dnis = Venta.objects.filter(
        NumeroMesPago__in=meses_requeridos
    ).values('Dni').annotate(
        total=Count('ConceptoNumeroMes', distinct=True)
    ).filter(total=len(meses_requeridos)).values_list('Dni', flat=True)

    return dnis