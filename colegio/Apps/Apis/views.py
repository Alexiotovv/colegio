import json
from django.http import JsonResponse
from django.shortcuts import render
from colegio.Apps.Matricula.models import Matricula
from colegio.Apps.Docente.models import Docente
from django.db.models import F,Q
from datetime import datetime
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import Venta
from datetime import datetime
from django.conf import settings

from django.views import View

def BuscarAlumno(request,dni):
    anho_actual= datetime.today().year - 1 # despues quitar el 1
    
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

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def RegistrarVenta(request):
    try:
        data = request.data
        venta = Venta.objects.create(
            id_operation=data.get('id_operation'),
            id_persona=data.get('id_persona'),
            descripcion=data.get('descripcion'),
            Dni=data.get('Dni'),
            Nombre=data.get('Nombre'),
            Apellido=data.get('Apellido'),
            NombreCompleto=data.get('NombreCompleto'),
            Nivel=data.get('Nivel'),
            Grado=data.get('Grado'),
            Seccion=data.get('Seccion'),
            Concepto=data.get('Concepto'),
            Mes=data.get('Mes'),
            TipoIngreso=data.get('TipoIngreso'),
            ConceptoNumeroMes=data.get('ConceptoNumeroMes'),
            FechaVencimiento=data.get('FechaVencimiento'),
            Monto=data.get('Monto'),
            FechaPago=data.get('FechaPago'),
            NumeroMesPago=data.get('NumeroMesPago'),
            LetraMesPago=data.get('LetraMesPago'),
            Atrasado=data.get('Atrasado'),
            DiasAtraso=data.get('DiasAtraso'),
            MesesAtraso=data.get('MesesAtraso'),
            Apoderado=data.get('Apoderado'),
            Padre=data.get('Padre'),
            Madre=data.get('Madre'),
            Direccion=data.get('Direccion')
        )

        return JsonResponse({'mensaje': 'Venta registrada correctamente', 'id': venta.id}, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


