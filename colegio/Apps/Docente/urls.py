from django.urls import path, include
from django.views.generic.base import TemplateView
from colegio.Apps.Docente.views import DocenteUpdate, DocenteNew, DocenteList, DocenteDelete, DocenteDetalle
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('docentes/nuevo/<id_user>', login_required(DocenteNew), name='app_docente_nuevo'),
    path('docentes/listar/', login_required(DocenteList.as_view()), name='app_docente_listar'),
    path('docentes/editar/<id_docente>', login_required(DocenteUpdate), name='app_docente_editar'),
	path('docentes/eliminar/<pk>', login_required(DocenteDelete.as_view()), name='app_docente_delete'),
	path('docentes/detalle/<pk>', login_required(DocenteDetalle.as_view()), name='app_docente_detalle'),		
]