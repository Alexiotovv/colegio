from django import forms
from colegio.Apps.Docente.models import Docente

class DocenteForm(forms.ModelForm):

	class Meta:
		model = Docente
		fields = [
		'DNI',
		'GradoNivel',
		'Seccion',
		'Direccion',
		'FechaNacimiento',
		'Sexo',
		'Telefono',
		'TutorGrado',
		'TutorSeccion',
		]
		widgets = {
		'DNI':forms.NumberInput(attrs = {'class':'form-control','size':'8'}),
		'GradoNivel':forms.TextInput(attrs = {'class':'form-control'}),
		'Seccion':forms.TextInput(attrs = {'class':'form-control'}),
		'Direccion':forms.TextInput(attrs = {'class':'form-control'}),
		'FechaNacimiento':forms.DateInput(attrs = {'class':'form-control', 'type':'Date'}),
		'Sexo':forms.Select(attrs = {'class':'form-control'}),
		'Telefono':forms.TextInput(attrs = {'class':'form-control'}),
		'TutorGrado':forms.Select(attrs = {'class':'form-control'}),
		'TutorSeccion':forms.Select(attrs = {'class':'form-control'}),
}
