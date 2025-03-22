from django.urls import path
from .views import *

urlpatterns = [
    path("whatsapp/justificaciones/", ListarJustificaciones, name="appWhatsappJustificaciones"),
    path("index/justificaciones/", IndexJustificaciones, name="appIndexJustificaciones"),
    
]
