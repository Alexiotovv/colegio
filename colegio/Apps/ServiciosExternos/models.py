from django.db import models

class AccesosExternos(models.Model):
    nombre = models.CharField(max_length=255, unique=True)  # Nombre identificador del acceso
    url = models.URLField(max_length=500)  # URL de la API externa
    token = models.CharField(max_length=500)  # Token de autenticación

    def __str__(self):
        return self.nombre