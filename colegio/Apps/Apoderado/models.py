from django.db import models
from datetime import date
# Create your models here.
class Apoderado (models.Model):
	DNI = models.CharField(max_length=8, unique=True)
	Nombres = models.CharField(max_length=60)
	ApellidoPaterno = models.CharField(max_length=60)
	ApellidoMaterno = models.CharField(max_length=60)
	Direccion = models.CharField(max_length=100,default='')
	SEXOS =  (('M','Masculino'),('F','Femenino'))
	Sexo = models.CharField(max_length=1,choices=SEXOS,default='M')
	Telefono = models.CharField(max_length=60)
	Email = models.EmailField(max_length=60)
	