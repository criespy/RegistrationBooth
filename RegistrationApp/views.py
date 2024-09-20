from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

redirect_authenticated_user = True

class RegistrationLoginView(LoginView):
    template_name = 'login.html'

class RegistrationLogoutView(LogoutView):
    def logout_view(selfrequest):
        logout(request)
    template_name_= 'login.html'
    next_page = 'login'

class Scanner(TemplateView):
    template_name = 'scan.html'