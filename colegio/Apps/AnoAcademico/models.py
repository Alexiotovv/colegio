from django.db import models
from datetime import date
class AnoAcademico (models.Model):
	Ano = models.CharField(max_length=4)
	FechaInicio = models.DateField()
	FechaFinal = models.DateField()
	activo = models.BooleanField(
        "Activo",
        default=False,
        help_text="Marque si este es el año académico actual"
    )
	
	def __str__(self):
		return self.Ano
