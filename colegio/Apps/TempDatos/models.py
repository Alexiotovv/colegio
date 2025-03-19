from django.db import models
from django.contrib.auth.models import User

class TempDatos(models.Model):
	User = models.OneToOneField(User, on_delete=models.CASCADE)
	idCurso=models.CharField(max_length=10,default='-')
	grado=models.CharField(max_length=10,default='-')
	seccion=models.CharField(max_length=1,default='-')
	idPAcademico=models.CharField(max_length=10,default='-')
	
	