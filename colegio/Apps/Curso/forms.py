from django import forms
from colegio.Apps.Curso.models import Curso

class CursoForm(forms.ModelForm):

	class Meta:
		model = Curso
		fields = [
		'CodCurso',
		'Nombre',
		'Tipo',
		'Orden',
		'Nivel',
		'Grados'
		]
		widgets = {
		'CodCurso':forms.TextInput(attrs = {'class':'form-control','size':'20'}),
		'Nombre':forms.TextInput(attrs = {'class':'form-control','size':'80'}),
		'Orden':forms.NumberInput(attrs = {'class':'form-control'}),
		'Nivel':forms.Select(attrs = {'class':'form-control'}),
		'Tipo':forms.Select(attrs={'class':'form-control'}),
		'Grados':forms.TextInput(attrs = {'class':'form-control'}),
		}
