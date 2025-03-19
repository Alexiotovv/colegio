from django import forms
from colegio.Apps.Apoderado.models import Apoderado

class ApoderadoForm(forms.ModelForm):

	class Meta:
		model = Apoderado
		fields = [
		'DNI',
		'Nombres',
		'ApellidoPaterno',
		'ApellidoMaterno',
		'Direccion',
		'Sexo',
		'Telefono',
		'Email'
		]
		widgets = {
		'DNI':forms.NumberInput(attrs = {'class':'form-control','size':'8'}),
		'Nombres':forms.TextInput(attrs = {'class':'form-control'}),
		'ApellidoPaterno':forms.TextInput(attrs = {'class':'form-control'}),
		'ApellidoMaterno':forms.TextInput(attrs = {'class':'form-control'}),
		'Direccion':forms.TextInput(attrs = {'class':'form-control'}),
		'Sexo':forms.Select(attrs = {'class':'form-control'}),
		'Telefono':forms.TextInput(attrs = {'class':'form-control'}),
		'Email':forms.EmailInput(attrs = {'class':'form-control'}),
		}
