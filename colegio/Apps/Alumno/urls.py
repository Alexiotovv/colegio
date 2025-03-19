from django.urls import path, include
from django.conf.urls import url
from django.views.generic.base import TemplateView # new
from colegio.Apps.Alumno.views import AlumnoList,AlumnoNew,AlumnoUpdate,AlumnoDelete,AlumnoDetalle,AlumnoListNoActivos
from django.contrib.auth.decorators import login_required

urlpatterns = [
path('alumnos/nuevo/', login_required(AlumnoNew.as_view()), name='app_alumno_nuevo'), 
path('alumnos/listar/', login_required(AlumnoList), name='app_alumno_listar'),
path('alumnos/listarnoactivos/', login_required(AlumnoListNoActivos), name='app_alumno_listar_noactivos'),
path('alumnos/editar/<pk>', login_required(AlumnoUpdate.as_view()), name='app_alumno_editar'),
path('alumnos/eliminar/<pk>', login_required(AlumnoDelete.as_view()), name='app_alumno_delete'),
path('alumnos/detalle/<pk>', login_required(AlumnoDetalle.as_view()), name='app_alumno_detalle'),
]

