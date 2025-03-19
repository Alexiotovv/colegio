from django.urls import path
from colegio.Apps.Pagos.views import RegistrarPago
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('pagos/registrar_pago/',login_required(RegistrarPago),name='app_registrar_pago'),
]