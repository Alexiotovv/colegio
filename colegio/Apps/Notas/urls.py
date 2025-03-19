from django.urls import path, include
from django.conf.urls import url
from django.views.generic.base import TemplateView
from colegio.Apps.Notas.views import NotasNuevoComp, ListaNotas, NotasDelete,NotasEdit, \
    OpcionNotas,NotasNuevoSaveUno,DeleteNotasxCurso, NotasNuevoBimestre,NotasNuevoSaveBimestre,\
    NotasNuevoSaveComp,ConsolidadoNotas, ObtenerCompetencias,GuardaAvanceNotasPorAlumno,\
    ObtenerAvanceExistentes,ObtenerAvanceExistentesEditar,ObtenerCompetenciasEditar,\
    ActualizarAvanceNotasPorAlumno,RegistroPorAlumno,BuscarCursoNivel,RegistroBimNotasPorAula,\
    AlumnosBimPorAula,ObtenerCursosBimPorAula,ObtenerCompetenciasBimPorAula,GuardarNotaEditada,\
    profesor_ingreso_notas_bimestre,GuardarPromedioEditado,progreso_registro_notas_bimestre
from django.contrib.auth.decorators import login_required

urlpatterns = [
path('notas/profe_ingreso_notas_bim/<ano>/<pac>/<cur>/<grad>/<sec>',login_required(profesor_ingreso_notas_bimestre),name='app_nota_prof_ingreso_bim'),
path('notas/notas_nuevo_save_uno/',login_required(NotasNuevoSaveUno),name='app_nota_nuevo_save_uno'),
path('notas/notas_nuevo_bimestre/',login_required(NotasNuevoBimestre),name='app_nota_nuevo_bimestre'),
path('notas/notas_nuevo_save_bimestre/',login_required(NotasNuevoSaveBimestre),name='app_nota_nuevo_save_bimestre'),
path('notas/notas_nuevo_comp/',login_required(NotasNuevoComp),name='app_nota_nuevo_comp'),
path('notas/notas_nuevo_save/',login_required(NotasNuevoSaveComp),name='app_nota_nuevo_save_comp'),
path('notas/eliminar/<pk>',login_required(NotasDelete.as_view()),name='app_notas_delete'),
path('notas/editar/<id_notas>',login_required(NotasEdit),name='app_notas_edit'),
path('notas/listar/',login_required(ListaNotas),name='app_listar_notas'),
path('notas/opcion_notas/',login_required(OpcionNotas),name='app_opcion_notas'),
path('notas/eliminarxcurso/',login_required(DeleteNotasxCurso),name='app_delete_notasxcurso'),
path('otras_opciones/consolidado_libretas/',login_required(ConsolidadoNotas),name='app_consolidado_libretas'),
path('otras_opciones/consolidado_libretas/progreso/registro/notas/bim/<ano>/<bim>/<gradonivel>/<seccion>/',login_required(progreso_registro_notas_bimestre),name='app_progreso_registro_notas_bimestre'),


path('notas/registro_bim_por_alumno/',login_required(RegistroPorAlumno),name='app_registro_bim_por_alumno'),
path('notas/buscar_bim_cursos_nivel/<nivel>',login_required(BuscarCursoNivel),name='app_buscar_cursos_nivel'),
path('notas/obtener_bim_competencias/<idCurso>',login_required(ObtenerCompetencias),name='app_obtener_competencias'),
path('notas/guardar_bim_notas_por_alumno/',login_required(GuardaAvanceNotasPorAlumno),name='app_guardar_notas_por_alumno'),
path('notas/obtener_notas_existentes/',login_required(ObtenerAvanceExistentes),name='app_obtener_notas_existentes'),
path('notas/obtener_notas_existentes_editar_bim/',login_required(ObtenerAvanceExistentesEditar),name='app_obtener_notas_existentes_editar_bim'),
path('notas/obtener_bim_competencias_editare/',login_required(ObtenerCompetenciasEditar),name='app_obtener_bim_competencias_editar'),
path('notas/actualizar_notas_competencias/',login_required(ActualizarAvanceNotasPorAlumno),name='app_actualizar_avance_notasporalumno'),

path('notas/GuardarNotaEditada/<id>',login_required(GuardarNotaEditada),name='app.GuardarNotaEditada'),
path('notas/GuardarPromedioEditado/<id>',login_required(GuardarPromedioEditado),name='app.GuardarPromedioEditado'),

path('notas/RegistroBimNotasPorAula', login_required(RegistroBimNotasPorAula), name='Registro.BimNotasPorAula'),
path('notas/AlumnosBimPorAula', login_required(AlumnosBimPorAula), name='Alumnos.BimPorAula'),
path('notas/ObtenerCursosBimPorAula/<nivel>', login_required(ObtenerCursosBimPorAula), name='Obtener.CursosBimPorAula'),
path('notas/ObtenerCompetenciasBimPorAula/<id>', login_required(ObtenerCompetenciasBimPorAula), name='Obtener.CompetenciasBimPorAula'),

]
