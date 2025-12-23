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
import logging
import traceback
from datetime import datetime
from django.conf import settings

# Configurar logging
logger = logging.getLogger(__name__)

def write_log(message, level='info', archivo_id=None):
    """
    Escribe un mensaje en el archivo de log
    """
    try:
        log_dir = os.path.join(settings.BASE_DIR, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, 'situacion_final.log')
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        archivo_info = f"[Archivo:{archivo_id}] " if archivo_id else ""
        
        log_message = f"{timestamp} - {archivo_info}{level.upper()}: {message}\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_message)
        
        # También escribir en el logger de Django
        if level == 'error':
            logger.error(f"{archivo_info}{message}")
        elif level == 'warning':
            logger.warning(f"{archivo_info}{message}")
        else:
            logger.info(f"{archivo_info}{message}")
            
    except Exception as e:
        print(f"Error escribiendo log: {e}")

class SubirArchivoView(CreateView):
    model = ArchivoSituacionFinal
    form_class = ArchivoSituacionFinalForm
    template_name = 'situacionfinal/subir_archivo.html'
    success_url = reverse_lazy('listar_archivos')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Archivo subido correctamente. Puede proceder a procesarlo.')
        write_log(f"Archivo subido: {form.instance.archivo.name}", archivo_id=form.instance.id)
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

