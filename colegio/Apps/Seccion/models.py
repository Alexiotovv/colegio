from django.db import models

class Seccion(models.Model):
	Nombre = models.CharField(max_length=2)
	
	def __str__(self):
		return self.Nombre	