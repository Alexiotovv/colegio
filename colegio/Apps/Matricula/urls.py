from django.urls import path, include
from django.conf.urls import url
from django.views.generic.base import TemplateView
from colegio.Apps.Matricula.views import MatriculaNew, MatriculaList, MatriculaNewEvent, MatriculaDelete,MatriculaDetalle, MatriculaUpdate,PasarTodosNuevoAno, PlantillaMatriculados, ImportarArchivo,NewMatriculaAlumno, VerificarDni, MatriculaPorNiveles,ListarMatriculaPorNiveles,NuevaMatricula,GuardaNuevaMatricula,MatriculaPrincipal
from django.contrib.auth.decorators import login_required

urlpatterns = [
path('matricula/importar_matriculas/',login_required(ImportarArchivo),name='app_importar_archivo'),
path('matricula/plantilla_matriculados/',login_required(PlantillaMatriculados),name='app_plantilla_matriculados'),
path('matricula/pasartodosnuevoano/',login_required(PasarTodosNuevoAno),name='app_pasar_todos_nuevo_ano'),
path('matricula/nuevo/',login_required(MatriculaNew.as_view()),name='app_matricula_nuevo'),
path('matricula/newmatriculaalumno/',login_required(NewMatriculaAlumno),name='app_new_matricula_alumno'),
path('matricula/listar/',login_required(MatriculaList),name='app_matricula_listar'),
path('matricula/editar/<pk>',login_required(MatriculaUpdate.as_view()),name='app_matricula_editar'),
path('matricula/eliminar/<id>',login_required(MatriculaDelete),name='app_matricula_delete'),
path('matricula/detalle/<pk>',login_required(MatriculaDetalle.as_view()),name='app_matricula_detalle'),
path('matricula/event/<id_alumno>',login_required(MatriculaNewEvent),name='app_matricula_event'),
path('matricula/verificardni/',login_required(VerificarDni),name='app_verificar_dni'),
path('matricula/matriculaporniveles/',login_required(MatriculaPorNiveles),name='app_matricula_niveles'),
path('matricula/listarmatriculaporniveles/',login_required(ListarMatriculaPorNiveles),name='app_listar_matricula_niveles'),


path('matricula/matriculaprincipal/',login_required(MatriculaPrincipal),name='app_matricula_principal'),
path('matricula/nuevamatricula/',login_required(NuevaMatricula),name='app_solo_nueva_matricula'),
path('matricula/guardanuevamatricula/',login_required(GuardaNuevaMatricula),name='app_nueva_matricula'),
]