@csrf_exempt
def procesar_archivo(request, pk):
    """
    Vista para procesar archivos con logging detallado
    """
    write_log(f"Iniciando procesamiento de archivo ID: {pk}", archivo_id=pk)
    
    if request.method != 'POST':
        write_log(f"Método no permitido: {request.method}", 'error', pk)
        return JsonResponse({
            'success': False,
            'message': 'Método no permitido'
        })
    
    try:
        write_log("Buscando archivo en base de datos...", archivo_id=pk)
        archivo = ArchivoSituacionFinal.objects.get(pk=pk)
        write_log(f"Archivo encontrado: {archivo.archivo.name}", archivo_id=pk)
        
        if archivo.procesado:
            write_log("Archivo ya procesado anteriormente", 'warning', pk)
            return JsonResponse({
                'success': False,
                'message': 'Este archivo ya ha sido procesado'
            })
        
        write_log("Extrayendo PDFs del archivo comprimido...", archivo_id=pk)
        try:
            pdfs = archivo.extraer_y_procesar_pdfs()
            write_log(f"Se encontraron {len(pdfs)} archivos PDF", archivo_id=pk)
        except Exception as e:
            write_log(f"Error al extraer PDFs: {str(e)}", 'error', pk)
            write_log(traceback.format_exc(), 'error', pk)
            return JsonResponse({
                'success': False,
                'message': f'Error al extraer archivos: {str(e)}',
                'debug': {
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'traceback': traceback.format_exc()
                }
            })
        
        if not pdfs:
            write_log("No se encontraron archivos PDF en el archivo comprimido", 'warning', pk)
            archivo.procesado = True
            archivo.save()
            return JsonResponse({
                'success': True,
                'message': 'No se encontraron archivos PDF para procesar',
                'resultados': [],
                'estadisticas': {
                    'procesados': 0,
                    'errores': 0,
                    'total': 0
                }
            })
        
        resultados = []
        procesados = 0
        errores = 0
        
        write_log(f"Iniciando procesamiento de {len(pdfs)} PDFs...", archivo_id=pk)
        
        for i, pdf_path in enumerate(pdfs, 1):
            try:
                write_log(f"Procesando PDF {i}/{len(pdfs)}: {os.path.basename(pdf_path)}", archivo_id=pk)
                
                # Buscar DNI y situación en el PDF
                dni, situacion = archivo.buscar_dni_en_pdf(pdf_path)
                write_log(f"Resultado búsqueda PDF - DNI: {dni}, Situación: {situacion}", archivo_id=pk)
                
                if not dni:
                    write_log(f"DNI no encontrado en PDF: {os.path.basename(pdf_path)}", 'warning', pk)
                    resultados.append({
                        'pdf': os.path.basename(pdf_path),
                        'dni': 'No encontrado',
                        'alumno': 'N/A',
                        'situacion': 'DNI no encontrado en PDF',
                        'estado': 'ERROR'
                    })
                    errores += 1
                    continue
                
                write_log(f"Buscando alumno con DNI: {dni}", archivo_id=pk)
                try:
                    alumno = Alumno.objects.get(DNI=dni)
                    write_log(f"Alumno encontrado: {alumno.NombreCompleto()}", archivo_id=pk)
                except Alumno.DoesNotExist:
                    write_log(f"No se encontró alumno con DNI: {dni}", 'error', pk)
                    resultados.append({
                        'pdf': os.path.basename(pdf_path),
                        'dni': dni,
                        'alumno': 'No encontrado',
                        'situacion': 'Alumno no registrado en sistema',
                        'estado': 'ERROR'
                    })
                    errores += 1
                    continue
                
                write_log(f"Buscando matrícula activa para alumno", archivo_id=pk)
                try:
                    matricula = Matricula.objects.filter(
                        Alumno=alumno,
                        AnoAcademico__activo=True
                    ).first()
                    
                    if not matricula:
                        write_log(f"No hay matrícula activa para el alumno", 'error', pk)
                        resultados.append({
                            'pdf': os.path.basename(pdf_path),
                            'dni': dni,
                            'alumno': alumno.NombreCompleto(),
                            'situacion': 'No tiene matrícula activa',
                            'estado': 'ERROR'
                        })
                        errores += 1
                        continue
                    
                    write_log(f"Matrícula encontrada: {matricula.id}", archivo_id=pk)
                    
                    # Crear o actualizar situación final
                    write_log(f"Creando/actualizando situación final...", archivo_id=pk)
                    situacion_final, created = SituacionFinal.objects.update_or_create(
                        matricula=matricula,
                        defaults={
                            'archivo_pdf': os.path.basename(pdf_path),
                            'dni_encontrado': dni,
                            'situacion_final': situacion or 'No encontrada'
                        }
                    )
                    
                    estado = 'NUEVO' if created else 'ACTUALIZADO'
                    write_log(f"Situación final {estado.lower()}: {situacion_final}", archivo_id=pk)
                    
                    resultados.append({
                        'pdf': os.path.basename(pdf_path),
                        'dni': dni,
                        'alumno': alumno.NombreCompleto(),
                        'situacion': situacion or 'No encontrada',
                        'estado': estado
                    })
                    procesados += 1
                    
                except Exception as e:
                    write_log(f"Error con matrícula: {str(e)}", 'error', pk)
                    write_log(traceback.format_exc(), 'error', pk)
                    resultados.append({
                        'pdf': os.path.basename(pdf_path),
                        'dni': dni,
                        'alumno': alumno.NombreCompleto() if 'alumno' in locals() else 'Error',
                        'situacion': f'Error: {str(e)[:100]}',
                        'estado': 'ERROR'
                    })
                    errores += 1
                    
            except Exception as e:
                write_log(f"Error procesando PDF {pdf_path}: {str(e)}", 'error', pk)
                write_log(traceback.format_exc(), 'error', pk)
                resultados.append({
                    'pdf': os.path.basename(pdf_path),
                    'dni': 'Error',
                    'alumno': f'Error: {type(e).__name__}',
                    'situacion': str(e)[:100],
                    'estado': 'ERROR'
                })
                errores += 1
        
        # Actualizar estadísticas del archivo
        write_log(f"Procesamiento completado. Procesados: {procesados}, Errores: {errores}", archivo_id=pk)
        archivo.procesado = True
        archivo.total_procesados = procesados
        archivo.total_errores = errores
        archivo.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Procesados: {procesados}, Errores: {errores}',
            'resultados': resultados,
            'estadisticas': {
                'procesados': procesados,
                'errores': errores,
                'total': len(pdfs)
            }
        })
        
    except ArchivoSituacionFinal.DoesNotExist:
        write_log(f"Archivo con ID {pk} no encontrado", 'error', pk)
        return JsonResponse({
            'success': False,
            'message': 'Archivo no encontrado'
        })
        
    except Exception as e:
        write_log(f"Error general en procesar_archivo: {str(e)}", 'error', pk)
        write_log(traceback.format_exc(), 'error', pk)
        return JsonResponse({
            'success': False,
            'message': f'Error interno del servidor: {str(e)}',
            'debug': {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'traceback': traceback.format_exc()
            }
        })

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



# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.views.generic import ListView, CreateView
# from django.urls import reverse_lazy
# from .models import ArchivoSituacionFinal, SituacionFinal
# from colegio.Apps.Alumno.models import Alumno
# from colegio.Apps.Matricula.models import Matricula
# from .forms import ArchivoSituacionFinalForm
# import os
# from django.db import transaction
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import json
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import get_object_or_404

# class SubirArchivoView(CreateView):
#     model = ArchivoSituacionFinal
#     form_class = ArchivoSituacionFinalForm
#     template_name = 'situacionfinal/subir_archivo.html'
#     success_url = reverse_lazy('listar_archivos')
    
#     def form_valid(self, form):
#         response = super().form_valid(form)
#         messages.success(self.request, 'Archivo subido correctamente. Puede proceder a procesarlo.')
#         return response

# def lista_archivos(request):
#     """
#     Vista basada en función que reemplaza a ArchivoListView
#     Muestra todos los archivos de situaciones finales ordenados por fecha descendente
#     """
#     # Obtener todos los archivos ordenados por fecha descendente
#     archivos = ArchivoSituacionFinal.objects.all().order_by('-fecha_subida')

#     # Crear el contexto para la plantilla
#     context = {
#         'archivos': archivos,
#         'title': 'Archivos de Situaciones Finales'
#     }
    
#     # Renderizar la plantilla con el contexto
#     return render(request, 'situacionfinal/lista_archivos.html', context)

# @csrf_exempt
# def procesar_archivo(request, pk):
#     if request.method == 'POST':
#         # try:
#         archivo = ArchivoSituacionFinal.objects.get(pk=pk)
        
#         if archivo.procesado:
#             return JsonResponse({
#                 'success': False,
#                 'message': 'Este archivo ya ha sido procesado'
#             })
        
#         # Extraer PDFs
#         pdfs = archivo.extraer_y_procesar_pdfs()
        
#         resultados = []
#         procesados = 0
#         errores = 0
        
#         for pdf_path in pdfs:
#             # try:
#                 dni, situacion = archivo.buscar_dni_en_pdf(pdf_path)
                
#                 if dni:
#                     # Buscar alumno por DNI
#                     # try:
#                         alumno = Alumno.objects.get(DNI=dni)
                        
#                         # Buscar matrícula activa del alumno
#                         matricula = Matricula.objects.filter(
#                             Alumno=alumno,
#                             AnoAcademico__activo=True
#                         ).first()
                        
#                         if matricula:
#                             # Crear o actualizar situación final
#                             situacion_final, created = SituacionFinal.objects.update_or_create(
#                                 matricula=matricula,
#                                 defaults={
#                                     'archivo_pdf': os.path.basename(pdf_path),
#                                     'dni_encontrado': dni,
#                                     'situacion_final': situacion or 'No encontrada'
#                                 }
#                             )
                            
