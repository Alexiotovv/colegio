from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

def Login(request):
	return render(request, 'registration/login.html')


			