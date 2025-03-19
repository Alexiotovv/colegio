from django.urls import path, include
from colegio.Apps.Login.views import Login
from django.conf.urls import url

from django.contrib.auth.views import logout, login, password_reset, password_reset_done, password_reset_confirm, password_reset_complete

urlpatterns = [
	path('', Login),
    path('', logout, kwargs='next_page':'/',name="salir"),
    path('login/password_reset',password_reset,
        {'template_name':'registration/password_reset_form.html',
        'email_template':'registration/password_reset_email.html'},
        name="app_password_reset_form"),

    path('login/password_reset_done',password_reset_done,
        {'template_name':'registration/password_reset_done.html'},
     	name="app_password_reset_done"),
     path('login/<uidb64>',password_reset_confirm,
     	{'template_name':'registration/password_reset_confirm.html'},
     	name="app_password_reset_confirm"),
     path('login/done',password_reset_complete,
     	{'template_name':'registration/password_reset_complete.html'},
     	name="app_password_reset_complete"),
 ]
