from django import forms
from colegio.Apps.AvanceNotas.models import AvanceNotas,AvanceNotasComp

class AvanceNotasForm(forms.ModelForm):
	class Meta:
		model = AvanceNotas
		fields =[
		'Matricula',
		'Curso',
		'PAcademico',
		'Docente',
		'Nota',
		'SimulacroNota',
		]
		widgets = {
		'Matricula': forms.Select(attrs={'class':'single-select'}),
		'Curso': forms.Select(attrs={'class':'single-select'}),
		'PAcademico': forms.Select(attrs={'class':'single-select'}),
		'Docente': forms.TextInput(attrs={'class':'form-control'}),
		'Nota': forms.TextInput(attrs={'class':'form-control'}),
		'SimulacroNota': forms.TextInput(attrs={'class':'form-control'}),
		}
		
class AvanceNotasCompForm(forms.ModelForm):
	class Meta:
		model = AvanceNotasComp
		fields =[
		'Matricula',
		'Curso',
		'PAcademico',
		'Docente',
		'Competencias',
		'Nota',

		]
		widgets = {
		'Matricula': forms.Select(attrs={'class':'single-select'}),
		'Curso': forms.Select(attrs={'class':'single-select'}),
		'PAcademico': forms.Select(attrs={'class':'single-select'}),
		'Docente': forms.TextInput(attrs={'class':'form-control'}),
		'Competencias': forms.Select(attrs={'class':'single-select'}),
		'Nota': forms.TextInput(attrs={'class':'form-control'}),

		}
		
				