from django.db import models
from django.contrib.auth.models import User

class AvanceTempDatos(models.Model):
	User = models.OneToOneField(User, on_delete=models.CASCADE)
	idCurso = models.CharField(max_length=10,default='-')
	grado = models.CharField(max_length=10,default='-')
	seccion = models.CharField(max_length=1,default='-')
	
class AvanceTempDatosComp(models.Model):
	User = models.OneToOneField(User, on_delete=models.CASCADE)
	idCurso = models.CharField(max_length=10,default=1)
	grado = models.CharField(max_length=10,default='')
	seccion = models.CharField(max_length=1,default='')
	