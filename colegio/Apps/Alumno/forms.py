from django import forms
from colegio.Apps.Alumno.models import Alumno

class AlumnoForm(forms.ModelForm):

	class Meta:
		model = Alumno
		fields = [
		'DNI',
		'Nombres',
		'ApellidoPaterno',
		'ApellidoMaterno',
		'Direccion',
		'FechaNacimiento',
		'Sexo',
		'Estado'
		]
		
		widgets = {
		'DNI':forms.NumberInput(attrs = {'class':'form-control','size':'8'}),
		'Nombres':forms.TextInput(attrs = {'class':'form-control'}),
		'ApellidoPaterno':forms.TextInput(attrs = {'class':'form-control'}),
		'ApellidoMaterno':forms.TextInput(attrs = {'class':'form-control'}),
		'Direccion':forms.TextInput(attrs = {'class':'form-control'}),
		'FechaNacimiento':forms.DateInput(attrs = {'class':'form-control', 'type':'Date'}),
		'Sexo':forms.Select(attrs = {'class':'single-select'}),
		'Estado':forms.Select(attrs = {'class':'single-select'}),
}
