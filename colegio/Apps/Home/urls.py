from django.urls import path, include
from colegio.Apps.Home.views import index
from django.contrib.auth.decorators import login_required

urlpatterns = [
	path('',login_required(index)),
]