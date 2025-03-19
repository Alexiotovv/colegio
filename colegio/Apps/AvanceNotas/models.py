from django.db import models
from datetime import date
from colegio.Apps.Competencias.models import Competencias
from colegio.Apps.Curso.models import Curso
from colegio.Apps.AnoAcademico.models import AnoAcademico
from colegio.Apps.Docente.models import Docente
from colegio.Apps.PeriodoAcademico.models import PAcademico
from colegio.Apps.Matricula.models import Matricula
from colegio.Apps.Competencias.models import Competencias

class AvanceNotas(models.Model):
	Curso = models.ForeignKey(Curso,null=False,blank=False,on_delete=models.CASCADE)
	Matricula = models.ForeignKey(Matricula,null=False,blank=False,on_delete=models.CASCADE)
	PAcademico = models.ForeignKey(PAcademico,null=False,blank=False,on_delete=models.CASCADE)
	Docente = models.ForeignKey(Docente,null=False,blank=False,on_delete=models.CASCADE)#user name
	Nota = models.CharField(max_length=100,default='-')
	SimulacroNota = models.CharField(max_length=100,default='-')

class AvanceNotasComp(models.Model):
	Curso = models.ForeignKey(Curso,null=False,blank=False,on_delete=models.CASCADE)
	Competencias = models.ForeignKey(Competencias,null=False,blank=False,on_delete=models.CASCADE)
	Matricula = models.ForeignKey(Matricula,null=False,blank=False,on_delete=models.CASCADE)
	PAcademico = models.ForeignKey(PAcademico,null=False,blank=False,on_delete=models.CASCADE)
	Docente = models.ForeignKey(Docente,null=False,blank=False,on_delete=models.CASCADE)#user name
	Nota = models.CharField(max_length=100,default='-')

