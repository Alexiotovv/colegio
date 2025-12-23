from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from .models import ArchivoSituacionFinal, SituacionFinal
from colegio.Apps.Alumno.models import Alumno
from colegio.Apps.Matricula.models import Matricula
from .forms import ArchivoSituacionFinalForm
import os
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils import timezone
import logging
import traceback


class SubirArchivoView(CreateView):
    model = ArchivoSituacionFinal
    form_class = ArchivoSituacionFinalForm
    template_name = 'situacionfinal/subir_archivo.html'
    success_url = reverse_lazy('listar_archivos')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Archivo subido correctamente. Puede proceder a procesarlo.')
        return response

def lista_archivos(request):
    """
    Vista basada en función que reemplaza a ArchivoListView
    Muestra todos los archivos de situaciones finales ordenados por fecha descendente
    """
    # Obtener todos los archivos ordenados por fecha descendente
    archivos = ArchivoSituacionFinal.objects.all().order_by('-fecha_subida')

    # Crear el contexto para la plantilla
    context = {
        'archivos': archivos,
        'title': 'Archivos de Situaciones Finales'
    }
    
    # Renderizar la plantilla con el contexto
    return render(request, 'situacionfinal/lista_archivos.html', context)


logger = logging.getLogger(__name__)

@csrf_exempt
def procesar_archivo(request, pk):
    if request.method == 'POST':
        # Sin try-except general para ver errores
        archivo = ArchivoSituacionFinal.objects.get(pk=pk)
        
        if archivo.procesado:
            return JsonResponse({
                'success': False,
                'message': 'Este archivo ya ha sido procesado'
            })
        
        # Extraer PDFs
        pdfs = archivo.extraer_y_procesar_pdfs()
        
        resultados = []
        procesados = 0
        actualizados = 0
        nuevos = 0
        errores = 0
        
        for pdf_path in pdfs:
            # Verificar que el archivo existe
            if not os.path.exists(pdf_path):
                resultados.append({
                    'pdf': os.path.basename(pdf_path),
                    'dni': 'Error',
                    'alumno': 'Archivo no encontrado',
                    'situacion': 'PDF no existe en disco',
                    'estado': 'ERROR',
                    'matricula_id': None
                })
                errores += 1
                continue
            
            dni, situacion = archivo.buscar_dni_en_pdf(pdf_path)
            
            if dni:
                # Buscar alumno por DNI
                alumno = Alumno.objects.get(DNI=dni)
                
                # Buscar matrícula del alumno en año activo
                matricula = Matricula.objects.filter(
                    Alumno=alumno,
                    AnoAcademico__activo=True
                ).first()
                
                if matricula:
                    # Usar update_or_create con matricula como criterio
                    situacion_final_obj, created = SituacionFinal.objects.update_or_create(
                        matricula=matricula,
                        defaults={
                            'archivo_pdf': os.path.basename(pdf_path),
                            'dni_encontrado': dni,
                            'situacion_final': situacion or 'No encontrada',
                            'fecha_procesamiento': timezone.now()
                        }
                    )
                    
                    if created:
                        estado = 'NUEVO'
                        nuevos += 1
                    else:
                        estado = 'ACTUALIZADO'
                        actualizados += 1
                    
                    resultados.append({
                        'pdf': os.path.basename(pdf_path),
                        'dni': dni,
                        'alumno': alumno.NombreCompleto(),
                        'situacion': situacion or 'No encontrada',
                        'estado': estado,
                        'matricula_id': matricula.id
                    })
                    procesados += 1
                else:
                    resultados.append({
                        'pdf': os.path.basename(pdf_path),
                        'dni': dni,
                        'alumno': alumno.NombreCompleto(),
                        'situacion': 'Matrícula no encontrada para año activo',
                        'estado': 'ERROR',
                        'matricula_id': None
                    })
                    errores += 1
            else:
                resultados.append({
                    'pdf': os.path.basename(pdf_path),
                    'dni': 'No encontrado',
                    'alumno': 'N/A',
                    'situacion': 'DNI no encontrado en PDF',
                    'estado': 'ERROR',
                    'matricula_id': None
                })
                errores += 1
        
        # Actualizar estadísticas del archivo
        archivo.procesado = True
        archivo.total_procesados = procesados
        archivo.total_errores = errores
        archivo.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Procesados: {procesados} (Nuevos: {nuevos}, Actualizados: {actualizados}), Errores: {errores}',
            'resultados': resultados,
            'estadisticas': {
                'nuevos': nuevos,
                'actualizados': actualizados,
                'errores': errores,
                'total': procesados
            }
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    })
# def procesar_archivo(request, pk):
#     if request.method == 'POST':
#         try:
#             logger.info(f"Iniciando procesamiento de archivo ID: {pk}")
            
