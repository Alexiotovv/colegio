"""colegio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('colegio.Apps.Home.urls')),
    #path('', include('colegio.Apps.Login.urls')),
    path('', include('colegio.Apps.Alumno.urls')),
    path('', include('colegio.Apps.Docente.urls')),
    path('', include('colegio.Apps.DocenteCurso.urls')),
    path('', include('colegio.Apps.Curso.urls')),
    path('', include('colegio.Apps.AnoAcademico.urls')),
    path('', include('colegio.Apps.PeriodoAcademico.urls')),
    path('', include('colegio.Apps.Apoderado.urls')),
    path('', include('colegio.Apps.Matricula.urls')),
    path('', include('colegio.Apps.Notas.urls')),
    path('', include('colegio.Apps.Nivel.urls')),
    path('', include('colegio.Apps.Grado.urls')),
    path('', include('colegio.Apps.Seccion.urls')),
    path('', include('colegio.Apps.Usuario.urls')),
    path('', include('colegio.Apps.OtrasOpciones.urls')),
    path('', include('colegio.Apps.BuscarNotas.urls')),
    path('', include('colegio.Apps.AvanceNotas.urls')),
    path('', include('colegio.Apps.Competencias.urls')),
    path('', include('colegio.Apps.LibretaAvance.urls')),
    path('', include('colegio.Apps.Pagos.urls')),
    path('', include('colegio.Apps.Apis.urls')),
    path('', include('colegio.Apps.ServiciosExternos.urls')),
    path('', include('django.contrib.auth.urls')), #new
    path('', include('colegio.Apps.SituacionFinal.urls')),
]
