from django.urls import path
from .views import *

urlpatterns = [
    path("listar/matriculados/<anho>", ListarMatriculados, name="appListarMatriculados"),
    path("listar/meses-no-pago/<anho>", ListarAlumnosMesesNoPago, name="appListarMesesNoPago"),
    path("buscar/alumno/<dni>", BuscarAlumno, name="appBuscarAlumno"),
    path('api/ventas/registrar', RegistrarVenta, name='registrar_venta'),

]