#             archivo = ArchivoSituacionFinal.objects.get(pk=pk)
#             logger.info(f"Archivo encontrado: {archivo.archivo.name}")
            
#             if archivo.procesado:
#                 logger.warning(f"Archivo {pk} ya procesado")
#                 return JsonResponse({
#                     'success': False,
#                     'message': 'Este archivo ya ha sido procesado'
#                 })
            
#             # Extraer PDFs
#             logger.info("Extrayendo PDFs del archivo comprimido...")
#             pdfs = archivo.extraer_y_procesar_pdfs()
#             logger.info(f"Total PDFs encontrados: {len(pdfs)}")
            
#             resultados = []
#             procesados = 0
#             actualizados = 0
#             nuevos = 0
#             errores = 0
            
#             for i, pdf_path in enumerate(pdfs):
#                 try:
#                     logger.info(f"Procesando PDF {i+1}/{len(pdfs)}: {os.path.basename(pdf_path)}")
                    
#                     # Verificar que el archivo existe
#                     if not os.path.exists(pdf_path):
#                         logger.error(f"PDF no existe: {pdf_path}")
#                         resultados.append({
#                             'pdf': os.path.basename(pdf_path),
#                             'dni': 'Error',
#                             'alumno': 'Archivo no encontrado',
#                             'situacion': 'PDF no existe en disco',
#                             'estado': 'ERROR',
#                             'matricula_id': None
#                         })
#                         errores += 1
#                         continue
                    
#                     # Verificar permisos del archivo
#                     try:
#                         with open(pdf_path, 'rb') as f:
#                             f.read(10)  # Intentar leer
#                     except PermissionError as pe:
#                         logger.error(f"Sin permisos para leer PDF: {pdf_path} - {pe}")
#                         resultados.append({
#                             'pdf': os.path.basename(pdf_path),
#                             'dni': 'Error',
#                             'alumno': 'Permiso denegado',
#                             'situacion': 'No se puede leer el PDF',
#                             'estado': 'ERROR',
#                             'matricula_id': None
#                         })
#                         errores += 1
#                         continue
                    
#                     dni, situacion = archivo.buscar_dni_en_pdf(pdf_path)
#                     logger.info(f"Resultado búsqueda - DNI: {dni}, Situación: {situacion}")
                    
#                     if dni:
#                         # Buscar alumno por DNI
#                         try:
#                             alumno = Alumno.objects.get(DNI=dni)
#                             logger.info(f"Alumno encontrado: {alumno.NombreCompleto()}")
                            
#                             # Buscar matrícula del alumno en año activo
#                             matricula = Matricula.objects.filter(
#                                 Alumno=alumno,
#                                 AnoAcademico__activo=True
#                             ).first()
                            
#                             if matricula:
#                                 logger.info(f"Matrícula encontrada: ID {matricula.id}")
                                
#                                 try:
#                                     # Usar update_or_create con matricula como criterio
#                                     situacion_final_obj, created = SituacionFinal.objects.update_or_create(
#                                         matricula=matricula,
#                                         defaults={
#                                             'archivo_pdf': os.path.basename(pdf_path),
#                                             'dni_encontrado': dni,
#                                             'situacion_final': situacion or 'No encontrada',
#                                             'fecha_procesamiento': timezone.now()
#                                         }
#                                     )
                                    
#                                     if created:
#                                         estado = 'NUEVO'
#                                         nuevos += 1
#                                         logger.info(f"NUEVO - Matrícula ID {matricula.id}, Alumno: {alumno.NombreCompleto()}")
#                                     else:
#                                         estado = 'ACTUALIZADO'
#                                         actualizados += 1
#                                         logger.info(f"ACTUALIZADO - Matrícula ID {matricula.id}, Alumno: {alumno.NombreCompleto()}")
                                    
#                                     resultados.append({
#                                         'pdf': os.path.basename(pdf_path),
#                                         'dni': dni,
#                                         'alumno': alumno.NombreCompleto(),
#                                         'situacion': situacion or 'No encontrada',
#                                         'estado': estado,
#                                         'matricula_id': matricula.id
#                                     })
#                                     procesados += 1
                                    
