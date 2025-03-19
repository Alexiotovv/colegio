from django import forms
from colegio.Apps.Competencias.models import Competencias,CompetenciaCurso

class CompetenciasForm(forms.ModelForm):
	class Meta:
		model = Competencias
		fields = [
		'nivel',
		'nombre_competencia',
		'Orden',
		'status'
		]
		widgets = {
		'nivel':forms.Select(attrs = {'class':'single-select'}),
		'nombre_competencia':forms.TextInput(attrs = {'class':'form-control'}),
		'Orden':forms.NumberInput(attrs = {'class':'form-control'}),
  		'status':forms.Select(attrs = {'class':'form-select'}),
		}

# class CompetenciaCursoForm(forms.ModelForm):
# 	class Meta:
# 		model = CompetenciaCurso
# 		fields = [
# 		'Curso',
# 		'Competencias',
# 		]
# 		widgets = {
# 		'Curso':forms.Select(attrs = {'class':'form-control'}),
# 		'Competencias':forms.Select(attrs = {'class':'form-control'}),
# 		}
