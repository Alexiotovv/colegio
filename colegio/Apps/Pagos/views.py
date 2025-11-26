from django.shortcuts import render, redirect, get_object_or_404
from colegio.Apps.Pagos.models import Pagos
from django.http import JsonResponse
from colegio.Apps.Apis.models import Venta
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.generic import TemplateView
from colegio.Apps.Alumno.models import Alumno
from colegio.Apps.Matricula.models import Matricula
from colegio.Apps.Pagos.models import CronogramaPagos, MontoPension
from colegio.Apps.AnoAcademico.models import AnoAcademico
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages

def RegistrarPago(request):
    
    existe=Pagos.objects.filter(Dni=request.POST.get("Dni"),PagoMes=request.POST.get("pago_mes"),PagoAno=request.POST.get("pago_ano")).exists()
    
    if existe:
        data={'mensaje':existe}
    else:
        obj=Pagos()
        obj.Dni=request.POST.get("Dni")
        obj.PagoMes=request.POST.get("pago_mes")
        obj.PagoAno=request.POST.get("pago_ano")
        obj.save()
        data={'mensaje':existe}
    return JsonResponse(data)
    
def ListarPagos(request):
    query = request.GET.get('q', '')
    
    ventas = Venta.objects.order_by(
    '-FechaPago','id_operation', 'id_persona', 'descripcion', 'Dni', 'Nombre', 'Apellido', 'NombreCompleto',
    'Nivel', 'Grado', 'Seccion', 'Concepto', 'Mes', 'TipoIngreso', 'ConceptoNumeroMes',
    'FechaVencimiento', 'Monto', 'FechaPago', 'NumeroMesPago', 'LetraMesPago', 'Atrasado',
    'DiasAtraso', 'MesesAtraso', 'Apoderado', 'Padre', 'Madre', 'Direccion'
    ).distinct(
        'id_operation', 'id_persona', 'descripcion', 'Dni', 'Nombre', 'Apellido', 'NombreCompleto',
        'Nivel', 'Grado', 'Seccion', 'Concepto', 'Mes', 'TipoIngreso', 'ConceptoNumeroMes',
        'FechaVencimiento', 'Monto', 'FechaPago', 'NumeroMesPago', 'LetraMesPago', 'Atrasado',
        'DiasAtraso', 'MesesAtraso', 'Apoderado', 'Padre', 'Madre', 'Direccion'
    )


    if query:
        ventas = ventas.filter(
            Q(NombreCompleto__icontains=query) |
            Q(Dni__icontains=query)
        )

    paginator = Paginator(ventas, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, "pagos/pagos.html", context)

@login_required
def GestionarCronogramaView(request):
    """Vista para gestionar el cronograma de pagos por alumno"""
    alumnos = Alumno.objects.filter(Estado='A').select_related()
    
    # Obtener el año académico activo y el monto de pensión activo
    try:
        ano_activo = AnoAcademico.objects.filter(activo=True).first()
        monto_pension = None
        if ano_activo:
            monto_pension = MontoPension.get_monto_activo(ano_activo)
    except:
        ano_activo = None
        monto_pension = None
    
    context = {
        'alumnos': alumnos,
        'ano_activo': ano_activo,
        'monto_pension_default': monto_pension.Monto if monto_pension else 150.00,  # Valor por defecto si no existe
    }
    return render(request, 'pagos/gestionar_cronograma.html', context)

