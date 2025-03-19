from django.urls import path, include
from django.views.generic.base import TemplateView # new
from colegio.Apps.Competencias.views import GrabarCompetencias,ListarCompetencias,EditarCompetencias,EliminarCompetencias,NuevaCompetencia#,EliminarCursoCompetencia
from django.contrib.auth.decorators import login_required

urlpatterns = [
	path('competencias/asignar_competencias/<curso_id>', login_required(GrabarCompetencias), name='app_grabar_asignacion_competencia'),
	path('competencias/editar_competencias/<id>', login_required(EditarCompetencias), name='app_editar_competencias'),
	path('competencias/nueva_competencia/', login_required(NuevaCompetencia), name='app_nueva_competencia'),
	path('competencias/eliminar_competencias/<id>', login_required(EliminarCompetencias), name='app_eliminar_competencias'),
	path('competencias/listar_competencias/', login_required(ListarCompetencias), name='app_listar_competencias'),
	
	#path('competencias/eliminar_cursocompetencias/<idcomcur>', login_required(EliminarCursoCompetencia()), name='app_eliminar_competencia_curso'),
]