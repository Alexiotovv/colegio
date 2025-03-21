import json
from django.http import JsonResponse
from django.shortcuts import render
from colegio.Apps.Matricula.models import Matricula
from colegio.Apps.Docente.models import Docente
from django.db.models import F,Q
from datetime import datetime


def BuscarAlumno(request,dni):
    # anho_actual= datetime.today().year
    anho_actual= '2024'
    matricula = list(Matricula.objects.filter(
        AnoAcademico__Ano=anho_actual,
        Alumno__Estado='A',
        Alumno__DNI=dni
    ).values(
        'Alumno__DNI',
        'Alumno__ApellidoPaterno',
        'Alumno__ApellidoMaterno',
        'Alumno__Nombres',
        'Grado',
        'Seccion'
    ).annotate(
        Dni=F('Alumno__DNI'),
        ApellidoPaterno=F('Alumno__ApellidoPaterno'),
        ApellidoMaterno=F('Alumno__ApellidoMaterno'),
        Nombres=F('Alumno__Nombres'),
    ).values(
        'Dni',
        'ApellidoPaterno',
        'ApellidoMaterno',
        'Nombres',
        'Grado',
        'Seccion',
    )
    )
    return JsonResponse(matricula,safe=False)



def ListarMatriculados(request,anho):
    tutores= Docente.objects.exclude(
        Q(TutorGrado='-') | Q(TutorGrado='')|Q(TutorSeccion='-') | Q(TutorSeccion='')
        ).filter(User__is_active=True
        ).values('TutorGrado', 'TutorSeccion', 'Telefono','User__first_name','User__last_name')
    print(tutores)
    matricula = list(Matricula.objects.filter(
        AnoAcademico__Ano=anho,
        Alumno__Estado='A'
    ).values(
        'Alumno__id',
        'Alumno__DNI',
        'Alumno__ApellidoPaterno',
        'Alumno__ApellidoMaterno',
        'Alumno__Nombres',
        'Grado',
        'Seccion'
    ).annotate(
        Id=F('Alumno__id'),
        Dni=F('Alumno__DNI'),
        ApellidoPaterno=F('Alumno__ApellidoPaterno'),
        ApellidoMaterno=F('Alumno__ApellidoMaterno'),
        Nombres=F('Alumno__Nombres'),
    ).values(
        'Id',
        'Dni',
        'ApellidoPaterno',
        'ApellidoMaterno',
        'Nombres',
        'Grado',
        'Seccion',
    )
    )

    # Crear un diccionario para facilitar la búsqueda de tutores por Grado y Seccion
    tutores_dict = {}
    for tutor in tutores:
        key = (tutor['TutorGrado'], tutor['TutorSeccion'])
        tutores_dict[key] = {
            'Telefono':tutor['Telefono'],
            'FirstName':tutor['User__first_name'],
            'LastName':tutor['User__last_name'],
        }
        
    # Asignar el teléfono del tutor correspondiente a cada registro de matrícula
    for alumno in matricula:
        key = (alumno['Grado'], alumno['Seccion'])
        tutor_info = tutores_dict.get(key, {})
        alumno['TelefonoTutor'] = str(tutor_info.get('Telefono', None)).replace(" ", "")
        alumno['FirstNameTutor'] = tutor_info.get('FirstName', None)
        alumno['LastNameTutor'] = tutor_info.get('LastName', None)
        #alumno['TelefonoTutor'] = tutores_dict.get(key, {})
        
    
    return JsonResponse(matricula,safe=False)

