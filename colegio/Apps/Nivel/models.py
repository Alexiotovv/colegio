from django.db import models

class Nivel(models.Model):
	Nombre = models.CharField(max_length=60)
	
