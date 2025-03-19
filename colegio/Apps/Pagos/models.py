from django.db import models
from colegio.Apps.Matricula.models import Matricula
# Create your models here.

class Pagos(models.Model):
	# Matricula = models.ForeignKey(Matricula,null=False,blank=False,on_delete=models.CASCADE)
	Dni = models.CharField(max_length=10,default='-')
	PagoMes = models.CharField(max_length=20,default='-')
	PagoAno = models.CharField(max_length=4,default='-')