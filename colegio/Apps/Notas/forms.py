from django import forms
from colegio.Apps.Notas.models import NotasComp

class NotasForm(forms.ModelForm):
	class Meta:
		model = NotasComp
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
		
		