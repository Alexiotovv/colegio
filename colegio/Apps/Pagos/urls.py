from django.urls import path
from colegio.Apps.Pagos.views import RegistrarPago, ListarPagos, \
     RegistrarCronograma, GestionarCronogramaView, GetCronogramaAlumno, \
     BuscarMatriculasAlumno ,ConfiguracionesPagosView,MontoPensionListView, \
     MontoPensionCreateView, MontoPensionUpdateView, MontoPensionDeleteView,GenerarCronogramasMasivos

from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('pagos/registrar_pago/',login_required(RegistrarPago),name='app_registrar_pago'),
    path('pagos/', login_required(ListarPagos), name='applistar_pagos'),
    
    #Cronogramas
    path('pagos/gestionar_cronograma/', login_required(GestionarCronogramaView), name='app_gestionar_cronograma'),
    path('pagos/registrar_cronograma/', login_required(RegistrarCronograma), name='app_registrar_cronograma'),
    path('pagos/get-cronograma/<int:matricula_id>/', login_required(GetCronogramaAlumno), name='app_get_cronograma'),
    path('pagos/buscar-matriculas/<int:alumno_id>/', login_required(BuscarMatriculasAlumno), name='app_buscar_matriculas'),
path('pagos/generar-cronogramas-masivos/', login_required(GenerarCronogramasMasivos), name='app_generar_cronogramas_masivos'),
    #MontoPensionenseñanza
    # Configuraciones de Pagos
    path('pagos/configuraciones/', login_required(ConfiguracionesPagosView.as_view()), 
         name='app_configuraciones_pagos'),
    path('pagos/configuraciones/montos/', login_required(MontoPensionListView.as_view()), 
         name='app_montopension_list'),
    path('pagos/configuraciones/montos/nuevo/', login_required(MontoPensionCreateView.as_view()), 
         name='app_montopension_create'),
    path('pagos/configuraciones/montos/editar/<int:pk>/', login_required(MontoPensionUpdateView.as_view()), 
         name='app_montopension_edit'),
    path('pagos/configuraciones/montos/eliminar/<int:pk>/', login_required(MontoPensionDeleteView.as_view()), 
         name='app_montopension_delete'),

]