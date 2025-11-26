import json
from django.http import JsonResponse
from django.shortcuts import render
from colegio.Apps.Matricula.models import Matricula
from colegio.Apps.Docente.models import Docente
from colegio.Apps.Pagos.models import CronogramaPagos
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
    anho_actual= datetime.today().year # despues quitar el 1
    
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
        'Seccion',
        # 'FechaMat',
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
        # 'FechaMat',
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

def ListarAlumnosMesesNoPago(request, anho):
    """
    Devuelve los alumnos con los meses que NO deben pagar según su cronograma
    Solo devuelve ID del alumno y lista de meses no pago
    """
    try:
        # Obtener matrículas del año activo con alumnos activos
        matriculas = Matricula.objects.filter(
            AnoAcademico__Ano=anho,
            Alumno__Estado='A'
        ).select_related('Alumno')
        
        resultados = []
        
        for matricula in matriculas:
            # Obtener los meses que NO debe pagar (cobrar_pension=False)
            meses_no_pago = CronogramaPagos.objects.filter(
                Matricula=matricula,
                cobrar_pension=False  # Solo los meses que NO debe pagar
            )
            
            if meses_no_pago.exists():  # Solo incluir alumnos que tienen meses sin pagar
                # Mapear números de mes a nombres
                meses_nombres = {
                    3: 'MARZO', 4: 'ABRIL', 5: 'MAYO', 6: 'JUNIO',
                    7: 'JULIO', 8: 'AGOSTO', 9: 'SETIEMBRE', 10: 'OCTUBRE',
                    11: 'NOVIEMBRE', 12: 'DICIEMBRE'
                }
                
                meses_no_pago_lista = [meses_nombres[c.NumeroMes] for c in meses_no_pago if c.NumeroMes in meses_nombres]
                
                resultados.append({
                    'Id': matricula.Alumno.id,  # Solo el ID del alumno
                    'MesesNoPago': meses_no_pago_lista  # Lista de meses que NO debe pagar
                })
        
        return JsonResponse(resultados, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
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


