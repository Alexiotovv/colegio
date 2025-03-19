from django.urls import path, include
from django.views.generic.base import TemplateView
from colegio.Apps.DocenteCurso.views import DocenteCursoCreate, DocenteCursoDelete,DocenteCursoUpdate,DocenteListarAsginaciones
from django.contrib.auth.decorators import login_required

urlpatterns = [
	path('docentecurso/create/<id_docente>',login_required(DocenteCursoCreate),name='app_docentecurso_create'),
	path('docentecurso/delete/<pk>',login_required(DocenteCursoDelete.as_view()),name='app_docentecurso_delete'),
	path('docentecurso/update/<pk>',login_required(DocenteCursoUpdate.as_view()),name='app_docentecurso_update'),
	path('docentecurso/listar_asginaciones/',login_required(DocenteListarAsginaciones),name='app_docente_listar_asignaciones'),
]