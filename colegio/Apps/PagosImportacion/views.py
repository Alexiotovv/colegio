from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from .forms import ExcelImportForm
from .services import ImportadorPagosExcel
from .models import ImportacionPagos, PagoAlumno
from datetime import datetime  # Agrega esto al inicio del archivo si no está

@login_required
def importar_excel(request):
    """Vista para importar el archivo Excel de pagos"""
    if request.method == 'POST':
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo_excel']
            anio = form.cleaned_data['anio']
            limpiar_antes = form.cleaned_data['limpiar_antes']
            
            # Verificar extensión
            if not archivo.name.endswith(('.xlsx', '.xls')):
                messages.error(request, 'El archivo debe ser de tipo Excel (.xlsx o .xls)')
                return redirect('PagosImportacion:importar')
            
            # Realizar importación
            importador = ImportadorPagosExcel(
                archivo=archivo,
                anio=anio,
                usuario=request.user.username
            )
            
            resultado = importador.importar(limpiar_antes=limpiar_antes)
            
            if resultado['success']:
                messages.success(
                    request, 
                    f'Importación exitosa. Se importaron {resultado["importados"]} registros de pago.'
                )
                if resultado['errores']:
                    for error in resultado['errores'][:5]:  # Mostrar solo primeros 5 errores
                        messages.warning(request, error)
                return redirect('PagosImportacion:listar_importaciones')
            else:
                messages.error(request, f'Error en la importación: {resultado["errores"][0] if resultado["errores"] else "Error desconocido"}')
                return redirect('PagosImportacion:importar')
    else:
        form = ExcelImportForm()
    
    # Obtener últimas importaciones para mostrar
    ultimas_importaciones = ImportacionPagos.objects.all()[:5]
    
    context = {
        'form': form,
        'ultimas_importaciones': ultimas_importaciones,
        'titulo': 'Importar Pagos desde Excel'
    }
    return render(request, 'pagos_importacion/importar.html', context)

@login_required
def listar_importaciones(request):
    """Lista todas las importaciones realizadas"""
    importaciones = ImportacionPagos.objects.all().order_by('-fecha_importacion')
    paginator = Paginator(importaciones, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'titulo': 'Historial de Importaciones'
    }
    return render(request, 'pagos_importacion/listar_importaciones.html', context)

@login_required
def detalle_importacion(request, importacion_id):
    """Detalle de una importación específica - Sin paginación"""
    importacion = get_object_or_404(ImportacionPagos, id=importacion_id)
    pagos = PagoAlumno.objects.filter(importacion=importacion).order_by('estudiante')
    
    # Estadísticas
    total_pagos = pagos.count()
    
    context = {
        'importacion': importacion,
        'pagos': pagos,  # Enviamos todos los registros directamente
        'total_pagos': total_pagos,
        'titulo': f'Detalle de Importación {importacion.id}'
    }
    return render(request, 'pagos_importacion/detalle_importacion.html', context)




@login_required
def limpiar_pagos(request, anio=None):
    """Vista para limpiar pagos de un año específico"""
    if request.method == 'POST':
        anio_limpiar = request.POST.get('anio', datetime.now().year)
        try:
            # Eliminar importaciones y pagos del año
            imports = ImportacionPagos.objects.filter(anio=anio_limpiar)
            count_imports = imports.count()
            imports.delete()
            messages.success(request, f'Se eliminaron {count_imports} importaciones del año {anio_limpiar}')
        except Exception as e:
            messages.error(request, f'Error al limpiar: {str(e)}')
        return redirect('PagosImportacion:importar')
    
    context = {
        'anio_actual': datetime.now().year,
        'titulo': 'Limpiar Pagos'
    }
    return render(request, 'pagos_importacion/limpiar_pagos.html', context)

@login_required
def buscar_pagos(request):
    """Vista para buscar y filtrar pagos - Vista horizontal"""
    query = request.GET.get('q', '')
    nivel = request.GET.get('nivel', '')
    grado = request.GET.get('grado', '')
    seccion = request.GET.get('seccion', '')
    mes_filtro = request.GET.get('mes_filtro', '')
    solo_deudores = request.GET.get('solo_deudores', '')
    
    pagos = PagoAlumno.objects.all().order_by('estudiante')
    
    if query:
        pagos = pagos.filter(
            Q(estudiante__icontains=query) |
            Q(dni__icontains=query) |
            Q(nombre_facturacion__icontains=query)
        )
    
    if nivel:
        pagos = pagos.filter(nivel=nivel)
    if grado:
        pagos = pagos.filter(grado=grado)
    if seccion:
        pagos = pagos.filter(seccion=seccion)
    
    # Filtrar por mes específico
    if mes_filtro:
        campo_mes = {
            '1': 'marzo', '2': 'abril', '3': 'mayo', '4': 'junio',
            '5': 'julio', '6': 'agosto', '7': 'setiembre', '8': 'octubre',
            '9': 'noviembre', '10': 'diciembre'
        }.get(mes_filtro)
        if campo_mes:
            # Excluir registros sin pago en ese mes
            pagos = pagos.exclude(**{f"{campo_mes}": '-'}).exclude(**{f"{campo_mes}": 'NO'})
    
    # Filtrar solo deudores (alumnos que tienen al menos un mes con DEBE)
    if solo_deudores:
        pagos = pagos.filter(
            Q(marzo__icontains='DEBE') |
            Q(abril__icontains='DEBE') |
            Q(mayo__icontains='DEBE') |
            Q(junio__icontains='DEBE') |
            Q(julio__icontains='DEBE') |
            Q(agosto__icontains='DEBE') |
            Q(setiembre__icontains='DEBE') |
            Q(octubre__icontains='DEBE') |
            Q(noviembre__icontains='DEBE') |
            Q(diciembre__icontains='DEBE')
        )
    
    paginator = Paginator(pagos, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    meses = ['Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 
             'Setiembre', 'Octubre', 'Noviembre', 'Diciembre']
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'nivel': nivel,
        'grado': grado,
        'seccion': seccion,
        'mes_filtro': mes_filtro,
        'solo_deudores': solo_deudores,
        'meses': meses,
        'titulo': 'Buscar Pagos'
    }
    return render(request, 'pagos_importacion/buscar_pagos.html', context)