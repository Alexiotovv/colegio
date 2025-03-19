from django import forms
from colegio.Apps.Grado.models import Grado

class GradoForm(forms.ModelForm):
	class Meta:
		model = Grado
		fields = [
		'Nombre'
		]
		widgets = {
		'Nombre':forms.TextInput(attrs={'class':'form-control'}),
		}
