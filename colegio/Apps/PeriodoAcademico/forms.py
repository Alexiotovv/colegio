from django import forms
from colegio.Apps.PeriodoAcademico.models import PAcademico

class PAcademicoForm (forms.ModelForm):
	class Meta:
		model = PAcademico

		fields = [
		'Nombre',
		'FechaInicio',
		'FechaFinal',
		'Status'
		]
		widgets = {
		'Nombre': forms.TextInput(attrs={'class':'form-control'}),
		'FechaInicio': forms.DateInput(attrs={'class':'form-control','type':'date'}),
		'FechaFinal': forms.DateInput(attrs={'class':'form-control','type':'date'}),
		'Status':forms.Select(attrs = {'class':'single-select'}),
		}