@login_required
def RegistrarCronograma(request):
    """Vista para guardar/actualizar el cronograma de pagos del alumno - Versión robusta"""
    if request.method == 'POST':
        try:
            # Debug: imprimir todos los datos recibidos
            print("=== DATOS RECIBIDOS ===")
            for key, value in request.POST.items():
                print(f"{key}: {value}")
            print("=======================")
            
            alumno_id = request.POST.get('alumno_id')
            matricula_id = request.POST.get('matricula_id')
            
            if not alumno_id:
                return JsonResponse({'success': False, 'error': 'Falta alumno_id'})
            if not matricula_id:
                return JsonResponse({'success': False, 'error': 'Falta matricula_id'})
            
            # Obtener la matrícula
            try:
                matricula = Matricula.objects.get(id=matricula_id, Alumno_id=alumno_id)
                print(f"Matrícula encontrada: {matricula}")
            except Matricula.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Matrícula no encontrada'})
            
            meses_guardados = 0
            errores = []
            
            # Primero, obtener todos los meses posibles (3-12)
            todos_los_meses = list(range(3, 13))
            
            # Crear un conjunto de meses que tienen checkbox marcado
            meses_con_checkbox = set()
            for key, value in request.POST.items():
                if key.startswith('debe_pagar_'):
                    mes_numero = int(key.replace('debe_pagar_', ''))
                    meses_con_checkbox.add(mes_numero)
            
            # Procesar cada mes posible
            for mes_numero in todos_los_meses:
                try:
                    # Determinar si debe pagar basado en si el checkbox está presente
                    debe_pagar = mes_numero in meses_con_checkbox
                    
                    # Obtener los otros campos para este mes
                    monto_key = f'monto_{mes_numero}'
                    observacion_key = f'observacion_{mes_numero}'
                    
                    monto_str = request.POST.get(monto_key, '0')
                    observacion = request.POST.get(observacion_key, '')
                    
                    try:
                        monto = float(monto_str) if monto_str else 0.0
                    except ValueError:
                        monto = 0.0
                    
                    print(f"Procesando mes {mes_numero}: pagar={debe_pagar}, monto={monto}")
                    
                    # Verificar si ya existe un registro para este mes
                    cronograma_existente = CronogramaPagos.objects.filter(
                        Matricula=matricula,
                        NumeroMes=mes_numero
                    ).first()
                    
                    if cronograma_existente:
                        # Si ya existe y está pagado, no actualizar
                        if cronograma_existente.pagado:
                            print(f"Mes {mes_numero} ya pagado, no se actualiza")
                            continue
                    
                    # Usar update_or_create para mayor robustez
                    cronograma_pago, created = CronogramaPagos.objects.update_or_create(
                        Matricula=matricula,
                        NumeroMes=mes_numero,
                        defaults={
                            'cobrar_pension': debe_pagar,
                            'monto': monto,
                            'observaciones': observacion,
                        }
                    )
                    
                    meses_guardados += 1
                    print(f"✓ Mes {mes_numero} {'creado' if created else 'actualizado'} - Pagar: {debe_pagar}")
                    
                except Exception as e:
                    error_msg = f"Error en mes {mes_numero}: {str(e)}"
                    errores.append(error_msg)
                    print(f"✗ {error_msg}")
            
            mensaje = f'Cronograma guardado exitosamente para {meses_guardados} meses'
            if errores:
                mensaje += f'. Errores: {", ".join(errores)}'
            
            return JsonResponse({
                'success': True, 
                'message': mensaje,
                'alumno': matricula.Alumno.NombreCompleto(),
                'meses_guardados': meses_guardados,
                'errores': errores
            })
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"ERROR GENERAL: {str(e)}")
            print(f"TRACEBACK: {error_detail}")
            return JsonResponse({'success': False, 'error': str(e), 'traceback': error_detail})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
