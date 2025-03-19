from django import forms
from colegio.Apps.AnoAcademico.models import AnoAcademico

class AnoAcademicoForm (forms.ModelForm):
	class Meta:
		model = AnoAcademico
		fields = [
		'Ano',
		'FechaInicio',
		'FechaFinal'
		]
		widgets = {
		'Ano':forms.TextInput(attrs={'class':'form-control'}),
		'FechaInicio':forms.DateInput(attrs={'class':'form-control','type':'Date'}),
		'FechaFinal':forms.DateInput(attrs={'class':'form-control','type':'Date'}),
		}
