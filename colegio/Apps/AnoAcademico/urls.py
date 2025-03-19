from django.urls import path, include
from django.views.generic.base import TemplateView
from colegio.Apps.AnoAcademico.views import AnoAcademicoUpdate, AnoAcademicoNew, AnoAcademicoList, AnoAcademicoDelete, AnoAcademicoDetalle
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('academico/nuevo/', login_required(AnoAcademicoNew), name='app_academico_nuevo'),
    path('academico/listar/', login_required(AnoAcademicoList.as_view()), name='app_academico_listar'),
    path('academico/editar/<pk>', login_required(AnoAcademicoUpdate.as_view()), name='app_academico_editar'),
	path('academico/eliminar/<pk>', login_required(AnoAcademicoDelete.as_view()), name='app_academico_delete'),
	path('academico/detalle/<pk>', login_required(AnoAcademicoDetalle.as_view()), name='app_academico_detalle'),		
]