from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView, UpdateView, ListView
from .models import *
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
import logging

logger = logging.getLogger(__name__)

redirect_authenticated_user = True

class RegistrationLoginView(LoginView):
    template_name = 'login.html'
    success_url = '/'

class RegistrationLogoutView(LogoutView):
    template_name = 'login.html'
    next_page = '/'

class Scanner(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'scan.html'

class CheckInView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = Tamu
    template_name = 'check_in_createview.html'
    fields = ['instansi', 'nama', 'meja', 'sudah_checkin']
    success_url = '../'

    def get_absolute_url(self):
        return reverse_lazy('checkin', kwargs={'slug':self.slug})

    def get_initial(self): #digunakan untuk memberikan nilai default di form    
        tamu = get_object_or_404(Tamu, slug=self.kwargs.get('slug'))
        #user = self.request.user.id
        return {
            'tamu':tamu,
        }
    
    def get_context_data(self, **kwargs): #digunakan untuk mengambil url dan mengirimkan nilainya ke template
        context = super().get_context_data(**kwargs)
        context['current_path'] = os.path.basename(self.request.get_full_path()) #digabung dengan fungsi os untuk mengambil url bagian terakhir saja
        context['path_without_query_string'] = self.request.path
        return context
    
class TamuListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Tamu
    template_name = 'tamu_listview.html'
    fields = '__all__'