from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from colegio.Apps.SituacionFinal.models import ArchivoSituacionFinal, SituacionFinal
from colegio.Apps.Alumno.models import Alumno
from colegio.Apps.Matricula.models import Matricula
from colegio.Apps.SituacionFinal.forms import ArchivoSituacionFinalForm
import os
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import get_object_or_404

from django.contrib.auth.decorators import login_required
from colegio.Apps.SituacionFinal.forms import SituacionFinalManualForm


class SubirArchivoView(CreateView):
    model = ArchivoSituacionFinal
    form_class = ArchivoSituacionFinalForm
    template_name = 'situacionfinal/subir_archivo.html'
    success_url = reverse_lazy('listar_archivos')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Archivo subido correctamente. Puede proceder a procesarlo.')
        return response

class ArchivoListView(ListView):
    model = ArchivoSituacionFinal
    template_name = 'situacionfinal/lista_archivos.html'
    context_object_name = 'archivos'
    ordering = ['-fecha_subida']


@csrf_exempt
def procesar_archivo(request, pk):
    if request.method == 'POST':
        # try:
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
            # try:
            dni, situacion, cursos = archivo.buscar_dni_en_pdf(pdf_path)
            
            if dni:
                # Buscar alumno por DNI
                # try:
                    alumno = Alumno.objects.get(DNI=dni)
                    
                    # Buscar matrícula activa del alumno
                    matricula = Matricula.objects.filter(
                        Alumno=alumno,
                        AnoAcademico__activo=True
                    ).first()
                    
                    if matricula:
                        # Crear o actualizar situación final
                        print(cursos)
                        situacion_final, created = SituacionFinal.objects.update_or_create(
                            matricula=matricula,
                            defaults={
                                'archivo_pdf': os.path.basename(pdf_path),
                                'dni_encontrado': dni,
                                'situacion_final': situacion or 'No encontrada',
                                'cursos': cursos or ''
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
                # except Alumno.DoesNotExist:
                #     resultados.append({
                #         'pdf': os.path.basename(pdf_path),
                #         'dni': dni,
                #         'alumno': 'No encontrado',
                #         'situacion': 'Alumno no registrado',
                #         'estado': 'ERROR'
                #     })
                #     errores += 1
            else:
                resultados.append({
                    'pdf': os.path.basename(pdf_path),
                    'dni': 'No encontrado',
                    'alumno': 'N/A',
                    'situacion': 'DNI no encontrado en PDF',
                    'estado': 'ERROR'
                })
                # errores += 1
                    
            # except Exception as e:
            #     resultados.append({
            #         'pdf': os.path.basename(pdf_path),
            #         'dni': 'Error',
            #         'alumno': str(e)[:50],
            #         'situacion': 'Error al procesar',
            #         'estado': 'ERROR'
            #     })
            #     errores += 1
        
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
            
        # except ArchivoSituacionFinal.DoesNotExist:
        #     return JsonResponse({
        #         'success': False,
        #         'message': 'Archivo no encontrado'
        #     })
    #     except Exception as e:
    #         return JsonResponse({
    #             'success': False,
    #             'message': f'Error: {str(e)}'
    #         })
    
    # return JsonResponse({
    #     'success': False,
    #     'message': 'Método no permitido'
    # })

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


@csrf_exempt
def eliminar_archivo(request, pk):
    if request.method == 'POST':
        try:
            # CAMBIA: ArchivoSituacionFinal en lugar de SituacionFinal
            archivo = get_object_or_404(ArchivoSituacionFinal, pk=pk)
            nombre_archivo = archivo.archivo.name
            archivo_id = archivo.id
            
            # Opcional: Eliminar el archivo físico
            if archivo.archivo and os.path.exists(archivo.archivo.path):
                try:
                    os.remove(archivo.archivo.path)
                except Exception as e:
                    print(f"Error eliminando archivo físico: {e}")
            
            # Eliminar el objeto
            archivo.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Archivo eliminado correctamente',
                'detalle': f'Se eliminó: {nombre_archivo}'
            })
            
        except ArchivoSituacionFinal.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Archivo no encontrado'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al eliminar: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    })



