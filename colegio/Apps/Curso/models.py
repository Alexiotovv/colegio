from pyexpat import model
from django.db import models
from datetime import date
# Create your models here.
class Curso (models.Model):
    CodCurso = models.CharField(max_length=20, unique=True)
    Orden=models.IntegerField(default=1)
    Nombre = models.CharField(max_length=80)
    TIPO = (('CURSO','CURSO'),('ACTITUDINAL','ACTITUDINAL'),('INASISTENCIAS','INASISTENCIAS'),('DEL PADRE DE FAMILIA','DEL PADRE DE FAMILIA'),('APRECIACIÓN DEL TUTOR','APRECIACIÓN DEL TUTOR'),('--','--'))
    Tipo=models.CharField(max_length=60,choices=TIPO,default='-')
    Grados = models.CharField(max_length=60, default='-')    
    NIVEL = (('PRIM','PRIM'),('SEC','SEC'))
    Nivel= models.CharField(max_length=60,choices=NIVEL, default='PRIM')
    
    def NombreCurso(self):
        cadena = "{0}-{1}-{2}"
        return cadena.format(self.Nivel,self.CodCurso,self.Nombre)
        
    def __str__(self):
        return self.NombreCurso()