def GetCronogramaAlumno(request, matricula_id):
    """Obtener el cronograma existente de un alumno (para edición)"""
    try:
        matricula = get_object_or_404(Matricula, id=matricula_id)
        cronogramas = CronogramaPagos.objects.filter(Matricula=matricula)
        
        data = {
            'success': True,
            'alumno': {
                'id': matricula.Alumno.id,
                'nombre': matricula.Alumno.NombreCompleto(),
                'dni': matricula.Alumno.DNI,
            },
            'matricula': {
                'id': matricula.id,
                'grado': matricula.Grado,
                'seccion': matricula.Seccion,
            },
            'cronograma': {},
            'existe_cronograma': cronogramas.exists()  # Nueva propiedad para saber si existe
        }
        
        for crono in cronogramas:
            data['cronograma'][crono.NumeroMes] = {
                'cobrar_pension': crono.cobrar_pension,
                'monto': float(crono.monto),
                'observaciones': crono.observaciones,
                'pagado': crono.pagado
            }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def BuscarMatriculasAlumno(request, alumno_id):
    """Buscar matrículas activas de un alumno"""
    try:
        # Obtener año académico activo
        ano_activo = AnoAcademico.objects.filter(activo=True).first()
        
        if not ano_activo:
            return JsonResponse({'success': False, 'error': 'No hay año académico activo'})
        
        # Buscar matrículas del alumno en el año activo
        matriculas = Matricula.objects.filter(
            Alumno_id=alumno_id, 
            AnoAcademico=ano_activo
        ).values('id', 'Grado', 'Seccion')
        
        matriculas_data = []
        for matricula in matriculas:
            matriculas_data.append({
                'id': matricula['id'],
                'grado': matricula['Grado'],
                'seccion': matricula['Seccion'],
                'ano_academico': ano_activo.Ano
            })
        
        return JsonResponse({
            'success': True,
            'matriculas': matriculas_data
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def GenerarCronogramasMasivos(request):
    """Generar cronogramas para todos los alumnos que no tengan en el año activo"""
    if request.method == 'POST':
        try:
            # Obtener año académico activo
            ano_activo = AnoAcademico.objects.filter(activo=True).first()
            if not ano_activo:
                return JsonResponse({
                    'success': False, 
                    'error': 'No hay año académico activo configurado'
                })
            
            # Obtener monto de pensión activo
            monto_pension = MontoPension.get_monto_activo(ano_activo)
            if not monto_pension:
                return JsonResponse({
                    'success': False, 
                    'error': 'No hay monto de pensión configurado para el año activo'
                })
            
            monto_valor = monto_pension.Monto
            
            # Obtener todas las matrículas activas del año académico activo
            matriculas_activas = Matricula.objects.filter(
                AnoAcademico=ano_activo,
                Alumno__Estado='A'  # Asumiendo que 'A' es activo
            ).select_related('Alumno')
            
            total_matriculas = matriculas_activas.count()
            cronogramas_generados = 0
            cronogramas_existentes = 0
            errores = []
            
            # Meses a generar (de Marzo a Diciembre)
            MESES_A_GENERAR = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
            
            for matricula in matriculas_activas:
                try:
                    # Verificar si ya existe algún cronograma para esta matrícula
                    cronograma_existente = CronogramaPagos.objects.filter(
                        Matricula=matricula
                    ).exists()
                    
                    if cronograma_existente:
                        cronogramas_existentes += 1
                        continue
                    
                    # Generar cronograma para cada mes
                    for mes_numero in MESES_A_GENERAR:
                        CronogramaPagos.objects.create(
                            Matricula=matricula,
                            NumeroMes=mes_numero,
                            cobrar_pension=True,
                            monto=monto_valor,
                            observaciones=f'Generado automáticamente - {ano_activo.Ano}',
                            pagado=False
                        )
                    
                    cronogramas_generados += 1
                    
                except Exception as e:
                    errores.append(f"Matrícula {matricula.id} - {matricula.Alumno.NombreCompleto()}: {str(e)}")
            
            # Preparar mensaje de resultado
            mensaje = f"""
            <div class="alert alert-success">
                <h6><i class="bx bx-check-circle"></i> Proceso completado</h6>
                <strong>Total de matrículas activas en {ano_activo.Ano}:</strong> {total_matriculas}<br>
                <strong>Cronogramas generados:</strong> {cronogramas_generados}<br>
                <strong>Cronogramas existentes (no generados):</strong> {cronogramas_existentes}<br>
                <strong>Monto utilizado:</strong> S/ {monto_valor}
            </div>
            """
            
            if cronogramas_generados == 0 and cronogramas_existentes > 0:
                mensaje += f"""
                <div class="alert alert-info">
                    <i class="bx bx-info-circle"></i> 
                    Todos los alumnos ({cronogramas_existentes}) ya tienen cronogramas generados para el año {ano_activo.Ano}.
                </div>
                """
            
            if errores:
                mensaje += f"""
                <div class="alert alert-warning">
                    <h6><i class="bx bx-error"></i> Errores encontrados ({len(errores)}):</h6>
                    <ul class="mb-0">
                        {"".join([f"<li>{error}</li>" for error in errores[:5]])}
                    </ul>
                    {f'<small>... y {len(errores) - 5} errores más</small>' if len(errores) > 5 else ''}
                </div>
                """
            
            return JsonResponse({
                'success': True,
                'message': mensaje,
                'estadisticas': {
                    'total_matriculas': total_matriculas,
                    'generados': cronogramas_generados,
                    'existentes': cronogramas_existentes,
                    'errores': len(errores),
                    'ano_academico': str(ano_activo.Ano),
                    'monto_utilizado': float(monto_valor)
                }
            })
            
        except Exception as e:
            import traceback
            return JsonResponse({
                'success': False, 
                'error': f'Error general: {str(e)}',
                'traceback': traceback.format_exc()
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

class ConfiguracionesPagosView(TemplateView):
    """Vista principal de configuraciones de pagos"""
    template_name = 'pagos/configuraciones/configuraciones_main.html'

class MontoPensionListView(ListView):
    model = MontoPension
    template_name = 'pagos/configuraciones/montopension_list.html'
    context_object_name = 'montos'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = MontoPension.objects.all().select_related('AnoAcademico')
        
        # Filtrar por año académico si se especifica
        ano_academico = self.request.GET.get('ano_academico')
        if ano_academico:
            queryset = queryset.filter(AnoAcademico_id=ano_academico)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['anos_academicos'] = AnoAcademico.objects.all().order_by('-Ano')
        return context

class MontoPensionCreateView(CreateView):
    model = MontoPension
    template_name = 'pagos/configuraciones/montopension_form.html'
    fields = ['AnoAcademico', 'Monto', 'descripcion', 'activo']
    success_url = reverse_lazy('app_montopension_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Monto de pensión creado exitosamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nuevo Monto de Pensión'
        return context

class MontoPensionUpdateView(UpdateView):
    model = MontoPension
    template_name = 'pagos/configuraciones/montopension_form.html'
    fields = ['AnoAcademico', 'Monto', 'descripcion', 'activo']
    success_url = reverse_lazy('app_montopension_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Monto de pensión actualizado exitosamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Monto de Pensión'
        return context

class MontoPensionDeleteView(DeleteView):
    model = MontoPension
    template_name = 'pagos/configuraciones/montopension_confirm_delete.html'
    success_url = reverse_lazy('app_montopension_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Monto de pensión eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)

