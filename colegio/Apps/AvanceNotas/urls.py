from django.urls import path, include
from django.conf.urls import url
from django.views.generic.base import TemplateView
from colegio.Apps.AvanceNotas.views import (AvanceNotasDelete,AvanceListaNotas,AvanceNotasNuevo,
AvanceNotasNuevoSave,AvanceNotasEdit,AvanceNotasNuevoUno, ConsolidadoAvances,DeleteAvanceNotasxCurso,AvanceNotasNuevoComp,
AvanceNotasNuevoSaveComp,RegistroPorAlumno,BuscarCursoNivel,ObtenerCompetencias,GuardaAvanceNotasPorAlumno,
ObtenerAvanceExistentes,ObtenerAvanceExistentesEditar,ObtenerCompetenciasEditar,ActualizarAvanceNotasPorAlumno,
profesor_ingreso_notas_avance)
from django.contrib.auth.decorators import login_required

urlpatterns = [
path('avancenotas/profe_ingreso_notas_avan/<ano>/<pac>/<cur>/<grad>/<sec>',login_required(profesor_ingreso_notas_avance),name='app_nota_prof_ingreso_avan'),

path('notas/avancenotas_nuevo_uno/',login_required(AvanceNotasNuevoUno),name='app_avancenota_nuevo_uno'),
path('notas/avancenotas_nuevo/',login_required(AvanceNotasNuevo),name='app_avancenota_nuevo'),
path('notas/avancenotas_nuevo_comp/',login_required(AvanceNotasNuevoComp),name='app_avancenota_nuevo_comp'),
path('notas/avancenotas_nuevo_save/',login_required(AvanceNotasNuevoSave),name='app_avancenota_nuevo_save'),
path('notas/avancenotas_nuevo_save_comp/',login_required(AvanceNotasNuevoSaveComp),name='app_avancenota_nuevo_save_comp'),
path('avancenotas/eliminar/<pk>',login_required(AvanceNotasDelete.as_view()),name='app_notas_avancedelete'),
path('avancenotas/editar/<id_notas>',login_required(AvanceNotasEdit),name='app_avancenotas_edit'),
path('avancenotas/listar/',login_required(AvanceListaNotas),name='app_listar_avancenotas'),
path('avancenotas/eliminaravancexcurso/',login_required(DeleteAvanceNotasxCurso),name='app_delete_avancenotasxcurso'),

path('otras_opciones/consolidado_avances/',login_required(ConsolidadoAvances),name='app_consolidado_avances'),

path('avancenotas/registro_por_alumno/',login_required(RegistroPorAlumno),name='app_registro_por_alumno'),
path('avancenotas/buscar_cursos_nivel/<nivel>',login_required(BuscarCursoNivel),name='app_buscar_cursos_nivel'),
path('avancenotas/obtener_competencias/<idCurso>',login_required(ObtenerCompetencias),name='app_obtener_competencias'),
path('avancenotas/guardar_notas_por_alumno/',login_required(GuardaAvanceNotasPorAlumno),name='app_guardar_notas_por_alumno'),
path('avancenotas/obtener_avancenotas_existentes/',login_required(ObtenerAvanceExistentes),name='app_obtener_notas_existentes'),
path('avancenotas/obtener_avancenotas_existentes_editar/',login_required(ObtenerAvanceExistentesEditar),name='app_obtener_notas_existentes_editar'),
path('avancenotas/obtener_competencias_editare/',login_required(ObtenerCompetenciasEditar),name='app_obtener_competencias_editar'),
path('avancenotas/actualizar_avancenotas_competencias/',login_required(ActualizarAvanceNotasPorAlumno),name='app_actualizar_avance_notasporalumno'),

]