#                                 except Exception as db_error:
#                                     logger.error(f"Error en base de datos para matrícula {matricula.id}: {db_error}")
#                                     logger.error(traceback.format_exc())
#                                     resultados.append({
#                                         'pdf': os.path.basename(pdf_path),
#                                         'dni': dni,
#                                         'alumno': alumno.NombreCompleto(),
#                                         'situacion': f'Error BD: {str(db_error)[:50]}',
#                                         'estado': 'ERROR',
#                                         'matricula_id': matricula.id
#                                     })
#                                     errores += 1
#                             else:
#                                 logger.warning(f"No hay matrícula activa para alumno: {alumno.NombreCompleto()}")
#                                 resultados.append({
#                                     'pdf': os.path.basename(pdf_path),
#                                     'dni': dni,
#                                     'alumno': alumno.NombreCompleto(),
#                                     'situacion': 'Matrícula no encontrada para año activo',
#                                     'estado': 'ERROR',
#                                     'matricula_id': None
#                                 })
#                                 errores += 1
#                         except Alumno.DoesNotExist:
#                             logger.warning(f"Alumno no encontrado con DNI: {dni}")
#                             resultados.append({
#                                 'pdf': os.path.basename(pdf_path),
#                                 'dni': dni,
#                                 'alumno': 'No encontrado',
#                                 'situacion': 'Alumno no registrado',
#                                 'estado': 'ERROR',
#                                 'matricula_id': None
#                             })
#                             errores += 1
#                     else:
#                         logger.warning(f"DNI no encontrado en PDF: {os.path.basename(pdf_path)}")
#                         resultados.append({
#                             'pdf': os.path.basename(pdf_path),
#                             'dni': 'No encontrado',
#                             'alumno': 'N/A',
#                             'situacion': 'DNI no encontrado en PDF',
#                             'estado': 'ERROR',
#                             'matricula_id': None
#                         })
#                         errores += 1
                        
#                 except Exception as e:
#                     error_msg = f"Error procesando PDF {os.path.basename(pdf_path)}: {type(e).__name__}: {str(e)}"
#                     logger.error(error_msg)
#                     logger.error(traceback.format_exc())
                    
#                     resultados.append({
#                         'pdf': os.path.basename(pdf_path),
#                         'dni': 'Error',
#                         'alumno': f"Excepción: {type(e).__name__}",
#                         'situacion': f"Error: {str(e)[:100]}",
#                         'estado': 'ERROR',
#                         'matricula_id': None
#                     })
#                     errores += 1
            
#             # Actualizar estadísticas del archivo
#             archivo.procesado = True
#             archivo.total_procesados = procesados
#             archivo.total_errores = errores
#             archivo.save()
            
#             logger.info(f"Procesamiento completado. Nuevos: {nuevos}, Actualizados: {actualizados}, Errores: {errores}")
            
#             return JsonResponse({
#                 'success': True,
#                 'message': f'Procesados: {procesados} (Nuevos: {nuevos}, Actualizados: {actualizados}), Errores: {errores}',
#                 'resultados': resultados,
#                 'estadisticas': {
#                     'nuevos': nuevos,
#                     'actualizados': actualizados,
#                     'errores': errores,
#                     'total': procesados
#                 }
#             })
            
#         except ArchivoSituacionFinal.DoesNotExist:
#             logger.error(f"Archivo con ID {pk} no encontrado")
#             return JsonResponse({
#                 'success': False,
#                 'message': 'Archivo no encontrado'
#             })
#         except Exception as e:
#             logger.error(f"Error general en procesar_archivo: {type(e).__name__}: {str(e)}")
#             logger.error(traceback.format_exc())
#             return JsonResponse({
#                 'success': False,
#                 'message': f'Error general: {str(e)}'
#             })
    
#     logger.warning("Método no permitido en procesar_archivo")
#     return JsonResponse({
#         'success': False,
#         'message': 'Método no permitido'
#     })

class SituacionFinalListView(ListView):
    model = SituacionFinal
    template_name = 'situacionfinal/lista_situaciones.html'
    context_object_name = 'situaciones'
    
    def get_queryset(self):
        return SituacionFinal.objects.select_related(
            'matricula',
            'matricula__Alumno',
            'matricula__AnoAcademico'
        ).order_by('matricula__Alumno__ApellidoPaterno')


@login_required
@csrf_exempt
def eliminar_archivo(request, pk):
    """
    Elimina un ArchivoSituacionFinal y su archivo físico asociado
    """
    if request.method == 'POST':
        try:
            archivo = get_object_or_404(ArchivoSituacionFinal, pk=pk)
            nombre_archivo = archivo.archivo.name
            archivo_id = archivo.id
            
            # Opcional: Eliminar el archivo físico del sistema de archivos
            if archivo.archivo and os.path.exists(archivo.archivo.path):
                try:
                    os.remove(archivo.archivo.path)
                except Exception as e:
                    print(f"Error eliminando archivo físico: {e}")
            
            # Eliminar el objeto de la base de datos
            # Esto NO eliminará las SituacionFinal asociadas automáticamente
            # a menos que tengas configurado on_delete=CASCADE en el modelo SituacionFinal
            archivo.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Archivo eliminado correctamente',
                'detalle': f'Se eliminó el archivo: {nombre_archivo} (ID: {archivo_id})'
            })
            
        except ArchivoSituacionFinal.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Archivo no encontrado'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al eliminar el archivo: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    })