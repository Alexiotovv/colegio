from django.db import models
from datetime import *
from colegio.Apps.Alumno.models import Alumno
from colegio.Apps.AnoAcademico.models import AnoAcademico
from django.utils import timezone

class Matricula (models.Model):    
    Alumno = models.ForeignKey(Alumno,null=False,blank=False,on_delete=models.PROTECT)
    AnoAcademico = models.ForeignKey(AnoAcademico,null=False,blank=False,on_delete=models.CASCADE)    
    GRADOS = (('1PRIM','1PRIM'),('2PRIM','2PRIM'),('3PRIM','3PRIM'),('4PRIM','4PRIM'),('5PRIM','5PRIM'),('6PRIM','6PRIM'),('1SEC','1SEC'),('2SEC','2SEC'),('3SEC','3SEC'),('4SEC','4SEC'),('5SEC','5SEC'))
    Grado = models.CharField(max_length=60, choices= GRADOS, default='--')
    SECCIONES = (('A','A'),('B','B'),('C','C'),('D','D'),('E','E'),('F','F'),('G','G'))
    Seccion = models.CharField(max_length=1, choices=SECCIONES, default='A')
    FechaMat = models.DateField(default=timezone.now)
    
    def Matricula(self):
        cadena = "{0} {1}, {2}"
        return cadena.format(self.Alumno,self.Grado,self.Seccion)

    def __str__(self):
    	return self.Matricula()