#                             resultados.append({
#                                 'pdf': os.path.basename(pdf_path),
#                                 'dni': dni,
#                                 'alumno': alumno.NombreCompleto(),
#                                 'situacion': situacion or 'No encontrada',
#                                 'estado': 'PROCESADO'
#                             })
#                             procesados += 1
#                         else:
#                             resultados.append({
#                                 'pdf': os.path.basename(pdf_path),
#                                 'dni': dni,
#                                 'alumno': 'No encontrado',
#                                 'situacion': 'Matrícula no encontrada',
#                                 'estado': 'ERROR'
#                             })
#                             errores += 1
#                     # except Alumno.DoesNotExist:
#                     #     resultados.append({
#                     #         'pdf': os.path.basename(pdf_path),
#                     #         'dni': dni,
#                     #         'alumno': 'No encontrado',
#                     #         'situacion': 'Alumno no registrado',
#                     #         'estado': 'ERROR'
#                     #     })
#                     #     errores += 1
#                 else:
#                     resultados.append({
#                         'pdf': os.path.basename(pdf_path),
#                         'dni': 'No encontrado',
#                         'alumno': 'N/A',
#                         'situacion': 'DNI no encontrado en PDF',
#                         'estado': 'ERROR'
#                     })
#                     errores += 1
                    
#             # except Exception as e:
#             #     resultados.append({
#             #         'pdf': os.path.basename(pdf_path),
#             #         'dni': 'Error',
#             #         'alumno': str(e)[:50],
#             #         'situacion': 'Error al procesar',
#             #         'estado': 'ERROR'
#             #     })
#             #     errores += 1
        
#         # Actualizar estadísticas del archivo
#         archivo.procesado = True
#         archivo.total_procesados = procesados
#         archivo.total_errores = errores
#         archivo.save()
        
#         return JsonResponse({
#             'success': True,
#             'message': f'Procesados: {procesados}, Errores: {errores}',
#             'resultados': resultados
#         })
        
#         # except ArchivoSituacionFinal.DoesNotExist:
#         #     return JsonResponse({
#         #             'success': False,
#         #             'message': 'Archivo no encontrado'
#         #         })
#         # except Exception as e:
#         #     return JsonResponse({
#         #         'success': False,
#         #         'message': f'Error: {str(e)}'
#         #     })
    
#     return JsonResponse({
#         'success': False,
#         'message': 'Método no permitido'
#     })

# class SituacionFinalListView(ListView):
#     model = SituacionFinal
#     template_name = 'situacionfinal/lista_situaciones.html'
#     context_object_name = 'situaciones'
    
#     def get_queryset(self):
#         return SituacionFinal.objects.select_related(
#             'matricula',
#             'matricula__Alumno',
#             'matricula__AnoAcademico'
#         ).order_by('matricula__Alumno__ApellidoPaterno')


# @login_required
# @csrf_exempt
# def eliminar_archivo(request, pk):
#     """
#     Elimina un ArchivoSituacionFinal y su archivo físico asociado
#     """
#     if request.method == 'POST':
#         try:
#             archivo = get_object_or_404(ArchivoSituacionFinal, pk=pk)
#             nombre_archivo = archivo.archivo.name
#             archivo_id = archivo.id
            
#             # Opcional: Eliminar el archivo físico del sistema de archivos
#             if archivo.archivo and os.path.exists(archivo.archivo.path):
#                 try:
#                     os.remove(archivo.archivo.path)
#                 except Exception as e:
#                     print(f"Error eliminando archivo físico: {e}")
            
#             # Eliminar el objeto de la base de datos
#             # Esto NO eliminará las SituacionFinal asociadas automáticamente
#             # a menos que tengas configurado on_delete=CASCADE en el modelo SituacionFinal
#             archivo.delete()
            
#             return JsonResponse({
#                 'success': True,
#                 'message': 'Archivo eliminado correctamente',
#                 'detalle': f'Se eliminó el archivo: {nombre_archivo} (ID: {archivo_id})'
#             })
            
#         except ArchivoSituacionFinal.DoesNotExist:
#             return JsonResponse({
#                 'success': False,
#                 'message': 'Archivo no encontrado'
#             })
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'message': f'Error al eliminar el archivo: {str(e)}'
#             })
    
#     return JsonResponse({
#         'success': False,
#         'message': 'Método no permitido'
#     })