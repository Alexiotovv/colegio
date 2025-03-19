from django import forms
from colegio.Apps.Matricula.models import Matricula

class MatriculaForm(forms.ModelForm):

	class Meta:
		model = Matricula
		fields = [ 
		'Alumno',
    	'AnoAcademico',
	    'Grado',
    	'Seccion',
    	'FechaMat'
		]
		widgets = {
		'Alumno':forms.Select(attrs = {'class':'single-select'}),
    	'AnoAcademico':forms.Select(attrs = {'class':'single-select'}),
	    'Grado':forms.Select(attrs = {'class':'single-select'}),
    	'Seccion':forms.Select(attrs = {'class':'single-select'}),
    	'FechaMat':forms.DateInput(attrs = {'class':'form-control','type':'Date'}),
    	}
class ImportFile(forms.Form):
	file=forms.FileField()