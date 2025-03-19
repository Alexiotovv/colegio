from django.urls import path
from .views import *

urlpatterns = [
    path("listar/matriculados/<anho>", ListarMatriculados, name="appListarMatriculados")
]
