from django.urls import path, include
from colegio.Apps.Turno.views import ListarTurno
from django.contrib.auth.decorators import login_required

urlpatterns = [
path('turno/list/',login_required(ListarTurno),name='app_turno_list'),
]