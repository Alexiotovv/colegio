from django.db import models
from colegio.Apps.Curso.models import Curso


class Competencias(models.Model):
    NIVEL=(('PRIM','PRIM'),('SEC','SEC'))
    nivel=models.CharField(max_length=10,choices=NIVEL,default='PRIM')
    nombre_competencia=models.CharField(max_length=250,default='')
    Orden=models.IntegerField(default=1)
    STATUS=((True,'HABILITADO'),(False,'INHABILITADO'))
    status=models.BooleanField(choices=STATUS,default=True)

    def Competencias(self):
        cadena = "{0}-{1}"
        return cadena.format(self.nivel,self.nombre_competencia)

    def __str__(self):
        return self.Competencias()

class CompetenciaCurso(models.Model):
    Competencias=models.ForeignKey(Competencias,null=False,blank=False,on_delete=models.CASCADE)
    Curso=models.ForeignKey(Curso,null=False,blank=False,on_delete=models.CASCADE)
