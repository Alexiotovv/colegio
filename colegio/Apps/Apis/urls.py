from django.urls import path
from .views import *

urlpatterns = [
    path("listar/matriculados/<anho>", ListarMatriculados, name="appListarMatriculados"),
    path("buscar/alumno/<dni>", BuscarAlumno, name="appBuscarAlumno"),
    path('api/ventas/registrar', RegistrarVenta, name='registrar_venta'),

]
