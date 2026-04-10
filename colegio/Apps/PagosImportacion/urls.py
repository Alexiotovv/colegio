from django.urls import path
from colegio.Apps.PagosImportacion.views import *

app_name = 'PagosImportacion'

urlpatterns = [
    path('pagos/importar/', importar_excel, name='importar'),
    path('pagos/importaciones/', listar_importaciones, name='listar_importaciones'),
    path('pagos/importacion/<int:importacion_id>/', detalle_importacion, name='detalle_importacion'),
    path('pagos/limpiar/', limpiar_pagos, name='limpiar_pagos'),
    path('pagos/limpiar/<int:anio>/', limpiar_pagos, name='limpiar_pagos_anio'),
    path('pagos/buscar/', buscar_pagos, name='buscar_pagos'),
]