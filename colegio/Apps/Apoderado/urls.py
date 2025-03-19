from django.urls import path, include
from django.conf.urls import url
from django.views.generic.base import TemplateView # new
from colegio.Apps.Apoderado.views import ApoderadoList,ApoderadoNew,ApoderadoUpdate,ApoderadoDelete,ApoderadoDetalle
from django.contrib.auth.decorators import login_required

urlpatterns = [
path('apoderados/nuevo/', login_required(ApoderadoNew.as_view()), name='app_apoderado_nuevo'), 
path('apoderados/listar/', login_required(ApoderadoList.as_view()), name='app_apoderado_listar'),
path('apoderados/editar/<pk>', login_required(ApoderadoUpdate.as_view()), name='app_apoderado_editar'),
path('apoderados/eliminar/<pk>', login_required(ApoderadoDelete.as_view()), name='app_apoderado_delete'),
path('apoderados/detalle/<pk>', login_required(ApoderadoDetalle.as_view()), name='app_apoderado_detalle'),
]

