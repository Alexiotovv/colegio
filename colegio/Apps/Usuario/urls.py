from django.urls import path, include
from colegio.Apps.Usuario.views import UsuarioList, UsuarioView, RegistroUsuario,change_password
from django.contrib.auth.decorators import login_required

urlpatterns = [
	path('usuario/change_password/',login_required(change_password), name='app_usuario_change_password'),
	path('usuario/crear/',login_required(RegistroUsuario), name='app_usuario_create'),
	#path('usuario/update/<pk>',login_required(ActualizarForm), name='app_usuario_update'),
	path('usuario/listar/',login_required(UsuarioList.as_view()), name='app_usuario_listar'),
	path('usuario/detalle/<pk>',login_required(UsuarioView.as_view()), name='app_usuario_detalle'),
]