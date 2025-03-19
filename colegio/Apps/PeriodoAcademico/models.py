from django.db import models
from datetime import date

class PAcademico (models.Model):
	Nombre = models.CharField(max_length=60)
	FechaInicio = models.DateField()
	FechaFinal = models.DateField()
	STATUS =  (('Activo','Activo'),('Inactivo','Inactivo'))
	Status = models.CharField(max_length=8,choices=STATUS,default='Inactivo')
	def NombrePA(self):
		cadena = "{0}"
		return cadena.format(self.Nombre)
	def __str__ (self):
		return self.NombrePA()