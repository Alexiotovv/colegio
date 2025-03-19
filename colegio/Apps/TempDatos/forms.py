from django import forms
from colegio.Apps.TempDatos.models import TempDatos

class TempDatosForm (forms.ModelForm):
	class Meta:
		model = TempDatos
		fields = [
		'idCurso',
		'grado',
		'seccion'
		]
		widgets = {
		'idCurso': forms.TextInput(attrs={'class':'form-control'}),
		'grado': forms.TextInput(attrs={'class':'form-control'}),
		'seccion': forms.TextInput(attrs={'class':'form-control'}),
		}