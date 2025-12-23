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

@csrf_exempt
def procesar_archivo(request, pk):
    if request.method == 'POST':
        try:
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
            errores = 0
            
            for pdf_path in pdfs:
                try:
                    dni, situacion = archivo.buscar_dni_en_pdf(pdf_path)
                    
                    if dni:
                        # Buscar alumno por DNI
                        try:
                            alumno = Alumno.objects.get(DNI=dni)
                            
                            # Buscar matrícula activa del alumno
                            matricula = Matricula.objects.filter(
                                Alumno=alumno,
                                AnoAcademico__activo=True
                            ).first()
                            
                            if matricula:
                                # Crear o actualizar situación final
                                situacion_final, created = SituacionFinal.objects.update_or_create(
                                    matricula=matricula,
                                    defaults={
                                        'archivo_pdf': os.path.basename(pdf_path),
                                        'dni_encontrado': dni,
                                        'situacion_final': situacion or 'No encontrada'
                                    }
                                )
                                
                                resultados.append({
                                    'pdf': os.path.basename(pdf_path),
                                    'dni': dni,
                                    'alumno': alumno.NombreCompleto(),
                                    'situacion': situacion or 'No encontrada',
                                    'estado': 'PROCESADO'
                                })
                                procesados += 1
                            else:
                                resultados.append({
                                    'pdf': os.path.basename(pdf_path),
                                    'dni': dni,
                                    'alumno': 'No encontrado',
                                    'situacion': 'Matrícula no encontrada',
                                    'estado': 'ERROR'
                                })
                                errores += 1
                        except Alumno.DoesNotExist:
                            resultados.append({
                                'pdf': os.path.basename(pdf_path),
                                'dni': dni,
                                'alumno': 'No encontrado',
                                'situacion': 'Alumno no registrado',
                                'estado': 'ERROR'
                            })
                            errores += 1
                    else:
                        resultados.append({
                            'pdf': os.path.basename(pdf_path),
                            'dni': 'No encontrado',
                            'alumno': 'N/A',
                            'situacion': 'DNI no encontrado en PDF',
                            'estado': 'ERROR'
                        })
                        errores += 1
                        
                except Exception as e:
                    resultados.append({
                        'pdf': os.path.basename(pdf_path),
                        'dni': 'Error',
                        'alumno': str(e)[:50],
                        'situacion': 'Error al procesar',
                        'estado': 'ERROR'
                    })
                    errores += 1
            
            # Actualizar estadísticas del archivo
            archivo.procesado = True
            archivo.total_procesados = procesados
            archivo.total_errores = errores
            archivo.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Procesados: {procesados}, Errores: {errores}',
                'resultados': resultados
            })
            
        except ArchivoSituacionFinal.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Archivo no encontrado'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
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