from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

#class ChangeForm(UserChangeForm):
#	class ClassMeta:
#		model = User

class RegistroForm(UserCreationForm):
	class Meta:
		model = User
		fields = [
			'username',
			'first_name',
			'last_name',
			'email',
			'is_active',
			'is_staff',
			'is_superuser',
			'groups',
		]
		widgets = {
			'username':forms.TextInput(attrs = {'class':'form-control'}),
			'first_name':forms.TextInput(attrs = {'class':'form-control'}),
			'last_name':forms.TextInput(attrs={'class':'form-control'}),
			'email':forms.EmailInput(attrs = {'class':'form-control'}),
			'groups':forms.SelectMultiple(attrs = {'class':'form-control','name':'old_group','id':'sel1'}),
		}