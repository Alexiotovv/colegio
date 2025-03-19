from django.urls import path, include
from django.views.generic.base import TemplateView
from colegio.Apps.Seccion.views import SeccionList,SeccionUpdate,SeccionCreate,SeccionDelete
from django.contrib.auth.decorators import login_required

urlpatterns = [
path('seccion/create/',login_required(SeccionCreate.as_view()),name='app_seccion_create'),
path('seccion/list/',login_required(SeccionList.as_view()),name='app_seccion_list'),
path('seccion/delete/<pk>',login_required(SeccionDelete.as_view()),name='app_seccion_delete'),
path('seccion/update/<pk>',login_required(SeccionUpdate.as_view()),name='app_seccion_update')
]