@login_required
def registrar_situacion_manual(request):
    """
    Vista para registrar situación final manualmente con validación anti-duplicados
    """
    alumno_info = None
    matricula_info = None
    
    if request.method == 'POST':
        form = SituacionFinalManualForm(request.POST)
        
        if form.is_valid():
            try:
                dni = form.cleaned_data['dni']
                situacion = form.cleaned_data['situacion_final']
                cursos = form.cleaned_data['cursos']
                archivo_pdf = form.cleaned_data['archivo_pdf'] or 'Registro manual'
                matricula = form.cleaned_data.get('matricula_encontrada')
                
                if not matricula:
                    messages.error(request, 'No se pudo obtener la matrícula activa')
                    return render(request, 'situacionfinal/registro_manual.html', {'form': form})
                
                # Crear la situación final (el formulario ya validó que no existe duplicado)
                situacion_final = SituacionFinal.objects.create(
                    matricula=matricula,
                    archivo_pdf=archivo_pdf,
                    dni_encontrado=dni,
                    situacion_final=situacion,
                    cursos=cursos if cursos else ''
                )
                
                alumno = matricula.Alumno
                messages.success(request, f'''
                    ✅ Situación final registrada exitosamente:
                    • Alumno: {alumno.NombreCompleto()}
                    • DNI: {dni}
                    • Grado/Sección: {matricula.Grado} - {matricula.Seccion}
                    • Situación: {situacion}
                    • Cursos: {cursos if cursos else "Ninguno"}
                ''')
                
                # Redirigir a lista de situaciones
                return redirect('listar_situaciones')
                
            except Exception as e:
                messages.error(request, f'Error al registrar: {str(e)}')
        else:
            # El formulario ya mostrará los errores de validación
            pass
    
    else:
        form = SituacionFinalManualForm()
    
    return render(request, 'situacionfinal/registro_manual.html', {
        'form': form,
        'alumno_info': alumno_info,
        'matricula_info': matricula_info
    })

@login_required
def buscar_alumno_dni(request):
    """
    Vista AJAX para buscar alumno por DNI con verificación de duplicados
    """
    if request.method == 'GET' and request.GET.get('dni'):
        dni = request.GET.get('dni')
        
        try:
            alumno = Alumno.objects.get(DNI=dni)
            matricula = Matricula.objects.filter(
                Alumno=alumno,
                AnoAcademico__activo=True
            ).first()
            
            # VERIFICAR SI YA TIENE SITUACIÓN FINAL REGISTRADA
            tiene_situacion = False
            situacion_actual = None
            
            if matricula:
                try:
                    situacion_existente = SituacionFinal.objects.get(matricula=matricula)
                    tiene_situacion = True
                    situacion_actual = situacion_existente.situacion_final
                    cursos_actual = situacion_existente.cursos
                except SituacionFinal.DoesNotExist:
                    tiene_situacion = False
            
            data = {
                'existe': True,
                'alumno': {
                    'nombre_completo': alumno.NombreCompleto(),
                    'dni': alumno.DNI,
                    'estado': alumno.get_Estado_display(),
                },
                'matricula': {
                    'existe': matricula is not None,
                    'grado': matricula.Grado if matricula else None,
                    'seccion': matricula.Seccion if matricula else None,
                    'ano_academico': matricula.AnoAcademico.Ano if matricula else None,
                    'matricula_id': matricula.id if matricula else None,
                } if matricula else None,
                'tiene_situacion': tiene_situacion,
                'situacion_actual': situacion_actual,
                'cursos_actual': cursos_actual if tiene_situacion else None
            }
            
        except Alumno.DoesNotExist:
            data = {'existe': False, 'mensaje': f'No existe alumno con DNI: {dni}'}
        
        from django.http import JsonResponse
        return JsonResponse(data)
    
    return JsonResponse({'error': 'DNI no proporcionado'})

@login_required
def actualizar_situacion_existente(request, matricula_id):
    """
    Vista para actualizar una situación final existente
    """
    try:
        matricula = Matricula.objects.get(id=matricula_id, AnoAcademico__activo=True)
        situacion_existente = SituacionFinal.objects.get(matricula=matricula)
        
        if request.method == 'POST':
            # Pasar update_mode=True para desactivar validación de duplicados
            form = SituacionFinalManualForm(request.POST, update_mode=True, matricula_id=matricula_id)
            
            if form.is_valid():
                # Solo actualizar si el DNI coincide (ya validado en el formulario)
                situacion_existente.situacion_final = form.cleaned_data['situacion_final']
                situacion_existente.cursos = form.cleaned_data['cursos']
                situacion_existente.archivo_pdf = form.cleaned_data['archivo_pdf'] or 'Registro manual actualizado'
                situacion_existente.save()
                
                messages.success(request, f'''
                    ✅ Situación actualizada para {matricula.Alumno.NombreCompleto()}
                    • Situación: {situacion_existente.situacion_final}
                    • Cursos: {situacion_existente.cursos or "Ninguno"}
                    • Fecha: {situacion_existente.fecha_procesamiento.strftime("%d/%m/%Y %H:%M")}
                ''')
                return redirect('listar_situaciones')
        else:
            # Pre-cargar formulario con datos existentes en modo actualización
            initial_data = {
                'dni': situacion_existente.dni_encontrado,
                'situacion_final': situacion_existente.situacion_final,
                'cursos': situacion_existente.cursos,
                'archivo_pdf': situacion_existente.archivo_pdf
            }
            form = SituacionFinalManualForm(initial=initial_data, update_mode=True, matricula_id=matricula_id)
        
        return render(request, 'situacionfinal/actualizar_situacion.html', {
            'form': form,
            'alumno': matricula.Alumno,
            'matricula': matricula,
            'situacion_existente': situacion_existente
        })
        
    except (Matricula.DoesNotExist, SituacionFinal.DoesNotExist) as e:
        messages.error(request, 'No se encontró la situación a actualizar')
        return redirect('registro_manual')