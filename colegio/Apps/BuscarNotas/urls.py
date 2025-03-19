from django.urls import path, include
from django.conf.urls import url
from django.views.generic.base import TemplateView # new
from colegio.Apps.BuscarNotas.views import BuscarNotas,BuscarAvanceNotas#,BuscarAvanceNotasComp
from django.contrib.auth.decorators import login_required

urlpatterns = [
path('notas/buscar/', login_required(BuscarNotas), name='app_buscar_notas'), 
path('avancenotas/buscar/', login_required(BuscarAvanceNotas), name='app_buscar_avancenotas'), 
]

