from django.db import models

class Grado(models.Model):
	Nombre=models.CharField(max_length=20)

	def __str__(self):
		return self.Nombre
	