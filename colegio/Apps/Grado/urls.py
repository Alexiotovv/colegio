from django.urls import path, include
from django.views.generic.base import TemplateView
from colegio.Apps.Grado.views import GradoList,GradoUpdate,GradoCreate,GradoDelete
from django.contrib.auth.decorators import login_required

urlpatterns = [
path('grado/create/',login_required(GradoCreate.as_view()),name='app_grado_create'),
path('grado/list/',login_required(GradoList.as_view()),name='app_grado_list'),
path('grado/delete/<pk>',login_required(GradoDelete.as_view()),name='app_grado_delete'),
path('grado/update/<pk>',login_required(GradoUpdate.as_view()),name='app_grado_update')
]