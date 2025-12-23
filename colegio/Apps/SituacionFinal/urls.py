from django.urls import path
from colegio.Apps.SituacionFinal.views import SubirArchivoView, ArchivoListView, procesar_archivo, SituacionFinalListView, eliminar_archivo


urlpatterns = [
    path('situacionfinal/subir/', SubirArchivoView.as_view(), name='subir_archivo'),
    path('situacionfinal/archivos/', ArchivoListView.as_view(), name='listar_archivos'),
    path('situacionfinal/procesar/<int:pk>/', procesar_archivo, name='procesar_archivo'),
    path('situacionfinal/situaciones/', SituacionFinalListView.as_view(), name='listar_situaciones'),
    path('situacionfinal/eliminar/<int:pk>/', eliminar_archivo, name='eliminar_situacion'), 
]