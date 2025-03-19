from django.urls import path,include
from django.views.generic.base import TemplateView
from colegio.Apps.Nivel.views import NivelCreate,NivelList,NivelDelete,NivelUpdate
from django.contrib.auth.decorators import login_required

urlpatterns = [
	path('nivel/create/',login_required(NivelCreate.as_view()),name='app_create_nivel'),
	path('nivel/update/<pk>',login_required(NivelUpdate.as_view()), name='app_update_nivel'),
	path('nivel/delete/<pk>',login_required(NivelDelete.as_view()),name='app_delete_nivel'),
	path('nivel/list/',login_required(NivelList.as_view()),name='app_list_nivel'),

]
