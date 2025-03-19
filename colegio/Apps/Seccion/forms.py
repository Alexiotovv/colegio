from django import forms
from colegio.Apps.Seccion.models import Seccion

class SeccionForm(forms.ModelForm):
	class Meta:
		model=Seccion
		fields=[
		'Nombre',
		]
		widgets={
		'Nombre':forms.TextInput(attrs={'class':'form-control'}),
		}
		