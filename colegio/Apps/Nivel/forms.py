from django import forms
from colegio.Apps.Nivel.models import Nivel

class NivelForm(forms.ModelForm):
	class Meta:
		model = Nivel
		fields = [
		'Nombre'
		]
		widgets = {
		'Nombre':forms.TextInput(attrs={'class':'form-control'}),
		} 
		
		