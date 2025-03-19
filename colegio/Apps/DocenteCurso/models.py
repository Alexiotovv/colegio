from django.db import models
from colegio.Apps.Docente.models import Docente
from colegio.Apps.Curso.models import Curso
class DocenteCurso(models.Model):
	Docente = models.ForeignKey(Docente,null=False,blank=False,on_delete=models.CASCADE)
	Curso = models.ForeignKey(Curso,null=False,blank=False,on_delete=models.CASCADE)
	
	def DocenteyCurso(self):
		cadena = "{0} {1} {2}"
		return cadena.format(self.Docente.User.first_name,self.Docente.User.last_name,self.Curso.Nombre)

	def __str__ (self):
		return self.DocenteyCurso()