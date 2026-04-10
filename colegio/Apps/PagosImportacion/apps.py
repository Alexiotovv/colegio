from django.apps import AppConfig

class PagosimportacionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'PagosImportacion'  # Importante: debe coincidir con el nombre exacto de la carpeta
    verbose_name = 'Gestión de Pagos'