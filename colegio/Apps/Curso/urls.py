from django.urls import path, include
from django.views.generic.base import TemplateView
from colegio.Apps.Curso.views import EditarCurso, NuevoCurso, CursoList, CursoDelete, CursoDetalle
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('cursos/nuevo/', login_required(NuevoCurso), name='app_curso_nuevo'),
    path('cursos/editar/<id_curso>', login_required(EditarCurso), name='app_curso_editar'),
    path('cursos/listar/', login_required(CursoList.as_view()), name='app_curso_listar'),    
	path('cursos/eliminar/<pk>', login_required(CursoDelete.as_view()), name='app_curso_delete'),
	path('cursos/detalle/<pk>', login_required(CursoDetalle.as_view()), name='app_curso_detalle'),		
]