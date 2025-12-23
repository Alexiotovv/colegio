from django import forms
from .models import ArchivoSituacionFinal

class ArchivoSituacionFinalForm(forms.ModelForm):
    class Meta:
        model = ArchivoSituacionFinal
        fields = ['archivo']
        widgets = {
            'archivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.zip,.rar'
            })
        }