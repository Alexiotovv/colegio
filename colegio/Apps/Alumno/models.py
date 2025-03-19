from django.db import models
from datetime import date
# Create your models here.
class Alumno (models.Model):
    
    ApellidoPaterno = models.CharField(max_length=60)
    ApellidoMaterno = models.CharField(max_length=60,default='-')
    Nombres = models.CharField(max_length=60)
    Direccion = models.CharField(max_length=100,default='-')
    DNI = models.CharField(max_length=8, unique=True, default='-')
    FechaNacimiento = models.DateField()
    SEXOS =  (('M','Masculino'),('F','Femenino'))
    Sexo = models.CharField(max_length=1,choices=SEXOS,default='M')
    ESTADOS = (('A','Activo'),('R','Retirado'),('E','Egresado'))
    Estado = models.CharField(max_length=1,choices=ESTADOS,default='A')
    def NombreCompleto(self):
    	cadena = "{0} {1}, {2}"
    	return cadena.format (self.ApellidoPaterno,self.ApellidoMaterno,self.Nombres)

    def __str__(self):
    	return self.NombreCompleto()