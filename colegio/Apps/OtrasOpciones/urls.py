from django.urls import path, include
from django.conf.urls import url
from django.views.generic.base import TemplateView # new
from colegio.Apps.OtrasOpciones.views import ImprimirLibretas,ImprimirAvances,ImprimirConsolidadoLibretas,\
 ResumenAnual,ImprimirConsolidadoAvances,ImprimirResumenAnual
from django.contrib.auth.decorators import login_required

urlpatterns = [
# path('otrasopciones/consolidado_avances/', login_required(ConsolidadoAvances), name='app_consolidado_avances'),
# path('otrasopciones/consolidado_libretas/', login_required(ConsolidadoLibretas), name='app_consolidado_libretas'),
path('otrasopciones/resumen_anual/', login_required(ResumenAnual), name='app_resumen_anual'),
path('otrasopciones/imprimir_resumen_anual/', login_required(ImprimirResumenAnual), name='app_imprimir_resumen_anual'),

##################Se está habilitando para ejecutar la impresion de avance de notas
path('otrasopciones/imprimir_consolidado_avances/', login_required(ImprimirConsolidadoAvances), name='app_imprimir_consolidado_avances'),
#################

path('otrasopciones/imprimir_consolidado_libretas/', login_required(ImprimirConsolidadoLibretas), name='app_imprimir_consolidado_libretas'),
path('otrasopciones/libretas/', login_required(ImprimirLibretas), name='app_imprimir_libretas'),
path('otrasopciones/avances/', login_required(ImprimirAvances), name='app_imprimir_avances'),
# path('otrasopciones/imprimir/',login_required(OpcionImprimir), name='app_opcion_imprimir'),
]

