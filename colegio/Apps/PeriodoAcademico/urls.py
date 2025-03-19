from django.urls import path, include
from django.views.generic.base import TemplateView
from colegio.Apps.PeriodoAcademico.views import PAcademicoUpdate, PAcademicoNew, PAcademicoList, PAcademicoDelete, PAcademicoDetalle
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('pacademico/nuevo/', login_required(PAcademicoNew), name='app_pacademico_nuevo'),
    path('pacademico/listar/', login_required(PAcademicoList.as_view()), name='app_pacademico_listar'),
    path('pacademico/editar/<id_paca>', login_required(PAcademicoUpdate), name='app_pacademico_editar'),
	path('pacademico/eliminar/<pk>', login_required(PAcademicoDelete.as_view()), name='app_pacademico_delete'),
	path('pacademico/detalle/<pk>', login_required(PAcademicoDetalle.as_view()), name='app_pacademico_detalle'),		
]